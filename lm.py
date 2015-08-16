#!/usr/bin/env python2
import kenlm

class LanguageModel(object):
    def __init__(self, path):
        self.model = kenlm.LanguageModel(path)

    def calc_prob(self, new_words, old_words=tuple()):
        '''
        compute the phrase lg-probability
        '''
        full_sen = ' '.join(tuple(old_words) + tuple(new_words))
        probs = list(prob for prob, _, _ in self.model.full_scores(full_sen, bos=False, eos=False))[len(old_words):]
        assert len(probs) == len(new_words)
        return sum(probs)
