from __future__ import division
from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse



def clean(word):
    return word.strip(",. ")
    

def bleu(text, entailment, threshold):
    def ngrams(stringlist, n):
        i = 0
        while i + n <= len(stringlist):
            yield tuple(stringlist[i:i+n])
            i += 1
    words = [clean(x) for x in text.lower().split()]
    hwords = [clean(x) for x in entailment.lower().split()]
    bleus = 0
    for N in range(1,1+len(hwords)):
        wn = list(ngrams(words,N))
        hn = list(ngrams(hwords,N))
        cm = filter(lambda x: x in wn, hn)
        bleus += len(cm) / len(hn)
    bleus /= len(hwords)
    if bleus > threshold:
        return True
    else:
        return False




def parse_xml(fileh):
    tree = ElementTree()
    tree.parse(fileh)
    parsed = {}
    for pair in list(tree.findall('pair')):
        attrib = pair.attrib
        t = pair.find('t').text
        h = pair.find('h').text
        parsed[attrib['id']] = (attrib,t,h)
    return parsed


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


def traverse(tree, function, threshold):
    print "ranked: no"
    for i,(a,t,h) in tree.items():
        #c = a['entailment'] == 'YES'
        print i,
        if function(t,h, threshold):
            print 'YES'
        else:
            print 'NO'


if __name__ == '__main__':
    import sys
    data = parse_xml(sys.argv[1])
    traverse(data, bleu, float(sys.argv[2]))
