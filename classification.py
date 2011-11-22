import sys
import orange, orngTest
import random

data = orange.ExampleTable("features.tab")
l = orange.BayesLearner(data)
#l.nu = 0.1
#l.svm_type = orange.SVMLearner.Nu_SVC

def split(data,n):
    i = 0
    while i < len(data):
        yield data[i:i+n]
        i += n

def cross_validation():
    k = 10
    d = list(data)
    nps = len(d) / 10
    acs = []
    for i in range(k):
        random.shuffle(d)
        subsamples = list(split(d,nps))
        accurancy = 0
        for j in range(k):
            validation = subsamples[j]
            training = []
            for s in subsamples:
                if s == validation: continue
                training += s
            l = orange.BayesLearner(training)
            thisa = 0
            for ex in validation:
                if ex.getclass() == l(ex):
                    thisa += 1
            accurancy += float(thisa) / len(validation)
        acs.append(accurancy)
    print sum(acs) / float(k) / float(k)

if __name__ == '__main__':
    import sys
    if 'cross' in sys.argv:
        cross_validation()
    else:
        print 'ranked: no'

        correct = 0
        for ex in data:
            print ex['id'], l(ex)
    

