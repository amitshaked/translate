#!/usr/bin/env python2.7
from constants import *
from phrase import Phrase
from translation import Translation


class Hypothesis(object):
    '''
    Each search state (hypothesis) is represented by
        a back link to the best previous state (needed for finding the best translation of the sentence by back-tracking through the search states)
        the foreign words covered so far
        the last added target phrase (needed for reading the translation from a path of hypotheses)
        the last n-1 target words generated in a n-gram model (needed for computing future language model costs)
        the cost so far
        an estimate of the future cost (is precomputed and stored for efficiency reasons)
    '''
    def __init__(self, prev, last_added_phrase, translation_index, 
        last_target_words, eos=False):
        self.prev = prev
        self.last_added_phrase = last_added_phrase
        self.translation_index = translation_index
        self.last_target_words = last_target_words
        self.eos = eos
        self._calc_prob()
        self._calc_foreign_covered_indexes()

    def _calc_foreign_covered_indexes(self):
        if self.prev is None:
            self.foreign_covered_indexes =set()
        else:
            self.foreign_covered_indexes = set(range(self.last_added_phrase.start, self.last_added_phrase.end))\
                .union(self.prev.get_foreign_covered_indexes())
        

    def get_foreign_covered_indexes(self):
        return self.foreign_covered_indexes

    def get_translation(self):
        if self.last_added_phrase is None:
            return tuple()

        trans = self.last_added_phrase.translations[self.translation_index].translation
        if self.prev is not None:
            trans = self.prev.get_translation() + trans
        return trans

    def get_translation_prob(self):
        return self.translation_prob

    def _calc_translation_prob(self):
        self.translation_prob = self.last_added_phrase.translations[self.translation_index].prob
        if self.prev is not None:
            self.translation_prob += self.prev.get_translation_prob()

    def get_lm_prob(self):
        if self.prev is None:
            return self.lm_prob
        else:
            return self.prev.get_lm_prob() + self.lm_prob

    def _calc_lm_prob(self):
        if self.prev is None:
            prev_target_words = []
        else:
            prev_target_words = self.prev.last_target_words

        trans = self.last_added_phrase.translations[self.translation_index].translation
        if self.eos:
            trans += (u'</s>',)

        self.lm_prob = Hypothesis.lm.calc_prob(trans, prev_target_words)

    def _calc_prob(self):
        self._calc_translation_prob()
        self._calc_lm_prob()

        self.prob = LAMBDA_TRANSLATION * self.get_translation_prob()
        self.prob += LAMBDA_LM * self.get_lm_prob()

    def get_prob(self):
        return self.prob

    def get_future_prob(self):
        return Hypothesis.estimator.get_future_prob(self.get_foreign_covered_indexes())

    def is_empty(self):
        return self.prev is None

    @staticmethod
    def AddFutureProbEstimator(estimator):
        Hypothesis.estimator = estimator

    @staticmethod
    def AddLanguageModel(lm):
        Hypothesis.lm = lm

    @classmethod
    def create_initial(cls):
        initial_phrase = Phrase(None, None, None)
        initial_phrase.translations = [Translation(None, (u'<s>',), 0)]
        return cls(None, initial_phrase, 0, (u'<s>',))

