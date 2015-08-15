#!/usr/bin/env python2.7
from constants import *


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
    def __init__(self, prev, last_foreign_covered_indexes, \
        last_added_phrase, last_target_words):
        self.prev = prev
        self.last_foreign_covered_indexes = list(set(last_foreign_covered_indexes))
        self.last_added_phrase = last_added_phrase
        self.last_target_words = last_target_words
        self._calc_prob()

    def get_foreign_covered_indexes(self):
        if self.prev == None:
            return self.last_foreign_covered_indexes
        return list(set(self.prev.get_foreign_covered_indexes() \
            + self.last_foreign_covered_indexes))

    def get_translation(self):
        if self.last_added_phrase == None:
            return ""

        trans = self.last_added_phrase.get_best_translation().translation
        if self.prev != None:
            return self.prev.get_translation() + trans

    def get_translation_prob(self):
        return self.translation_prob

    def _calc_translation_prob(self):
        if self.last_added_phrase == None:
            self.translation_prob = 0
            return

        self.translation_prob = self.prev.get_translation_prob() \
         + self.last_added_phrase.get_best_translation().prob

    def get_lm_prob(self):
        return self.lm_prob

    def _calc_lm_prob(self):
        '''
        '''
        if self.last_added_phrase == None:
            self.lm_prob = 0
            return

        self.lm_prob = Hypothesis.lm.calc_prob(self.last_added_phrase.get_best_translation() \
            ,self.prev.last_target_words )

    def _calc_prob(self):
        self._calc_translation_prob()
        self._calc_lm_prob()

        self.prob =  LAMBDA_TRANSLATION * self.translation_prob + LAMBDA_LM * self.lm_prob

    def get_prob(self):
        return self.prob

    def get_future_prob(self):
        return Hypothesis.estimator.get_future_prob(self)

    def is_empty(self):
        return self.last_added_phrase == None

    @staticmethod
    def AddFutureProbEstimator(estimator):
        Hypothesis.estimator = estimator

    @staticmethod
    def AddLanguageModel(lm):
        Hypothesis.lm = lm

