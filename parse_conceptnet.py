import json
import os
from collections import defaultdict
import pickle as pkl

def getRelationDict():
    file_loc = "./conceptnet-assertions-5.6.0.csv"

    symmetric_rels = {'/r/RelatedTo', '/r/Synonym', '/r/Antonym', '/r/DistinctFrom',
                      '/r/SimilarTo', '/r/LocatedNear', '/r/EtymologicallyRelatedTo'}

    with open(file_loc, 'r') as f:

        R = defaultdict(lambda: defaultdict(lambda: set()))

        for i, line in enumerate(f):

            if not i % 1000000:
                print("Processed {} lines".format(i))

            elements = line.split(sep='\t')
            if len(elements) != 5:
                continue

            rel, source, target, js  = elements[1:5]

            lang_source, source_w = source.split('/')[2:4]
            lang_target, target_w = target.split('/')[2:4]

            source_w = " ".join(source_w.split("_"))
            target_w = " ".join(target_w.split("_"))

            if rel in ['/r/RelatedTo', '/r/IsA', '/r/PartOf', '/r/HasA', '/r/UsedFor', '/r/CapableOf', '/r/Causes', '/r/HasProperty', '/r/Desires', '/r/Synonym', '/r/Antonym', '/r/Entails', '/r/DistinctFrom', '/r/MannerOf', '/r/HasPrerequisite', '/r/SimilarTo', '/r/InstanceOf']:
                # for start in ['the ', 'an ', 'a ']:
                #     if source_w.startswith(start):
                #         source_w = source_w[len(start):]
                #     if target_w.startswith(start):
                #         target_w = target_w[len(start):]

                if lang_source == "en" and lang_target == "en":

                    R[source_w][rel].add(target_w)

                    if rel in symmetric_rels:

                        R[target_w][rel].add(source_w)

        for w in R:
            R[w] = dict(R[w])

            for r in R[w]:
                R[w][r] = list(R[w][r])

        with open("./relations_dict", 'wb') as f:
            pkl.dump(dict(R), f)

getRelationDict()