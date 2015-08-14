#!/usr/bin/env python2
import codecs
import re
import os.path
import subprocess
import operator


ALPHABET = [chr(ord('a') + i) for i in xrange(ord('z') - ord('a') + 1)] + [chr(ord('A') + i) for i in xrange(ord('Z') - ord('A') + 1)]

# TODO: should we accept non-alphabet tokens?
def tokenize(s):
    #def is_word(x):
    #    return len(x) and x[0] in ALPHABET
    #def convert(x):
    #    return re.sub('[^a-zA-Z]', '', x).lower()
    #return filter(is_word, map(convert, re.findall(r"[\w'.]+", s)))
    return re.findall(r"[\w']+", s.lower(), re.UNICODE)


class Word(object):
    def __init__(self, word):
        self.word = word
        self.al = set()

    def __repr__(self):
        return "%s { %s }" % (self.word.encode('utf-8'), ' '.join(str(x+1) for x in self.al))


class PhraseTable(object):
    def __init__(self, source_language_corpus_path, target_language_corpus_path, alignment_folder, word_output, phrase_output, max_tokens, verbose=True):
        # Print to log if needed
        if verbose:
            def info(s):
                print s
        else:
            def info(s):
                pass

        self.info = info
        self.source_language_corpus_path = source_language_corpus_path
        self.target_language_corpus_path = target_language_corpus_path
        self.max_tokens = max_tokens
        self.alignment_folder = alignment_folder
        self.word_output = word_output
        self.phrase_output = phrase_output

        self.final_wa_path = os.path.join(self.alignment_folder, self.word_output) + '.A3.final'

    def _clean(self, source, target, source_cleaned, target_cleaned, m):
        self.info('Cleaning...')
        source_in = codecs.open(source, 'rb', 'utf-8')
        target_in = codecs.open(target, 'rb', 'utf-8')
        source_out = codecs.open(source_cleaned, 'wb', 'utf-8')
        target_out = codecs.open(target_cleaned, 'wb', 'utf-8')

        while True:
            source_line = source_in.readline()
            target_line = target_in.readline()

            if not source_line or not target_line:
                break

            source_tokens = tokenize(source_line)
            target_tokens = tokenize(target_line)

            if len(source_tokens) == 0 or len(source_tokens) > m \
                    or len(target_tokens) == 0 or len(target_tokens) > m:
                continue

            source_out.write(' '.join(source_tokens) + '\n')
            target_out.write(' '.join(target_tokens) + '\n')

        source_in.close()
        target_in.close()
        source_out.close()
        target_out.close()

    def word_alignment(self, override=False, clean=True):
        if os.path.exists(self.final_wa_path) and not override:
            return

        cleaned_src_path = self.source_language_corpus_path + '.cleaned'
        cleaned_target_path = self.target_language_corpus_path + '.cleaned'

        if clean:
            self._clean(self.source_language_corpus_path, self.target_language_corpus_path, cleaned_src_path, cleaned_target_path, self.max_tokens)

        # Create snt files
        self.info('Create snt files...')
        subprocess.call([r'../tools/giza-pp/GIZA++-v2/plain2snt.out', cleaned_src_path, cleaned_target_path])

        source_target_snt = cleaned_src_path + '_' + cleaned_target_path.split('/')[-1] + '.snt'

        # Create cooc file
        #self.info('Creating coocurrence file...')
        #cooc_file_path = self.alignment_folder + '/' + 'cooc.cooc'
        #subprocess.call(['../mgizapp/manual-compile/snt2cooc', cooc_file_path, cleaned_src_path+'.vcb', cleaned_target_path+'.vcb', source_target_snt])

        # Create vcb.classes files
        self.info('Create classes files...')
        subprocess.call([r'../giza-pp/mkcls-v2/mkcls', '-p' + cleaned_src_path, '-V' + cleaned_target_path + '.vcb.classes'])
        subprocess.call([r'../giza-pp/mkcls-v2/mkcls', '-p' + cleaned_target_path, '-V' + cleaned_src_path + '.vcb.classes'])

        # Run word alignment
        self.info('Running word alinment...')
        subprocess.call([r'../tools/giza-pp/GIZA++-v2/GIZA++',
            '-S', cleaned_src_path + '.vcb',
            '-T', cleaned_target_path + '.vcb',
            '-C', source_target_snt,
            '-o', self.word_output,
            '-outputpath', self.alignment_folder,
            ])

    def read_sentence_alignment(self, f):
        comment = f.readline()
        if not comment:
            raise EOFError()
        target = f.readline().split()
        source = f.readline().split()

        target_sen = [Word(x) for x in target]
        source_sen = []

        # Build source and target sentences
        i = 0
        while i < len(source):
            token = source[i]

            if token == 'NULL':
                while source[i] != '})': i += 1
                i += 1
                continue

            word = Word(token)
            i += 1

            i += 1  # skip '({'
            while source[i] != '})':
                target_idx = int(source[i]) - 1
                word.al.add(target_idx)
                target_sen[target_idx].al.add(len(source_sen))
                i += 1
            i += 1 # skip ')}'

            source_sen.append(word)

        return source_sen, target_sen

    def extract_phrase_pairs(self, s, t):
        # Check whether set of indexes x is quasi-consecutive in sentence sen
        def is_quasi_consecutive(x, sen):
            for i in xrange(min(x)+1, max(x)):
                if i not in x and len(sen[i].al) > 0:
                    return False
            return True

        pairs = []

        # (s_start, ..., s_end) is the source phrase
        for s_start in xrange(len(s)):
            # tp is the set of words aligned to the current source phrase
            tp = set()
            tp_min = 0xffffffff
            tp_max = -1

            # sp is the set of words aligned to tp
            sp = set()
            calc_sp = True

            for s_end in xrange(s_start, len(s)):
                tp |= s[s_end].al
                if len(tp)==0 or not is_quasi_consecutive(tp, t):
                    continue

                old_min = tp_min
                old_max = tp_max

                if s[s_end].al:
                    new_min = min(s[s_end].al)
                    new_max = max(s[s_end].al)
                    if new_min < tp_min:
                        tp_min = new_min
                    if new_max > tp_max:
                        tp_max = new_max

                if calc_sp:
                    sp = reduce(operator.or_, (t[i].al for i in xrange(tp_min, tp_max+1)))
                    calc_sp = False
                else:
                    if tp_min < old_min:
                        sp |= reduce(operator.or_, (t[i].al for i in xrange(tp_min, old_min)))
                    if tp_max > old_max:
                        sp |= reduce(operator.or_, (t[i].al for i in xrange(old_max+1, tp_max+1)))

                assert len(sp)>0
                for x in sp:
                    if x < s_start or x > s_end:
                        continue

                pairs.append(tuple(s[i].word for i in xrange(s_start, s_end+1)))

        return pairs


    def phrase_alignment(self):
        wa = codecs.open(self.final_wa_path, 'rb', 'UTF-8')
        self.info('Extracting source pharses...')

        tot_lines = 0
        for l in wa:
            tot_lines += 1
        wa.seek(0, 0)
        checkpoint = (tot_lines/3) / 100
        print '0% done',

        src_phrases = set()
        try:
            line = 0
            while True:
                line += 1
                if (line % checkpoint) == 0:
                    print '\r%d%% done' % (line/checkpoint),
                s, t = self.read_sentence_alignment(wa)
                for src_phrase in self.extract_phrase_pairs(s, t):
                    #print ' '.join(src_phrase)
                    src_phrases.add(src_phrase)
                #break
        except EOFError:
            pass
        print '\r           \r',
        print 'Extracted', len(src_phrases), 'source phrases'
        wa.close()
