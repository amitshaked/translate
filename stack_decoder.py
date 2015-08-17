#!/usr/bin/env python2.7

from future_prob_estimator import FutureProbEstimator
from hypothesis import Hypothesis
from hypothesis_stack import HypothesisStack
from constants import *
from phrase import Phrase

class StackDecoder(object):
    '''
    Implements Beam Search
    '''
    def __init__(self, lattice, language_model):
        self.cost_estimator = FutureProbEstimator(lattice, language_model)
        self.lattice = lattice
        self.hypothesis_stack = {}
        self.number_of_foreign_words = len(self.lattice.sentence)
        Hypothesis.AddLanguageModel(language_model)
        Hypothesis.AddFutureProbEstimator(FutureProbEstimator(lattice, language_model))

    def decode(self):
        '''
        return the best translation for the sentence
        '''
        # initialize hypothesis stack
        for i in xrange(self.number_of_foreign_words +1):
            self.hypothesis_stack[i] = HypothesisStack(MAX_HISTOGRAMS)

        # create initial hypothesis
        hyp_init = Hypothesis.create_initial()
        self.hypothesis_stack[0].push(hyp_init)
        for i in xrange(self.number_of_foreign_words):
            for hyp in self.hypothesis_stack[i]:
                new_hyps = self._generate_new_hypotheses(hyp)
                for new_hyp in new_hyps:
                    self.hypothesis_stack[len(new_hyp.get_foreign_covered_indexes())].push(new_hyp)

        return self._get_best_hypothesis()

    def _generate_new_hypotheses(self, hyp):
        '''
        returns all new hypotheses that can be derived from hyp
        '''
        prev_foreign_covered_indexes = hyp.get_foreign_covered_indexes()
        new_phrases = self.lattice.get_all_untranslated_possible_phrases(prev_foreign_covered_indexes)
        new_hyps = []
        for phrase in new_phrases:
            foreign_covered_indexes = range(phrase.start, phrase.end)
            eos = len(foreign_covered_indexes) + len(prev_foreign_covered_indexes) \
                    == self.number_of_foreign_words
            for i in xrange(len(phrase.translations)):
	            last_target_words = hyp.get_translation() \
	            + phrase.translations[i].translation [-(NGRAM -1):]
	            new_hyps.append(Hypothesis(hyp, foreign_covered_indexes, phrase, i, \
	                last_target_words, eos))

        return new_hyps

    def _get_best_hypothesis(self):
        '''
        Finds the best hypothesis in hypothesisStack[foreign_covered],
        output best path that leads to it;
        '''
        if self.hypothesis_stack[self.number_of_foreign_words] == None:
            print "Error in stack decoder, got no hypothesis for the sentence"
            return
        return self.hypothesis_stack[self.number_of_foreign_words].get_best_hypothesis()
