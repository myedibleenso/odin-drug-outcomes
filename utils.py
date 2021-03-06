from collections import Counter

def character_ngrams(string, n):

	ngrams = []
	string = "^" + string + "$"
	
	for i in range(0, len(string) - (n-1)):
		yield string[i:i+n]

def ngrams_from_file(file_path, nlp_pipeline, n):

	# open file, store lines as list
	with open(file_path, 'r') as f:
		lines = f.read().splitlines()
	
	# get distinct lines
	distinct_lines = set(lines)

	cnts = Counter()
	for distinct_line in distinct_lines:
		doc = nlp_pipeline.bionlp.annotate(distinct_line)
		counts_for_doc = ngrams_from_doc(doc, n)
		for k,v in counts_for_doc.items():
			cnts[k] += v
	
	# normalize the dictionary
	return normalize(cnts)

def ngrams_from_documents(documents, n):
	
	cnts = Counter()
	for doc in documents:
		counts_for_doc = ngrams_from_doc(doc, n)
		for k,v in counts_for_doc.items():
			cnts[k] += v
	# normalize the dictionary
	return normalize(cnts)

def normalize(cnts_dict):
	total = sum(v for k,v in cnts_dict.items())
	return Counter({k: v / total for k,v in cnts_dict.items()})

def ngrams_from_doc(doc, n):

	'''
	Takes an annotated processors.ds.Document 
	and returns its character ngrams of size n
	'''
	cnt = Counter()
	for word in doc.words:
			ngrams = character_ngrams(word, n)
			for gram in ngrams:
				cnt[gram] += 1
	return cnt

def diff_distributions(target_dist, background_dist):
	for k,v in background_dist.items():
		target_value = target_dist[k]
		if target_value > 0:
			difference = target_value - v
			target_dist[k] = difference if difference > 0 else 0
	# now normalize target
	return normalize(target_dist)

def create_morphological_rule(ngram_dist, label, top_n):
	"""
	Gus: instantiates a rule template from a character ngram distribution.
	"""
	sub_patterns = [k for k,v in ngram_dist.most_common(top_n)]
	rules = []
	for i, sub_pattern in enumerate(sub_patterns):
		with open("entity_template.yml") as in_file:
			rule_template = in_file.read()
		# this way we can evaluate the feature quality of each ngram from our distribution
		rule_name = "{}-{}".format(label.lower(), i + 1)
		rule = rule_template.format(
			name=rule_name,
			label=label,
			pattern="""[tag=/^NN/ & lemma=/{p}/]""".format(p=sub_pattern)
		)
		rules.append(rule)
	return "\n\n".join(rules)


