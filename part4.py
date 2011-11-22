from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse

from nltk.corpus import wordnet as wn
from collections import defaultdict
import math

#preprocessed_data = parse_preprocessed_xml('rte2_dev_data/RTE2_dev.preprocessed.xml')
#data = parse_xml('rte2_dev_data/RTE2_dev.xml')

def classifier(text,hypothesis):
    hypwords = [n.synonyms for s in hypothesis
                           for n in s.nodes
                           if n.isWord]
    candidates = {}
    candimdict = defaultdict(list)
    
    for s_num, sentence in enumerate(text):
        for n_num, word in enumerate(sentence.nodes):
            if not word.isWord: continue
            for synset in word.synonyms:
                for h_num,hynsynsets in enumerate(hypwords):
                    ps = [(i,synset.path_similarity(x)) for i,x in enumerate(hynsynsets)]
                    for i,x in ps:
                        if x:
                            candimdict[h_num].append(x)
    notsinhyp = sum([1 for s in hypothesis
                       for n in s.nodes
                       if n.isWord and n.lemma == 'not'])
    notsintext = sum([1 for s in text
                       for n in s.nodes
                       if n.isWord and n.lemma == 'not'])
    synonymmatch = 0
    #print candimdict
    for k in candimdict:
        synonymmatch += math.log(max(candimdict[k]))
    synonymmatch /= len(hypwords)
    #print candimdict
    return (notsinhyp,notsintext,synonymmatch)
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
            self.word = etree.findtext('word').strip().lower()
            self.lemma = etree.findtext('lemma').strip().lower()
            self.postag = etree.findtext('pos-tag').strip().lower()
            self.relation = etree.findtext('relation')
            self.synonyms = self._synonyms()
            self.wnbase = self._wnbase()
            if self.relation: self.relations = self.relation.strip()
    def _synonyms(self):
        try:
            return wn.synsets(self.lemma, pos=self.postag)    
        except:
            return []
    def _wnbase(self):
        if self.postag == 'n':
            return wn.morphy(self.lemma, wn.NOUN)
        elif self.postag == 'v':
            return wn.morphy(self.lemma, wn.VERB)
        elif self.postag == 'a':
            return wn.morphy(self.lemma, wn.ADJ)
        return None

def parse_preprocessed_xml(fileh):
    pair = None
    etree = xmlparse(fileh)
    pairs = []
    for pair in etree.iterfind('pair'):
        pairs.append(Pair(pair))
    return pairs



def traverse_preprocessed_out(pairs, function):
    correct = 0
    print "ranked: no"    
    for pair in pairs:
        print pair.id,
        if function(pair.text, pair.hypothesis):
            print 'YES'
        else:
            print 'NO'
        print pair.entailment
        break

def traverse_preprocessed_val(pairs, function):
    correct = 0
    print "id\ta\tb\tc\tentailment"
    print "d\td\td\tc\td"
    print "meta\t\t\t\tclass"
    for pair in pairs:
        c = pair.entailment == 'YES'
        r = function(pair.text, pair.hypothesis)
        #if r == c:
        #    print 'r',c,r
        #    correct += 1
        #else:
        #    print 'f',c,r
        print "%s\t%d\t%d\t%f\t%s"%(pair.id,r[0], r[1], r[2], pair.entailment)
    #print correct / len(pairs)

if __name__ == '__main__':
    import sys
    data = parse_preprocessed_xml(sys.argv[1])
    traverse_preprocessed_val(data, classifier)
