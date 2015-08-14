#!/usr/bin/env python2.7

class Translation(object):
	def __init__(self, foreign_words, translation, prob):
		self.foreign_words = foreign_words
		self.translation = translation
		self.prob = prob

	