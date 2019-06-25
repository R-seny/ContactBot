import pickle as pkl
	
templates = dict()
templates['/r/RelatedTo'] = ["is related to {}", "has a certain connection with {}", "kind of related to {}"]

def get_hint(rel, source, target):
	
	return np.random.choice(templates[rel]).format(target)
	
def sample_definition(word):
	
	raise NotImplementedError()
	