#!/usr/bin/env python2.7
from phrase import Phrase
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
        print sentence
        self.sentence = sentence
        for start in xrange(len(sentence)):
        	self.phrases[start] = {}
            for end in xrange(start+1, len(sentence)):
                foreign = sentence[start:end]
                p = Phrase(foreign, i, j)
                p.set_translations(pt.translate(foreign))
                self.phrases[start][end] = p


    def get_all_untranslated_possible_phrases(self, translated_indexes):
        for start in self.phrases.indexes():
        	for end in self.phrases[start].indexes():
        		flag = True
	            for i in translated_indexes:
	                if start <= i and i <= end:
	                    flag = False
	                    continue
	            if flag:
	                new_phrases.append(p)

        return new_phrases

    def get_untranslated_phrases(self, translated_indexes):
        new_phrases = []
        for i in translated_indexes:
	        for start in xrange(len(self.sentence))
	        	for end in xrange(start , len(self.sentence))
	        		if end +1 >= i:
	        			break
        		new_phrases.append(self.phrases[start][end])
        		start = i + 1

        return new_phrases

    def translate(self, start, end):
    	'''
    	return the best translation in the phrasetable for a given indexes if such exsits
    	'''
    	if start in self.phrases.indexes() and end in self.phrases[start].indexes()
    		return self.phrases[start][end].get_best_translation()
    	return None

    def dump(self, output_file):
        with open(output_file, 'wb') as f:
            # write sentence
            f.write('%s\n' % ' '.join(self.sentence))
            for phrase in self.phrases:
                # write new phrase line
                f.write('%d-%d:\n' % (phrase.start, phrase.end))
                for trans in phrase.translations:
                    # write translation
                    f.write('%s %f\n'%(trans.translation, trans.prob))


    @staticmethod
    def Load(f):

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



