#!/usr/bin/env python2
import os.path
import cPickle
import argparse
import sys
import phrase_table
from nltk.probability import LidstoneProbDist, WittenBellProbDist
from collections import namedtuple

def main():
    parser = argparse.ArgumentParser(description="Build a phrase table from the bilingual parallel texts and a language model from the corpus file")
    parser.add_argument('-s', '--source_language_corpus_path', type=str, required=True, help='The source language file')
    parser.add_argument('-d', '--target_language_corpus_path', type=str, required=True, help='The destination language file')
    parser.add_argument('-c', '--corpus_file_for_lm', type=str, required=True, help='The corpus file for building a language model')
    parser.add_argument('-af', '--alignment_folder', type=str, required=True, help='alignment folder')
    parser.add_argument('-wo', '--word_output', type=str, default='word', help='word alignment output path')
    parser.add_argument('-po', '--phrase_output', type=str, default='phrase', help='phrase alignment output path')
    parser.add_argument('-mt', '--max_tokens', type=int, default=60, help='Maximum number of tokens pe line')
    parser.add_argument('-lm', '--lm_output', type=str, required=True, help='language model output path')

    args = parser.parse_args()

    pt = phrase_table.PhraseTable(args.max_tokens, args.alignment_folder)
    pt.source_language_corpus_path = args.source_language_corpus_path
    pt.target_language_corpus_path = args.target_language_corpus_path
    pt.word_output = args.word_output
    pt.phrase_output = args.phrase_output

    # TODO: Symmetrization
    pt.word_alignment()
    pt.phrase_alignment()

    create_language_model(args.corpus_file_for_lm, args.lm_output)

    return 0

def create_language_model(corpus, lm_output):
    if os.path.exists(lm_output):
        if raw_input('Language model already exists! Override [y/N]? ') != 'y':
            return

    print 'Training 3-gram model...'
    raise NotImplementedError()
    # TODO


if __name__ == '__main__':
    sys.exit(main())
