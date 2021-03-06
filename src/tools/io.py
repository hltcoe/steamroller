from concrete.util.file_io import CommunicationReader
import gzip
import codecs
import os.path
import logging
import numpy


logging.basicConfig(level=logging.INFO)


writer = codecs.getwriter("utf-8")
reader = codecs.getreader("utf-8")


def read_data(data_file, num_file, tag_type, of_interest=None):
    conc = data_file.endswith("tgz")
    nums = set()
    with gzip.open(num_file) as ifd:
        for n in ifd:
            nums.add(int(n.rstrip(b"\n")))
    items = []
    ifd = CommunicationReader(data_file) if conc else reader(gzip.open(data_file))
    for n, item in enumerate(ifd):
        if n in nums:
            if conc:
                text = item[0].text.lower()
                cid = item[0].id                
                labels = [t for t in item[0].communicationTaggingList if
                          t.taggingType == tag_type][0].tagList
                label = "_".join(sorted(labels))
            else:
                cid, label, text = item.rstrip("\n").split("\t")
            items.append((cid, label, text))
    logging.info("Read %d Communications", len(items))
    return items

def write_probabilities(data, output_file):
    """
    data = {"ID" : ("GOLD", {"LAB1" : logprob, ... })
    }    
    """
    codes = set()
    for i, (gold, probs) in data.items():
        for l in probs.keys():
            codes.add(l)
    codes = sorted(codes)
    with writer(gzip.open(output_file, "w")) as ofd:
        ofd.write("\t".join(["DOC", "GOLD"] + codes) + "\n")
        for cid, (label, probs) in data.items():
            #print(probs)
            ofd.write("\t".join([cid, label] + [str(probs.get(c, float("-inf"))) for c in codes]) + "\n")
            #norm = numpy.logaddexp.reduce(probs.values())
            #ofd.write("\t".join([cid, label] + [str(probs.get(c, float("-inf")) - norm) for c in codes]) + "\n")
    

def get_count(data_file):
    conc = data_file.endswith("tgz")
    ifd = CommunicationReader(data_file) if conc else reader(gzip.open(data_file))
    n = 0
    for c, _ in enumerate(ifd):
        n += 1
    logging.info("File %s contains %d Communications", data_file, n)
    return n


def extract_character_ngrams(text, n):
    stack = ["NULL" for _ in range(n)]
    ngrams = {}
    for c in text:
        stack = stack[1:]
        stack.append(c)
        ngrams[tuple(stack)] = ngrams.get(tuple(stack), 0) + 1
    return list(ngrams.items())
