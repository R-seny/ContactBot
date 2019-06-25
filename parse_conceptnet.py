import json
import os
from collections import defaultdict
import pickle as pkl
import settings

def getRelationDict():
    file_loc = "./conceptnet-assertions-5.6.0.csv"
	
	symmetric_rels = {'/r/RelatedTo', '/r/Synonym', '/r/Antonym', '/r/DistinctFrom',
					  '/r/SimilarTo', '/r/LocatedNear', '/r/EtymologicallyRelatedTo'}
	
	with open(file_loc, 'r') as f:
	
		R = defaultdict(lambda: [])
	
		for i, line in enumerate(f):
	
			if not i % 1000000:
				print("Processed {} lines".format(i))
			
			elements = line.split(sep='\t')
			if len(elements) != 5:
				continue
	
			rel, source, target, js  = elements[1:5]
	
			lang_source, source_w = source.split('/')[2:4]
			lang_target, target_w = target.split('/')[2:4]
	
			if rel in ['/r/RelatedTo', '/r/FormOf', '/r/IsA', '/r/PartOf', '/r/HasA', '/r/UsedFor', '/r/CapableOf', '/r/Causes', '/r/HasProperty', '/r/Desires', '/r/Synonym', '/r/Antonym', '/r/DistinctFrom', '/r/Entails', '/r/SimilarTo', '/r/InstanceOf']:
				for start in ['the ', 'an ', 'a ']:
					if source_w.startswith(start):
						source_w = source_w[len(start):]
					if target_w.startswith(start):
						target_w = target_w[len(start):]
						
				if lang_source == "en" and lang_target == "en":
					
					R[source_w].add((rel, target_w))
	
					if rel in symmetric_rels:
					
						R[target_w].add((rel, source_w))

		for k in R:
			R[k] = list(R[k])
	
	with open(file_loc, 'wb') as f:
		pkl.dump(dict(R), f)
