#!/usr/bin/env python2
import nltk
import cPickle

class LanguageModel(object):
    def __init__(self, path):
        #self.lm = cPickle.load(open(path, 'rb'))
        pass

    def calc_prob(self, new_words, old_words = []):
        '''
        compute the phrase lg-probability
        '''
        return 0
