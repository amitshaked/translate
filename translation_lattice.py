#!/usr/bin/env python2.7
import codecs
from phrase import Phrase
from tokenizer import tokenize

class TranslationLattice(object):
    def __init__(self):
        self.sentence = None
        self.phrases = []

    def set_sentence(self, s):
        self.sentence = tokenize(s)

    def set_phrases(self, p):
        self.phrases = p

    def add_phrase(self, p):
        self.phrases.append(p)


    def build_lattice(self, pt, sentence):
        '''
        Gets a phrase table and the tokenized sentence and outputs a lattice
        file formatted as follows:
            whole sentence
            1-1:
            <English translation> <Translation score>
            <English translation> <Translation score>
            ...
            1-2:
            <English translation> <Translation score>
            <English translation> <Translation score>
            ...
            2-2:

        The spans n-n refer to the tokens of the input Spanish sentence
        '''
        sentence = tokenize(sentence)
        self.sentence = sentence
        for i in xrange(len(sentence)):
            for j in xrange(i, len(sentence)):
                foreign = sentence[i:j+1]
                p = Phrase(foreign, i, j)
                translations = pt.translate(foreign)
                if not translations:
                    continue
                p.set_translations(pt.translate(foreign))
                self.phrases.append(p)


    def get_all_untranslated_phrases(self, translated_indexes):
        new_phrases = []
        for p in self.phrases:
            for i in translated_indexes:
                if p.start <= i and i <= p.end:
                    break
            else:
                new_phrases.append(p)

        return new_phrases

    def dump(self, output_file):
        with codecs.open(output_file, 'wb', 'utf8') as f:
            # write sentence
            f.write('%s\n' % ' '.join(self.sentence))
            for phrase in self.phrases:
                # write new phrase line
                f.write('%d-%d:\n' % (phrase.start+1, phrase.end+1))
                for trans in phrase.translations:
                    # write translation
                    f.write('%s %f\n'%(trans.translation, trans.prob))


    @staticmethod
    def load(f):
        sentence = None
        while True:
            # sentence
            l = f.readline().strip()
            if not l:
                break
            sentence = tokenize(l)

        assert sentence != None, "Can't find sentence in file!"

        tl = TranslationLattice()
        tl.set_sentence(sentence)

        #read phrases
        phrases = []
        current_phrase = None
        while True:
            l = f.readline().strip()
            if not l:
                break
            elif l.endswith(':'): #new phrase line
                if current_phrase != None:
                    tl.add_phrase(current_phrase)
                start, end = l[:-1].split('-')
                current_phrase = Phrase(sentence[start : end], start, end)
            else: # translation line:
                t, prob = l.split()
                current_phrase.add_translation(t, prob)

        # add last phrase
        if current_phrase != None:
            tl.add_phrase(current_phrase)

        return tl



