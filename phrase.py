#!/usr/bin/env python2.7
from translation import Translation

class Phrase(object):
    def __init__(self, words, start, end):
        self.words = words
        self.start = start
        self.end = end
        self.translations = []

    def add_translation(self, trans, prob):
        self.translations.append(Translation(words, trans, prob))

    def set_translations(self, translations):
        self.translations = sorted(translations, key=lambda x: x.prob, reverse =True)

    def get_best_translation(self):
        if self.translations == []:
            if self.start == self.end:
                return Translation(tuple(), tuple(), 0)
            else:
                return Translation(tuple(), tuple(), float('-infinity'))
        return max(self.translations, key=lambda x: x.prob)
