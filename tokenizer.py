#!/usr/bin/env python2.7
import re

ALPHABET = [chr(ord('a') + i) for i in xrange(ord('z') - ord('a') + 1)] + [chr(ord('A') + i) for i in xrange(ord('Z') - ord('A') + 1)]

# TODO: should we accept non-alphabet tokens?
def tokenize(s):
    #def is_word(x):
    #    return len(x) and x[0] in ALPHABET
    #def convert(x):
    #    return re.sub('[^a-zA-Z]', '', x).lower()
    #return filter(is_word, map(convert, re.findall(r"[\w'.]+", s)))
    return re.findall(r"[\w']+|,", s.lower(), re.UNICODE)
