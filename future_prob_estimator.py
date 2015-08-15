
from collections import defaultdict
from constant import *

def FutureProbEstimator(object):
	'''
	Computes the estimated future probability for every possible phrase
	'''
	def __init__(self, lattice, lm):
		self.lattice = lattice
		self.lm_prob = defaultdict(dict)
		self.translation_prob = defaultdict(dict)

		for length in xrange(1, len(lattice.sentence) + 1):
			for start in xrange(len(lattice.sentence) - length ):
				end = start + length
				self.lm_prob[start][end] = lm.calc_prob(lattice.sentence[start:end])
				self.translation_prob[start][end] = float("-infinity")
				t = lattice.translate(start, end)
				if t != None:
					self.translation_prob[start][end] = t.prob
				for i in xrange(start+1, end )
					if self.translation_prob[start][i] + self.translation_prob[i+1][end] \
						< self.translation_prob[start][end]:
						self.translation_prob[start][end] = self.ranslation_prob[start][i] + translation_prob[i+1][end]

	def get_future_prob(self, foreign_covered_indexes):
		phrases = self.lattice.get_untranslated_phrases(foreign_covered_indexes)
		t_prob = 0
		lm prob = 0 
		for p in phrases:
			t_prob += self.translation_prob[p.start][p.end]
			lm_prob += self.lm_prob[p.start][p.end]

		return LAMBDA_TRANSLATION * t_prob + LAMBDA_LM * lm_prob