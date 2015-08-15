#!/usr/bin/env python2.7
import argparse
import sys
import phrase_table
from translation_lattice import TranslationLattice
from lm import LanguageModel
from stack_decoder import StackDecoder
from collections import namedtuple
from tokenizer import tokenize
from phrase_table import PhraseTable

def main():
    parser = argparse.ArgumentParser(description="Prints the best translation for a tokenized Spanish sentence")
    parser.add_argument('-pt', '--phrase-table', required=True, help='The phrase table file')
    parser.add_argument('-lm', '--language-model', required=True, help='The language model file')
    parser.add_argument('-s', '--sentence', type=lambda s: str(s).decode('utf8'), required=True, help='The sentence to translate')

    args = parser.parse_args()

    lattice_output_file = 'files/lattice.txt'
    pt = PhraseTable.load(args.phrase_table)
    lattice = TranslationLattice()
    lattice.build_lattice(pt, args.sentence)
    lattice.dump(lattice_output_file)

    print 'Translating: \'%s\'' % (u' '.join(lattice.sentence))

    lm = LanguageModel(args.language_model)
    decoder = StackDecoder(lattice, lm)
    best = decoder.decode()

    if best != None:
        print "Best translation: %s\nScore: %d" % \
                (' '.join(best.get_translation()), best.get_prob())

    return 0

if __name__ == '__main__':
    sys.exit(main())
