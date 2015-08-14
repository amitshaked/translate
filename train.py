import argparse
import sys
import phrase_table
from nltk.probability import LidstoneProbDist, WittenBellProbDist
import nltk
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

	args = parser.parse_args()

	pt = phrase_table.PhraseTable(args.source_language_corpus_path, args.target_language_corpus_path, \
		args.alignment_folder, args.word_output, args.phrase_output, args.max_tokens, verbose = True)
	pt.word_alignment()
	pt.phrase_alignment()

	create_language_model(args.corpus_file_for_lm)

	return 0

def create_language_model(corpus):
	estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
	with open(corpus, 'rb') as c:
		lm = nltk.NgramModel(3, c.readlines(), estimator)
		print lm


if __name__ == '__main__':
	sys.exit(main())
