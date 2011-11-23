from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse

from nltk.corpus import wordnet as wn
from collections import defaultdict
import math

from lemma_pos_matching import lemma_matching
import sys
import numpy as np
#preprocessed_data = parse_preprocessed_xml('rte2_dev_data/RTE2_dev.preprocessed.xml')
#data = parse_xml('rte2_dev_data/RTE2_dev.xml')
THRESHOLD = 0.5

def word_similar(tn, hn):
    if tn.lemma == hn.lemma:
        return True
    else:
        for syn in tn.synonyms:
            for hsyn in hn.synonyms:
                if syn.path_similarity(hsyn) > THRESHOLD:
                    return True
    # hypernyms_for_h = list(y for s in hn.synonyms for x in s.hypernym_paths() for y in x)
    # if hypernyms_for_h:
    #     hypernyms_for_t = list(y for s in tn.synonyms for x in s.hypernym_paths() for y in x)
    #     for a in hypernyms_for_h:
    #         for b in hypernyms_for_t:
    #             if a.path_similarity(b) > THRESHOLD:
    #                 #print a,b
    #                 #print 'tn',tn
    #                 #print 'hn',hn
    #                 #sys.exit()
    #                 return True
    #     

    return False

def type_r(rs, node):
    if not node.children: return None
    for r in rs:
        if r in node.childrendict:
            return node.childrendict[r]
    for cn in node.children:
        t = type_r(rs,cn)
        if t: return t
    return None

frequently_used = []
usage = defaultdict(int)

def classifier(pair):
    verbs_hypothesis = [x for s in pair.hypothesis for x in s.nodes if x.postag=='v']
    verbs_text = [x for s in pair.text for x in s.nodes if x.postag=='v']
    
    be_hypothesis = [x for s in pair.hypothesis for x in s.nodes if x.postag=='vbe']
    verbs_hypothesis += be_hypothesis
    #be_text = [x for s in pair.text for x in s.nodes if x.postag=='vbe']
    #print be_hypothesis
    
    overlap = defaultdict(list)
    for i,vh in enumerate(verbs_hypothesis):
        for j,vb in enumerate(verbs_text):
            if word_similar(vh,vb):
                overlap[i].append(j)
            if vh.postag == 'vbe':
                overlap[i].append(j)
    #print overlap, verbs_hypothesis, verbs_text
    #print overlap

    overlap_txx = 0
    presence_correct = True
    modstatus = True
    for i,cand in overlap.items():
        for j in cand:
            objhyp = type_r(['obj','obj1'], verbs_hypothesis[i])
            subhyp = type_r(['s','subj'], verbs_hypothesis[i]) 

            objtex = type_r(['obj','obj1'], verbs_text[j])
            subtex = type_r(['s','subj'], verbs_text[j]) 


            if subhyp and subtex:
                if word_similar(subhyp, subtex):
                    overlap_txx += 1

                    if modstatus:
                        mod_h = type_r(['mod'], verbs_hypothesis[i])
                        mod_t = type_r(['mod'], verbs_text[j])
                        if mod_h and mod_t:
                            pcomp_h = type_r(['pcomp-n'], mod_h)
                            pcomp_t = type_r(['pcomp-n'], mod_t)
                            if pcomp_h and pcomp_t:
                                if not word_similar(pcomp_h, pcomp_t):
                                    modstatus = False
                            #print pcomp_h, pcomp_t
            if objhyp and objtex:
                if word_similar(objhyp, objtex):
                    overlap_txx += 1
                    if modstatus:
                        mod_h = type_r(['mod'], verbs_hypothesis[i])
                        mod_t = type_r(['mod'], verbs_text[j])
                        if mod_h and mod_t:
                            pcomp_h = type_r(['pcomp-n'], mod_h)
                            pcomp_t = type_r(['pcomp-n'], mod_t)
                            if pcomp_h and pcomp_t:
                                if not word_similar(pcomp_h, pcomp_t):
                                    modstatus = False
                            #print pcomp_h, pcomp_t

            if presence_correct:
                be_h = type_r(['be'], verbs_hypothesis[i])
                be_t = type_r(['be'], verbs_text[j])
                if be_h and be_t:
                    if be_h.word != be_t.word:
                        presence_correct = False
            
    #print verbs_hypothesis
    synonym_match = 0
    hypothesis = [x for s in pair.hypothesis for x in s.nodes if x.isWord and x.lemma not in frequently_used]
    #print hypothesis, len(hypothesis)
    text = [x for s in pair.text for x in s.nodes if x.isWord and x.lemma not in frequently_used]
    for h_w in hypothesis:
        for t_w in text:
            if word_similar(h_w, t_w):
                synonym_match += 1
                break
            #synonym_match += word_similar(h_w, t_w) 
    #print frequently_used
    synonym_match = synonym_match / len(hypothesis) 

    return (presence_correct,overlap_txx>1, modstatus, synonym_match**2, 0)

