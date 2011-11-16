from xml.etree.ElementTree import ElementTree

WORD_MATHCING_THRESHOLD = 0.60

preprocessed_data = parse_preprocessed_xml('rte2_dev_data/RTE2_dev.preprocessed.xml')
data = parse_xml('rte2_dev_data/RTE2_dev.xml')

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

# def lemma_matching(text, entailment, threshold):

    for 

    for word, lemma in preprocessed_data.values():
        


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

def parse_preprocessed_xml(fileh):
    tree = ElementTree()
    tree.parse(fileh)
    parsed = {}
    for pair in list(tree.findall('pair')):
        attrib = pair.attrib
        word = pair.find('word').text
        lemma = pair.find('lemma').text
        pos = pair.find('pos-tag').text
        parsed[attrib['id']] = (attrib, word, lemma, pos)
    return parsed

def traverse(tree, function, threshold):
    correct = 0
    for a,t,h in tree.values():
        c = a['entailment'] == 'YES'
        if function(t,h, threshold) == c:
            correct += 1
    print float(correct) / len(tree)


if __name__ == '__main__':

    traverse(data, word_matching, WORD_MATHCING_THRESHOLD)
