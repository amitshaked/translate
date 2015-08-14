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
		self.cost_estimator = FutureProbEstimator(lattice.sentence)
		self.lattice = lattice
		self.hypothesis_stack = {}
		self.number_of_foreign_words = len(self.lattice.sentence)
		Hypothesis.AddLanguageModel(language_model)
		Hypothesis.AddFutureProbEstimator(FutureProbEstimator(lattice.sentence))
			

	def decode(self):		
		'''
		return the best translation for the sentence
		'''
		# initialize hypothesis stack
		for i in xrange(self.number_of_foreign_words +1):
			self.hypothesis_stack[i] = HypothesisStack(MAX_HISTOGRAMS)
		
		# create initial hypothesis
		hyp_init = Hypothesis(None, [], None, [])
		self.hypothesis_stack[0].push(hyp_init)
		for i in xrange(self.number_of_foreign_words):
			for hyp in self.hypothesis_stack[i]:
				new_hyps = self._generate_new_hypotheses(hyp)
				for new_hyp in new_hyps:					
					self.hypothesis_stack[len(new_hyp.get_foreign_covered_indexes())-1].push(new_hyp)

		return self._get_best_hypothesis()

	def _generate_new_hypotheses(self, hyp):
		'''
		returns all new hypotheses that can be derived from hyp
		'''

		new_phrases = self.lattice.get_all_untranslated_phrases(hyp.get_foreign_covered_indexes())
		new_hyps = []
		for phrase in new_phrases:
			foreign_covered_indexes = range(phrase.start, phrase.end +1)
			last_target_words = hyp.get_translation() \
			+ phrase.get_best_translation().translation [-(NGRAM -1):]
			
			new_hyps.append(Hypothesis(hyp, foreign_covered_indexes, phrase, \
				last_target_words))

		return new_hyps

	def _get_best_hypothesis(self):
		'''
		Finds the best hypothesis in hypothesisStack[foreign_covered],
		output best path that leads to it;
		'''
		if self.hypothesis_stack[self.number_of_foreign_words] == None:
			print "Error in stack decoder, got no hypothesis for the sentence"
			return
		return self.hypothesis_stack[self.number_of_foreign_words-1].get_best_hypothesis()