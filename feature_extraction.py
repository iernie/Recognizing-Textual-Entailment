from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse

from bleu import bleu
from lemma_pos_matching import lemma_matching as lemma_pos
from lemma_matcing import lemma_matching
from word_matching import word_matching,parse_xml

import sys

class Pair(object):
    def __init__(self, etree):
        self.id = etree.attrib['id'].strip()
        self.tast = etree.attrib['task'].strip()
        self.text = [Sentence(s) for s in etree.iterfind('text/sentence')]
        self.hypothesis = [Sentence(s) for s in etree.iterfind('hypothesis/sentence')]
        self.entailment = etree.attrib['entailment']

class Sentence(object): # list of nodes
    def __init__(self, etree):
        self.serial = etree.attrib['serial'].strip()
        self.nodes = [Node(n) for n in etree.iterfind('node')]

class Node(object):
    def __init__(self, etree):
        self.id = etree.attrib['id']
        if self.id[0] == 'E': # artificial node
            self.isWord = False
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

def write(t):
    sys.stdout.write(str(t))
    sys.stdout.write("\t")

def matching_bigrams(text,hypothesis):
    def ngrams(stringlist, n):
        i = 0
        while i + n <= len(stringlist):
            yield tuple(stringlist[i:i+n])
            i += 1
    t = list(ngrams(text,2) )
    h = list(ngrams(hypothesis, 2))
    correct = 0
    for w in h:
        if w in t:
            correct += 1
    return correct / len(h)

def feature_extraction(data,data2):
    write('id')
    write('word')
    write('lemma')
    write('pos')
    write('bigrams')
    write('entailment')
    print
    print 'd\tc\tc\tc\tc\td'
    print 'meta\t\t\t\t\tclass'
    for pair in data: 
        write(pair.id)
        t = data2[pair.id][1]
        h = data2[pair.id][2]
        write(word_matching(t,h))
        write(lemma_matching(pair.text, pair.hypothesis))
        write(lemma_pos(pair.text, pair.hypothesis))
        write(matching_bigrams(t,h))
        write(data2[pair.id][0]['entailment'])
        print



if __name__ == '__main__':
    import sys
    data = parse_preprocessed_xml(sys.argv[1])
    data2 = parse_xml(sys.argv[2])
    feature_extraction(data,data2)
