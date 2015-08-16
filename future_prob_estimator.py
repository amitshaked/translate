
from collections import defaultdict
from constant import *

class FutureProbEstimator(object):
    '''
    Computes the estimated future probability for every possible phrase
    '''
    def __init__(self, lattice, lm):
        self.lattice = lattice
        self.lm_prob = defaultdict(dict)
        self.translation_prob = defaultdict(dict)

        for length in xrange(1, len(lattice.sentence) + 1):
            for start in xrange(len(lattice.sentence) - length + 1):
                end = start + length
                self.lm_prob[start][end] = lm.calc_prob(lattice.sentence[start:end])
                t = lattice.translate(start, end)
                if t is not None:
                    self.translation_prob[start][end] = t.prob
                else:
                    self.translation_prob[start][end] = float("-infinity")

                for i in xrange(start+1, end):
                    if self.translation_prob[start][i] + self.translation_prob[i][end] \
                        < self.translation_prob[start][end]:
                        self.translation_prob[start][end] = self.translation_prob[start][i] + self.translation_prob[i][end]

    def get_future_prob(self, foreign_covered_indexes):
        phrases = self.lattice.get_untranslated_phrases(foreign_covered_indexes)
        t_prob = 0
        lm_prob = 0
        for p in phrases:
            t_prob += self.translation_prob[p.start][p.end]
            lm_prob += self.lm_prob[p.start][p.end]

        return LAMBDA_TRANSLATION * t_prob + LAMBDA_LM * lm_prob
