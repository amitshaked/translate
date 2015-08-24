#!/usr/bin/env python2.7
import argparse
import sys
from collections import namedtuple

def main():
    parser = argparse.ArgumentParser(description="Spanish to English translator")
    parser.add_argument('-pt', '--phrase-table', required=True, help='The phrase table file')
    parser.add_argument('-lm', '--language-model', required=True, help='The language model file')
    parser.add_argument('-s', '--sentence', type=lambda s: str(s).decode('utf8'), required=True, help='The sentence to translate')
    parser.add_argument('--max-histogram-size', type=int, default=30,
            help='Maximum number of hypotheses in the stack (default: 30)')
    parser.add_argument('--search-size', type=int, default=100,
            help='Maximum number of phrases to retrieve per foreign phrase (default: 100)')
    parser.add_argument('--reorder-alpha', type=float, default=0.5,
            help='Alpha parameter for reordering model (default: 0.5)')
    parser.add_argument('--lambda-translation', type=float, default=0.5,
            help='Phrase alignment lambda (default: 0.5)')
    parser.add_argument('--lambda-lm', type=float, default=0.5,
            help='Language model lambda (default: 0.5)')
    parser.add_argument('--lambda-reorder', type=float, default=0.1,
            help='Reorder model lambda (default: 0.1)')
    parser.add_argument('--lambda-length', type=float, default=0.1,
            help='Length award lambda (default: 0.1)')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    import constants
    constants.MAX_HISTOGRAMS = args.max_histogram_size
    constants.SEARCH_SIZE = args.search_size
    constants.REORDER_ALPHA = args.reorder_alpha
    constants.LAMBDA_TRANSLATION = args.lambda_translation
    constants.LAMBDA_LM = args.lambda_lm
    constants.LAMBDA_REORDER = args.lambda_reorder
    constants.LAMBDA_LENGTH = args.lambda_length

    from translation_lattice import TranslationLattice
    from lm import LanguageModel
    from stack_decoder import StackDecoder
    from phrase_table import PhraseTable

    lattice_output_file = 'files/lattice.txt'
    pt = PhraseTable.load(args.phrase_table)
    lattice = TranslationLattice()
    lattice.build_lattice(pt, args.sentence)
    lattice.dump(lattice_output_file)

    if args.verbose:
        print >>sys.stderr, 'Translating: \'%s\'' % (u' '.join(lattice.sentence))

    lm = LanguageModel(args.language_model)
    decoder = StackDecoder(lattice, lm)
    best = decoder.decode()

    if best is not None:
        translation = best.get_translation()[1:]  # skip <s>
        while len(translation) and translation[0] == ',':
            translation = translation[1:]
        while len(translation) and translation[-1] == ',':
            translation = translation[:-1]
        translation = ' '.join(translation)
        translation = translation.replace(' ,', ',')
        if len(translation):
            translation = translation[0].upper() + translation[1:]
        if args.sentence[-1] == '.' or args.sentence[-1] == '?':
            translation += args.sentence[-1]
        score = best.get_prob()
    else:
        translation = ''
        score = float('-inf')

    print translation
    if args.verbose:
        print >>sys.stderr, "Score: %.2f" % best.get_prob()

    return 0

if __name__ == '__main__':
    sys.exit(main())
