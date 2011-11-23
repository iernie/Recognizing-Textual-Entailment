from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse
from tree_edit_dist import *
from collections import defaultdict

DISTANCE_THRESHOLD = 0.565
IDF = dict()

class Pair(object):
    def __init__(self, etree):
        self.id = etree.attrib['id'].strip()
        self.task = etree.attrib['task'].strip()
        self.text = [Sentence(s) for s in etree.iterfind('text/sentence')]
        self.hypothesis = [Sentence(s) for s in etree.iterfind('hypothesis/sentence')]
        self.entailment = etree.attrib['entailment']

class Sentence(object): # list of nodes
    def __init__(self, etree):
        self.serial = etree.attrib['serial'].strip()
        self.nodes = [SentenceNode(n) for n in etree.iterfind('node')]

class SentenceNode(object):
    def __init__(self, etree):
        self.id = etree.attrib['id']
        self.parent = None
        if etree.findtext('relation'): self.parent = etree.find('relation').attrib['parent']
        
        if self.id[0] == 'E': # artificial node
            self.isWord = False
            self.lemma = etree.findtext('lemma')
            if self.lemma: self.lemma = self.lemma.strip()
        else:
            self.isWord = True
            self.word = etree.findtext('word').strip()
            self.lemma = etree.findtext('lemma').strip()
            self.postag = etree.findtext('pos-tag').strip()
            self.relation = etree.findtext('relation')
            if self.relation: self.relations = self.relation.strip()

def parse_preprocessed_xml(fileh):
    pair = None
    etree = xmlparse(fileh)
    pairs = []
    for pair in etree.iterfind('pair'):
        pairs.append(Pair(pair))
    return pairs
    
def calculate_tree_edit_dist(pair, function=unit_costs):
    text_trees = []
    for sentence in pair.text:
        text_trees += make_tree(sentence)
        
    hypothesis_trees = []
    for sentence in pair.hypothesis:
        hypothesis_trees += make_tree(sentence)
        
    T_node = Node("T")
    for tree in text_trees:
        T_node.append(tree)
        
    H_node = Node("H")
    for tree in hypothesis_trees:
        H_node.append(tree)
        
    return distance(T_node, H_node, function)
    
def calculate_tree_edit_dist_hypothesis(hypothesis):
    hypothesis_trees = []
    for sentence in hypothesis:
        hypothesis_trees += make_tree(sentence)

    H_node = Node("H")
    for tree in hypothesis_trees:
        H_node.append(tree)

    return distance(Node(""), H_node, unit_costs_ent)
    
def make_tree(sentence):
    hash_map = dict()
    root = []
    
    for node in sentence.nodes:
        if node.isWord:
            hash_map[node.id] = Node(node.lemma)
        else:
            hash_map[node.id] = Node(node.id)
    
    for node in sentence.nodes:
        if node.parent:
            hash_map[node.parent].append(hash_map[node.id])
        else:
            root.append(hash_map[node.id])
    
    return root
                
def unit_costs_ent(node1, node2):
    # insertion cost
    if node1 is None:
        return 1

    # deletion cost
    if node2 is None:
        return 0

    # substitution cost
    if node1.label != node2.label:
        return 1
    else:
        return 0
        
def unit_costs_idf(node1, node2):
    # insertion cost
    if node1 is None:
        return 1

    # deletion cost
    if node2 is None:
        return 0

    # substitution cost
    if node1.label != node2.label:
        return IDF[node1.label]
    else:
        return 0
        
def calculate_idf(data):
    
    IDF = defaultdict(int)
    
    for pair in data:
        for sentence in pair.text:
            for word in sentence.nodes:
                if word.isWord:
                    IDF[word.lemma.strip()] += 1
        
        for sentence in pair.hypothesis:
            for word in sentence.nodes:
                if word.isWord:
                    IDF[word.lemma] += 1
                    
    for key, value in IDF.items():
        IDF[key] = 1 / value
        
    return IDF
    
def build_word_match(data, IDF):
    
    word_match = dict()
    
    TH_count = 0
    H_count = 0
    
    hwords_in_t = []
    
    for pair in data:
        hwords = [x.lemma for s in pair.hypothesis for x in s.nodes if x.isWord]
        twords = [x.lemma for s in pair.text for x in s.nodes if x.isWord]
        hwords_in_t += filter(lambda x: x in twords, hwords)
        
        
if __name__ == '__main__':
    import sys
    data = parse_preprocessed_xml("rte2_dev_data/RTE2_dev.preprocessed.xml")
    DISTANCE_THRESHOLD = float(sys.argv[2])
    
    verdict_correct = 0
    
    print "ranked:no"
    
    IDF = calculate_idf(data)
    
    for pair in data:
        #print "Pair #", pair.id
        
        # II-a
        #d = calculate_tree_edit_dist(pair)
        #print "Distance between T-H pair is", d
        
        # II-b
        #d = calculate_tree_edit_dist(pair, unit_costs_ent)
        #cost_by_inserting = calculate_tree_edit_dist_hypothesis(pair.hypothesis)
        #div = (float(d) / float(cost_by_inserting))

        #if div < DISTANCE_THRESHOLD:
        #    if pair.entailment == "YES":
        #        verdict_correct += 1
        #    print pair.id, "YES"
        #else:
        #    if pair.entailment == "NO":
        #        verdict_correct += 1
        #    print pair.id, "NO"
            
        # II-c
        d = calculate_tree_edit_dist(pair, unit_costs_idf)
        cost_by_inserting = calculate_tree_edit_dist_hypothesis(pair.hypothesis)
        div = (float(d) / float(cost_by_inserting))

        if div < DISTANCE_THRESHOLD:
            if pair.entailment == "YES":
                verdict_correct += 1
            print pair.id, "YES"
        else:
            if pair.entailment == "NO":
                verdict_correct += 1
            print pair.id, "NO"
        
    #print
    #print "Correctness ", (verdict_correct / len(data))
        
        
        
        
        
        
        
