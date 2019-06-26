import pickle as pkl
import numpy as np

# A dictionary with relations
with open("./relations_dict", 'rb') as f:
    relations = pkl.load(f)
	
templates = dict()
templates['/r/RelatedTo'] = ["is related to {}", "has a certain connection with {}", "is kind of related to {}", "is linked to {}", "has some relationship with nine"]
templates['/r/IsA'] = ["is {}", "is an example of {}", "is a special case of {}", "is an instance of {}", "can be thought as an instance of {}", "could be considered to be an example of {}"]
templates['/r/PartOf'] = ["is a part of {}", "{} has as a part"]
templates['/r/HasA'] = ["has {} as a part", "has {} as its part"]
templates['/r/UsedFor'] = ["is sometimes used for {}", "could be used for {}", "may be used for {}", "may prove its utilitarian value in {}", "{} is its purpose", "has {} as its purpose"]
templates['/r/CapableOf'] = ["can {}", "is capable of {}", "can perform {}", "can do {}"]
templates['/r/Causes'] = ["can cause {}", "may causes {}", "may be a cause of {}", "may lead to {}"]
templates['/r/HasProperty'] = ["has a property that {}", "is characterizes by {}", "is {}"]
templates['/r/Desires'] = ["wants (if not craves) {}", "desires {}", "wants {}", "is craving (or, at least, wants)"]
templates['/r/Synonym'] = ["is a synonym for {}", "is synonimous to {}", "is essentially the same as {}", "has the same meaning as {}"]
templates['/r/Antonym'] = ["is an antonym for {}", "is antonymous to {}", "is the opposite of {}", "has a meaning opposite to {}", "has an opposite meaning to {}"]
templates['/r/DistinctFrom'] = ["is not the same as {}", "is distinct from {}"]
templates['/r/MannerOf'] = ["is a way of doing {}", "{} be could be done in this way"]
templates['/r/HasPrerequisite'] = ["in order for it to happen, {} needs to happen", "depends on {}", "that needs {} to happen"]
templates['/r/Implies'] = ["in order for it to happen, {} needs to happen", "depends on {}", "that needs {} to happen", "implies {}"]
templates['/r/SimilarTo'] = ["is very similar to {}", "is similar to {}", "has some similarity with {}", "it and {} are similar"]
templates['/r/InstanceOf'] = ["is {}", "is an example of {}", "is a special case of {}", "is an instance of {}", "can be thought as an instance of {}", "could be considered to be an example of {}"]



def get_hint(rel, source, target):
	
	return np.random.choice(templates[source]).format(target)
	
starters = ("It is a thing that ", "It is something that ", "This thing is such that ")
connectors = (" and such that ", ", such that ", ", such that also ", ", also, ", ", additionally, ", ". Moreover, this thing is such that ")

def sample_definition(word):
	
	message = np.random.choice(starters)

	relations = relations[word]
	num_properties = np.min(np.random.geometric(0.5), len(relations[word]))
	properties = np.random.choice(a, size=num_properties, replace=False)
	

	for p in properties:
		message += p

	message += "."


	return message
		