def update_use(text):
    global usage, frequently_used
    text = [x.lemma for s in text for x in s.nodes if x.isWord]
    for word in text:
        if word == 'not': continue
        if word == 'non': continue
        usage[word] += 1
    tmp = sorted(usage.items(), key=lambda x: x[1], reverse=True)

    frequently_used = []
    for w,dummy in tmp[:20]:
        frequently_used.append(w)



class Pair(object):
    def __init__(self, etree):
        self.id = etree.attrib['id'].strip()
        self.tast = etree.attrib['task'].strip()
        self.text = [Sentence(s) for s in etree.iterfind('text/sentence')]
        update_use(self.text)
        self.hypothesis = [Sentence(s) for s in etree.iterfind('hypothesis/sentence')]
        if 'entailment' in etree.attrib:
            self.entailment = etree.attrib['entailment']
        else:
            self.entailment = None
        self.texttree = Node2('text_root')
        for s in self.text:
            for root in s.roots:
                self.texttree.children.append(root)
        self.hyptree = Node2('hyp_root')
        for s in self.hypothesis:
            for root in s.roots:
                self.hyptree.children.append(root)

class Sentence(object): # list of nodes
    def __init__(self, etree):
        self.serial = etree.attrib['serial'].strip()
        self.noded = {}
        for n in etree.iterfind('node'):
            node = Node(n)
            self.noded[node.id] = node
        self.nodes = self.noded.values()
        self.roots = []
        for n in self.nodes:
            if not n.relation:
                self.roots.append(n)
            else:
                n.parent = self.noded[n.parentid]
                n.parent.appendChild(n)

class Node2(object):
    def __init__(self, id):
        self.id = id
        self.children = []
        self.parent = None
        self.isWord = False
    def __repr__(self):
        c = ", ".join(repr(x) for x in self.children)
        return "<Node2(%s)>"%c

class Node(object):
    def __init__(self, etree):
        self.id = etree.attrib['id']
        if self.id[0] == 'E': # artificial node
            self.isWord = False
            self.postag = etree.findtext('pos-tag').strip().lower()
            self.relation = etree.findtext('relation')
            if self.relation:
                self.relation = self.relation.strip()
                self.parentid = etree.find('relation').attrib['parent']
            
            self.lemma = etree.findtext('lemma')
            if self.lemma:
                self.lemma = self.lemma.strip().lower()
                self.synonyms = self._synonyms()
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
                self.parentid = etree.find('relation').attrib['parent']
        self.parent = None
        self.children = []
        self.childrendict = {}
    def appendChild(self,x):
        self.children.append(x)
        self.childrendict[x.relation] = x
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
        c = ", ".join(repr(x) for x in self.children)
        if self.lemma:
            return "Node(lemma=%s :: %s)"%(self.lemma,c)
        else:
            return "Node(id=%s :: %s)"%(self.id,c)
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
    print "id\ta\tc\tb\tq\tp\tentailment"
    print "d\td\td\td\tc\td\td"
    print "meta\t\t\t\t\t\tclass"
    for pair in pairs:
        #c = pair.entailment == 'YES'
        sys.stderr.write("%s\n"% pair.id)
        r = function(pair)
        # if pair.id == "190":
        #     break
        #if r == c:
        #    print 'r',c,r
        #    correct += 1
        #else:
        #    print 'f',c,r
        print "%s\t%s\t%s\t%s\t%f\t%d\t%s"%(pair.id,r[0], r[1], r[2],r[3],r[4],pair.entailment)
    #print correct / len(pairs)

if __name__ == '__main__':
    import sys
    data = parse_preprocessed_xml(sys.argv[1])
    traverse_preprocessed_val(data, classifier)
