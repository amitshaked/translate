#!/usr/bin/env python2
import argparse
import sys
import phrase_table
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
    parser.add_argument('-lo', '--lm_output', type=str, required=True, help='language model output path')
    parser.add_argument('--override', action='store_true')

    args = parser.parse_args()

    pt = phrase_table.PhraseTable(args.source_language_corpus_path, args.target_language_corpus_path, \
        args.alignment_folder, args.word_output, args.phrase_output, args.max_tokens, verbose = True)
    pt.word_alignment(override=args.override)
    pt.phrase_alignment()

    return 0

if __name__ == '__main__':
    sys.exit(main())
