#!/usr/bin/env python2.7
import codecs
from phrase import Phrase
from translation import Translation
from tokenizer import tokenize

class TranslationLattice(object):
    def __init__(self):
        self.sentence = None
        self.phrases = {}

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
        for start in xrange(len(sentence)):
            self.phrases[start] = {}
            for end in xrange(start+1, len(sentence)+1):
                foreign = sentence[start:end]
                p = Phrase(foreign, start, end)
                if len(foreign) == 1 and foreign[0] == ',':
                    p.translations = [Translation(foreign, (',',), 0)]
                else:
                    p.translations = pt.translate(foreign)
                self.phrases[start][end] = p


    def get_all_untranslated_possible_phrases(self, translated_indexes):
        new_phrases = []
        for start in self.phrases.iterkeys():
            for end in self.phrases[start].iterkeys():
                for i in translated_indexes:
                    if start <= i < end:
                        break
                else:
                    new_phrases.append(self.phrases[start][end])

        return new_phrases

    def get_untranslated_phrases(self, translated_indexes):
        all_indexes = sorted([-1] + list(translated_indexes) + [len(self.sentence)])
        ranges = [(all_indexes[i]+1, all_indexes[i+1]) for i in xrange(len(all_indexes)-1)]

        new_phrases = []
        for start, end in ranges:
            if start == end:
                continue
            new_phrases.append(self.phrases[start][end])

        return new_phrases

    def translate(self, start, end):
        '''
        return the translations in the phrasetable for a given indexes if such exsits
        '''
        if start in self.phrases.iterkeys() and end in self.phrases[start].iterkeys():
            return self.phrases[start][end].translations
        return []

    def dump(self, output_file):
        with codecs.open(output_file, 'wb', 'utf8') as f:
            # write sentence
            f.write('%s\n' % ' '.join(self.sentence))
            for start in self.phrases:
                for phrase in self.phrases[start].itervalues():
                    # write new phrase line
                    f.write('%d-%d:\n' % (phrase.start+1, phrase.end))
                    for trans in phrase.translations:
                        # write translation
                        f.write('%s %f\n'%(trans.translation, trans.prob))


    @staticmethod
    def load(f):
        #FIXME
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



