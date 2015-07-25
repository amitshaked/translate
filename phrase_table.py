import re
import os.path
import subprocess


ALPHABET = [chr(ord('a') + i) for i in xrange(ord('z') - ord('a') + 1)] + [chr(ord('A') + i) for i in xrange(ord('Z') - ord('A') + 1)]

# TODO: should we accept non-alphabet tokens?
def tokenize(s):
	def is_word(x):
		return len(x) and x[0] in ALPHABET
	def convert(x):
		return re.sub('[^a-zA-Z]', '', x).lower()
	return filter(is_word, map(convert, re.findall(r"[\w'.]+", s)))


class PhraseTable(object):

	def __init__(self, source_language_corpus_path, target_language_corpus_path, alignment_folder, word_output, phrase_output, max_tokens, verbose=True):
		# Print to log if needed
		if verbose:
			def info(s):
				print s
		else:
			def info(s):
				pass

		self.info = info
		self.source_language_corpus_path = source_language_corpus_path
		self.target_language_corpus_path = target_language_corpus_path
		self.max_tokens = max_tokens
		self.alignment_folder = alignment_folder
		self.word_output = word_output
		self.phrase_output = phrase_output

	def _clean(self, src, dest, cleaned_src_path, cleaned_target_path, m):
		def longer_than_max(x):
			return len(tokenize(x)) < m

		cleaned_src = []
		cleaned_target = []
		
		self.info('Cleaning...')
		with open(self.source_language_corpus_path, 'rb') as src:
			cleaned_src = filter(longer_than_max, src.readlines())
		with open(self.target_language_corpus_path, 'rb') as target:
			cleaned_target = filter(longer_than_max, target.readlines())

		self.info('Dumping cleaned files...')
		with open(cleaned_src_path, 'wb') as src:
			src.writelines(cleaned_src)
		with open(cleaned_target_path, 'wb') as target:
			target.writelines(cleaned_target)

	def word_alignment(self, override=False):
		final_path = self.alignment_folder + '/' + self.word_output + '.actual.ti.final'
		if os.path.isfile(final_path) and not override:
			return

		#Clean lines longer than max tokens
		cleaned_src_path = self.source_language_corpus_path + '.cleaned'
		cleaned_target_path = self.target_language_corpus_path + '.cleaned'
		self._clean(self.source_language_corpus_path, self.target_language_corpus_path, cleaned_src_path, cleaned_target_path, self.max_tokens)

		#Create snt files
		self.info('Create snt files...')
		subprocess.call([r'../giza-pp/GIZA++-v2/plain2snt.out', cleaned_src_path, cleaned_target_path])

		#Create vcb.classes files
		self.info('Create classes files...')
		subprocess.call([r'../giza-pp/mkcls-v2/mkcls', '-p', cleaned_src_path, '-V', cleaned_target_path + '.vcb.classes'])
		subprocess.call([r'../giza-pp/mkcls-v2/mkcls', '-p', cleaned_target_path, '-V', cleaned_src_path + '.vcb.classes'])

		#Run word alignment
		target_source_snt = cleaned_target_path + '_' + cleaned_src_path.split('/')[-1] + '.snt'
		
		self.info('Running word alinment...')		
		subprocess.call([r'../giza-pp/GIZA++-v2/GIZA++', '-S', cleaned_target_path + '.vcb' \
			,'-T', cleaned_src_path + '.vcb' \
			,'-C', target_source_snt \
			,'-o', self.word_output \
			,'-outputpath', self.alignment_folder])

	def phrase_alignment(self):
		pass