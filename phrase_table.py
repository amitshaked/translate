#!/usr/bin/env python2.7
import cPickle
import math
import codecs
import re
import os.path
import subprocess
import operator
from itertools import count
import progressbar
import tokenizer
from translation import Translation
from db import PhraseDB

MAX_PHRASE_LEN = 7


class Word(object):
    def __init__(self, word):
        self.word = word
        self.al = set()

    def __repr__(self):
        return "%s { %s }" % (self.word.encode('utf-8'), ' '.join(str(x+1) for x in self.al))


class PhraseTable(object):
    def __init__(self, max_tokens, alignment_folder, verbose=True):
        # Print to log if needed
        if verbose:
            def info(s):
                print s
        else:
            def info(s):
                pass

        self.info = info
        self.max_tokens = max_tokens
        self.source_language_corpus_path = None
        self.target_language_corpus_path = None
        self.alignment_folder = alignment_folder
        self.word_output = None
        self.phrase_output = None
        self.final_wa_path = None
        self.db_path = os.path.join(self.alignment_folder, 'phrase.db')
        self.db = None

    def __getstate__(self):
        return {'max_tokens': self.max_tokens, 'alignment_folder': self.alignment_folder}

    def __setstate__(self, state):
        self.__init__(**state)
        self.db = PhraseDB(self.db_path, False)
        self.db.create_probs_index()

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

    def word_alignment(self):
        self.final_wa_path = os.path.join(self.alignment_folder, self.word_output) + '.A3.final'

        if os.path.exists(self.final_wa_path):
            if raw_input('Word alignment already exists! Override [y/N]? ') != 'y':
                return

        cleaned_src_path = self.source_language_corpus_path + '.cleaned'
        cleaned_target_path = self.target_language_corpus_path + '.cleaned'

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
        def is_quasi_consecutive(x, sen):
            ''' Checks whether set of indexes 'x' is quasi-consecutive in sentence 'sen' '''
            for i in xrange(min(x)+1, max(x)):
                if i not in x and len(sen[i].al) > 0:
                    return False
            return True

        pairs = []

        # Calculate minima and maxima
        for i in xrange(len(s)):
            if not s[i].al:
                s[i].al_min = 0xffffffff
                s[i].al_max = -1
            else:
                s[i].al_min = min(s[i].al)
                s[i].al_max = max(s[i].al)

        # (s_start, ..., s_end) is the source phrase
        for s_start in xrange(len(s)):
            # tp is the set of words aligned to the current source phrase
            tp = set()
            tp_min = 0xffffffff
            tp_max = -1

            # sp is the set of words aligned to tp
            sp = set()
            calc_sp = True

            for s_end in xrange(s_start, min(s_start + MAX_PHRASE_LEN, len(s))):
                tp |= s[s_end].al
                if len(tp)==0 or not is_quasi_consecutive(tp, t):
                    continue

                old_min = tp_min
                old_max = tp_max

                if s[s_end].al:
                    if s[s_end].al_min < tp_min:
                        tp_min = s[s_end].al_min
                    if s[s_end].al_max > tp_max:
                        tp_max = s[s_end].al_max

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

                t_start = tp_min
                t_end = tp_max

                source_phrase = tuple(s[i].word for i in xrange(s_start, s_end+1))
                base_target_phrase = tuple(t[i].word for i in xrange(t_start, t_end+1))

                # Add all unaligned words from both sides of the target phrase as
                # additional possible target phrases
                for new_t_start in xrange(t_start, -1, -1):
                    target_phrase = base_target_phrase
                    if new_t_start < t_start:
                        # If the word is aligned, we're done
                        if len(t[new_t_start].al):
                            break
                        target_phrase = tuple(t[i].word for i in xrange(new_t_start, t_start))\
                                + base_target_phrase

                    for new_t_end in xrange(t_end, len(t)):
                        if new_t_end > t_end:
                            # If the word is aligned, we're done
                            if len(t[new_t_end].al):
                                break
                            target_phrase += (t[new_t_end].word,)
                        pairs.append((source_phrase, target_phrase))


        return pairs


    def phrase_alignment(self):
        self.db = PhraseDB(self.db_path, True)
        self.extract_phrases()

        if self.db.trans_probs_available:
            return

        self.info('Loading the number of instances of each English phrase...')
        dst_counts = {}
        for dst_phrase, count in self.db.dst_phrases():
            dst_counts[dst_phrase] = math.log(count)

        self.info('Calculating phrases translation probabilities...')
        num_phrases = self.db.phrases_count()
        trans_probs = []
        with progressbar.ProgressBar(widgets=[progressbar.Percentage(), ' ', progressbar.Bar()],
                max_value=num_phrases) as pbar:
            for i, (src, dst, count) in enumerate(self.db.phrases()):
                prob = math.log(count) - dst_counts[dst]
                trans_probs.append((src, dst, prob))
                if len(trans_probs) >= 1000000:
                    self.db.add_trans_probs(trans_probs)
                    del trans_probs[:]
                if (i % 1000) == 0:
                    pbar.update(i)
        self.db.trans_probs_available = True


    def extract_phrases(self):
        if self.final_wa_path is None:
            raise Exception('Word alignment path must be set before phrase alignment')

        if self.db.phrase_pairs_available:
            return

        wa = codecs.open(self.final_wa_path, 'rb', 'UTF-8')
        self.info('Extracting phrases...')

        tot_lines = 0
        for l in wa:
            tot_lines += 1
        wa.seek(0, 0)

        with progressbar.ProgressBar(widgets=[progressbar.Percentage(), ' ', progressbar.Bar()],
                max_value=tot_lines/3) as pbar:
            phrase_pairs = []
            try:
                for i in count(0):
                    s, t = self.read_sentence_alignment(wa)
                    phrase_pairs.extend(self.extract_phrase_pairs(s, t))
                    if len(phrase_pairs) >= 1000000:
                        self.db.add_phrase_pairs(phrase_pairs)
                        del phrase_pairs[:]
                    pbar.update(i)
            except EOFError:
                pass
        wa.close()

        self.db.phrase_pairs_available = True

    def translate(self, phrase):
        phrase_can = PhraseDB.canonicalize(phrase)
        translations =  list(Translation(*x) for x in self.db.get_translations(phrase))
        return translations

    def save(self, path):
        cPickle.dump(self, open(path, 'wb'), cPickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, path):
        return cPickle.load(open(path, 'rb'))
