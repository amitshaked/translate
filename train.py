import argparse
import sys
import phrase_table
from collections import namedtuple

def main():
    parser = argparse.ArgumentParser(description="Build a phrase table from the bilingual parallel texts and a language model from the corpus file")
    parser.add_argument('-s', '--src', type=str, required=True, help='The source language file')
    parser.add_argument('-d', '--dest', type=str, required=True, help='The destination language file')
    parser.add_argument('-c', '--corpus', type=str, required=True, help='The corpus file')
    parser.add_argument('-po', '--phrase_output', type=str, required=True, help='phrase alignment output path')
    parser.add_argument('-lo', '--lm_output', type=str, required=True, help='language model output path')
    parser.add_argument('-wo', '--word_output', type=str, default='./words.A3', help='word alignment output path')
    parser.add_argument('-mt', '--max_tokens', type=int, default=60, help='Maximum number of tokens pe line')
   
    args = parser.parse_args()

    pt = phrase_table.PhraseTable(args.src, args.dest, args.word_output, args.phrase_output)
    pt.clean(args.max_tokens)
    pt.word_alignment()
    pt.phrase_alignment()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
