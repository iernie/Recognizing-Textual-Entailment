from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse

from nltk.corpus import wordnet as wn
from collections import defaultdict
import math

import sys
#preprocessed_data = parse_preprocessed_xml('rte2_dev_data/RTE2_dev.preprocessed.xml')
#data = parse_xml('rte2_dev_data/RTE2_dev.xml')


def classifier(text,hypothesis):
    hypothesis = [x for s in hypothesis for x in s.nodes if x.isWord and x.postag != 'u']
    textunwrap = [x for s in text for x in s.nodes if x.isWord]
    #print hyphypernyms
    #print hypwords
    candidates = {}
    candimdict = defaultdict(list)

    # for i,antonym in enumerate(hypants):
    #     for word in textunwrap:
    #         for syn in word.synonyms:
    #             if syn.path_similarity(antonym.synset) > 0.9:
    #                 if antonym.name in [x.lemma for x in textunwrap]:
    #                     continue
    #                 print antonym, word,syn
    #                 sys.exit()
    
    for s_num, sentence in enumerate(text):
        for n_num, word in enumerate(sentence.nodes):
            if not word.isWord: continue
            if word.postag == 'u': continue
            for synset in word.synonyms:
                for h_num,hypoi in enumerate(hypothesis):
                    ps = [synset.path_similarity(x) for x in hypoi.synonyms]
                    for i,x in enumerate(ps):
                        if x and text[s_num].nodes[n_num].postag == hypothesis[h_num].postag:
                            candimdict[h_num].append(x)

    notsinhyp = sum([1 for n in hypothesis
                       if (n.lemma == 'not' or n.lemma == 'non')])
    notsintext = sum([1 for s in text
                       for n in s.nodes
                       if n.isWord and (n.lemma == 'not' or n.lemma == 'non')])

    
    synonymmatch = 0
    #print candimdict
    for k in candimdict:
        synonymmatch -= math.log(max(candimdict[k]))
    #sys.stderr.write(str(hypothesis))
    #sys.stderr.write("\n")
    synonymmatch /= len(hypothesis)
    #print candimdict
    return (abs(notsinhyp-notsintext),synonymmatch,0)

class Pair(object):
    def __init__(self, etree):
        self.id = etree.attrib['id'].strip()
        self.tast = etree.attrib['task'].strip()
        self.text = [Sentence(s) for s in etree.iterfind('text/sentence')]
        self.hypothesis = [Sentence(s) for s in etree.iterfind('hypothesis/sentence')]
        if 'entailment' in etree.attrib:
            self.entailment = etree.attrib['entailment']
        else:
            self.entailment = None

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
            #self.antonyms = self._antonyms()
            self.hypernyms = self._hypernyms()
            if self.relation:
                self.relation = self.relation.strip()
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
    def __repr__(self):
        return "Node(%s)"%self.lemma
    def _antonyms(self):
        try:
            return wn.lemma("%s.%s.1.%s"%(self.wnbase,
                self.postag,
                self.lemma)).antonyms()
        except:
            return []
    def _hypernyms(self):
        hypernyms = []
        for syn in self.synonyms:
            hypernyms += syn.hypernyms()
        return hypernyms
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
    print "id\ta\tc\tb\tentailment"
    print "d\td\tc\tc\td"
    print "meta\t\t\t\tclass"
    for pair in pairs:
        #c = pair.entailment == 'YES'
        #print pair.id
        r = function(pair.text, pair.hypothesis)
        #if r == c:
        #    print 'r',c,r
        #    correct += 1
        #else:
        #    print 'f',c,r
        print "%s\t%d\t%f\t%d\t%s"%(pair.id,r[0], r[1], r[2],pair.entailment)
    #print correct / len(pairs)

if __name__ == '__main__':
    import sys
    data = parse_preprocessed_xml(sys.argv[1])
    traverse_preprocessed_val(data, classifier)
