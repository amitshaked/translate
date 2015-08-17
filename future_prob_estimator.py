from collections import defaultdict, namedtuple
from constants import *

BestTranslation = namedtuple('BestTranslation', ['trans', 'lm_prob', 'trans_prob', 'prob'])

class FutureProbEstimator(object):
    '''
    Computes the estimated future probability for every possible phrase
    '''
    def __init__(self, lattice, lm):
        self.lattice = lattice
        self.lm = lm
        self.best_trans = defaultdict(dict)

        for length in xrange(1, len(lattice.sentence) + 1):
            for start in xrange(len(lattice.sentence) - length + 1):
                end = start + length
                self.best_trans[start][end] = self.get_best_translation(start, end)

                for i in xrange(start+1, end):
                    new_trans_prob = self.best_trans[start][i].trans_prob + self.best_trans[i][end].trans_prob
                    new_lm_prob = self.best_trans[start][i].lm_prob
                    new_lm_prob += self.lm.calc_prob(self.best_trans[i][end].trans, self.best_trans[start][i].trans)
                    new_prob = LAMBDA_TRANSLATION * new_trans_prob + LAMBDA_LM * new_lm_prob
                    if new_prob < self.best_trans[start][end].prob:
                        self.best_trans[start][end] = BestTranslation(
                                self.best_trans[start][i].trans + self.best_trans[i][end].trans,
                                new_lm_prob, new_trans_prob, new_prob)

    def get_best_translation(self, start, end):
        translations = self.lattice.translate(start, end)
        best = BestTranslation(tuple(), float('-inf'), float('-inf'), float('-inf'))
        for translation in translations:
            trans_prob = translation.prob
            lm_prob = self.lm.calc_prob(translation.translation)
            prob = LAMBDA_TRANSLATION * trans_prob + LAMBDA_LM * lm_prob
            if prob < best.prob:
                best = BestTranslation(translation.translation, lm_prob, trans_prob, prob)
        return best

    def get_future_prob(self, foreign_covered_indexes):
        phrases = self.lattice.get_untranslated_phrases(foreign_covered_indexes)
        prob = 0.0
        for p in phrases:
            prob += self.best_trans[p.start][p.end].prob

        return prob
