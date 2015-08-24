#!/usr/bin/env python2
import subprocess
import os.path
import cPickle
import argparse
import sys
import phrase_table
from itertools import count
from progressbar import ProgressBar
from collections import namedtuple
from tokenizer import tokenize
from constants import *

def main():
    parser = argparse.ArgumentParser(description="Build a phrase table from the bilingual parallel texts and a language model from the corpus file")
    parser.add_argument('-pt', '--phrase-table',
            help='phrase table output file (PT is generated if given)')
    parser.add_argument('-lm', '--lm-output',
            help='language model output file (LM is generated if given)')

    pt_group = parser.add_argument_group('Phrase Table generation options')
    pt_group.add_argument('-s', '--source-language-corpus-path',
            help='The source language file')
    pt_group.add_argument('-d', '--target-language-corpus-path',
            help='The destination language file')
    pt_group.add_argument('-af', '--alignment-folder',
            help='alignment folder')
    pt_group.add_argument('-wo', '--word-output', default='word',
            help='word alignment output path')
    pt_group.add_argument('-mt', '--max-tokens', type=int, default=60,
            help='Maximum number of tokens per line')

    lm_group = parser.add_argument_group('LM generation options')
    lm_group.add_argument('-c', '--corpus-file-for-lm',
            help='The corpus file for building a language model')

    args = parser.parse_args()

    if args.phrase_table is None and args.lm_output is None:
        parser.error('either -pt or -lm is required')

    if args.phrase_table is not None:
        if args.source_language_corpus_path is None:
            parser.error('--source-language-corpus-path is required with -pt')
        if args.target_language_corpus_path is None:
            parser.error('--target-language-corpus-path is required with -pt')
        if args.alignment_folder is None:
            parser.error('--alignment-folder is required with -pt')

        pt = phrase_table.PhraseTable(args.max_tokens, args.alignment_folder)
        pt.source_language_corpus_path = args.source_language_corpus_path
        pt.target_language_corpus_path = args.target_language_corpus_path
        pt.word_output = args.word_output

        pt.word_alignment()
        pt.phrase_alignment()
        pt.create_index()
        pt.save(args.phrase_table)

    if args.lm_output is not None:
        if args.corpus_file_for_lm is None:
            parser.error('--corpus-file-for-lm is required with -lm')

        create_language_model(args.corpus_file_for_lm, args.lm_output)

    return 0

def create_language_model(corpus, lm_output):
    corpus_token = corpus + '.cleaned'
    if not os.path.exists(corpus_token) or raw_input('Cleaned LM corpus already exists! Override [y/N]? ') == 'y':
        print 'Cleaning corpus file...'
        corpus_f = open(corpus, 'rb')
        corpus_token_f = open(corpus_token, 'wb')
        for line_count, _ in enumerate(corpus_f): pass
        corpus_f.seek(0, 0)

        pbar = ProgressBar(maxval=line_count).start()
        for l in count(0):
            line = corpus_f.readline()
            if not line:
                break
            line_tokens = tokenize(line)
            corpus_token_f.write(' '.join(line_tokens) + '\n')
            pbar.update(l)
        pbar.finish()

        corpus_f.close()
        corpus_token_f.close()

    if os.path.exists(lm_output):
        if raw_input('Language model already exists! Override [y/N]? ') != 'y':
            return

    print 'Training %d-gram model...' % (NGRAM)
    subprocess.call(['externals/kenlm/bin/lmplz', '-o', str(NGRAM), '-S', '20%',
        '--text', corpus_token, '--arpa', lm_output + '.arpa'])
    subprocess.call(['externals/kenlm/bin/build_binary', lm_output + '.arpa', lm_output])


if __name__ == '__main__':
    sys.exit(main())
