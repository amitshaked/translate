#!/usr/bin/env python2.7
from translation import Translation

BAD_TRANSLATION = Translation([], tuple(), float('-inf'))

class Phrase(object):
    def __init__(self, words, start, end):
        self.words = words
        self.start = start
        self.end = end
        self.translations = []

    def get_best_translation(self):
        if not len(self.translations):
            return BAD_TRANSLATION
        else:
            return self.translations[0]
