import re

ALPHABET = [chr(ord('a') + i) for i in xrange(ord('z') - ord('a') + 1)] + [chr(ord('A') + i) for i in xrange(ord('Z') - ord('A') + 1)]

# TODO: should we accept non-alphabet tokens?
def tokenize(s):
	def is_word(x):
		return len(x) and x[0] in ALPHABET
	def convert(x):
		return re.sub('[^a-zA-Z]', '', x).lower()
	return filter(is_word, map(convert, re.findall(r"[\w'.]+", s)))


class PhraseTable(object):

	def __init__(self, src_path, dest_path, word_output, phrase_output, verbose=True):
		# Print to log if needed
		if verbose:
			def info(s):
				print s
		else:
			def info(s):
				pass

		self.info = info

		self.src_path = src_path
		self.dest_path = dest_path

		self.word_output = word_output
		self.phrase_output = phrase_output



	def clean(self, m):
		
		def longer_than_max(x):
			return len(tokenize(x)) < m

		cleaned_src = []
		cleaned_dest = []

		self.info('Cleaning...')
		with open(self.src_path, 'rb') as src:
			cleaned_src = filter(longer_than_max, src.readlines())
		with open(self.dest_path, 'rb') as dest:
			cleaned_dest = filter(longer_than_max, dest.readlines())

		self.info('Dumping cleaned files...')
		with open(self.src_path + '.cleaned', 'wb') as src:
			src.writelines(cleaned_src)
		with open(self.dest_path + '.cleaned', 'wb') as dest:
			dest.writelines(cleaned_dest)

	def word_alignment(self):
		pass

	def phrase_alignment(self):
		pass