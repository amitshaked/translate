#!/usr/bin/env python2.7

class HypothesisStack(object):
	'''
	Keep the best hypotheses that cover the same number of foreign words.
	Keep at most #size hypotheses
	'''
	def __init__(self, size):
		self.size = size
		self.hyps = []

	def push(self, hyp):
		'''
		pushes new thesis to stack. recombine if possible, prune if necessary.
		'''
		if self._recombine_all_hyps(hyp):
			return

		self.hyps.append(hyp)
		if len(self.hyps) > self.size:
			self._prune

	def _recombine_all_hyps(self, new_hyp):
		'''
		Trys to recombine the new thesis with all current theses
		return true if recombining succeded
		'''
		hyps = self.hyps
		for hyp in hyps:
			flag, t = recombine(hyp, new_hyp)
			if flag:
				self.hyps.remove(hyp)
				self.hyps.append(t)
				return True

		return False


	def _prune(self):
		'''
		We compare the hypotheses in the stack (they all cover the same number of foreign words)
		 and prune out the inferior hypotheses.
		key = hyp.prob + hyp.future_prob
		'''
		
		self.hyps = sorted(self.hyps, key=lambda hyp: hyp.get_prob() + hyp.get_future_prob(), reverse= True)[:size]
	def get_best_hypothesis(self):
		if len(self.hyps) == 0:
			return
		return sorted(self.hyps, key=lambda hyp: hyp.get_prob(), reverse=True)[0]

	def __getitem__(self, item):
		return self.hyps[item]

	def __len__(self):
		return len(self.hyps)

def recombine(hyp1, hyp2):
	'''
	Two hypothesis paths lead to hypotheses indistinguishable in subsequent search
		- same number of foreign words translated
		- same last n-1 English words in output (assuming n language model)
		- same last foreign word translated
		- different scores

	returns true, best if recombining succeded
	'''
	if hyp1.is_empty() or hyp2.is_empty():
		return False, None

	if len(hyp1.get_foreign_covered_indexes()) == len(hyp2.get_foreign_covered_indexes()) \
		and hyp1.last_target_words == hyp2.last_target_words \
		and hyp1.last_added_phrase.words[-1] == hyp2.last_added_phrase.words[-1]:
		if hyp1.get_prob() > hyp2.get_prob():
			return True, hyp1

		return True, hyp2

	return False, None