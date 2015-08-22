#!/usr/bin/env python2.7

NGRAM = 3 # the order of the language model (ngram size)

MAX_HISTOGRAMS = 30 #Histogram pruning keeps a certain number n of hypotheses

LAMBDA_TRANSLATION = 0.5
LAMBDA_LM = 0.5
LAMBDA_REORDER = 0.1
LAMBDA_LENGTH = 0.1

SEARCH_SIZE = 50
