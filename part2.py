from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse
from tree_edit_dist import *

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
    
def calculate_tree_edit_dist(pair):
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
        
    d = distance(T_node, H_node)
    print "Distance between T-H pair is", d
    
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
                


if __name__ == '__main__':
    data = parse_preprocessed_xml("rte2_dev_data/RTE2_dev.preprocessed.xml")
    for pair in data:
        print pair.id
        calculate_tree_edit_dist(pair)
        print