from xml.etree.ElementTree import ElementTree
from xml.etree.cElementTree import parse as xmlparse

WORD_MATHCING_THRESHOLD = 0.60
LEMMA_MATHING_TRESHOLD = 0.635

#preprocessed_data = parse_preprocessed_xml('rte2_dev_data/RTE2_dev.preprocessed.xml')
#data = parse_xml('rte2_dev_data/RTE2_dev.xml')

def word_matching(text, entailment, threshold):
    words = text.split()
    hwords = entailment.split()
    intext = 0
    for h in hwords:
        if h in words:
            intext += 1

    p = float(intext) / len(hwords)
    if p > threshold:
        return True
    else:
        return False

        
def lemma_matching(text, hypothesis, threshold):
    lemmastext = [(n.lemma, n.postag) for s in text for n in s.nodes if n.isWord]
    lemmashyp = [(n.lemma, n.postag) for s in hypothesis for n in s.nodes if n.isWord]
    hypintext = filter(lambda x: x in lemmastext, lemmashyp)
    p = float(len(hypintext)) / len(lemmashyp)
    if p > threshold:
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

def parse_preprocessed_xml(fileh):
    pair = None
    etree = xmlparse(fileh)
    pairs = []
    for pair in etree.iterfind('pair'):
        pairs.append(Pair(pair))
    return pairs


def traverse(tree, function, threshold):
    correct = 0
    for a,t,h in tree.values():
        c = a['entailment'] == 'YES'
        if function(t,h, threshold) == c:
            correct += 1
    print float(correct) / len(tree)

def traverse_preprocessed(pairs, function, threshold):
    correct = 0
    
    for pair in pairs:
        c = pair.entailment == 'YES'
        if function(pair.text, pair.hypothesis, threshold) == c:
            correct += 1
    print float(correct) / len(pairs)


if __name__ == '__main__':
    data =parse_preprocessed_xml("rte2_dev_data/RTE2_dev.preprocessed.xml")
    traverse_preprocessed(data, lemma_matching, LEMMA_MATHING_TRESHOLD) 
    #traverse(data, word_matching, WORD_MATHCING_THRESHOLD)
