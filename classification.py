import sys
import orange, orngTest

data = orange.ExampleTable("features.tab")
l = orange.SVMLearner(data)
#l.nu = 0.1
#l.svm_type = orange.SVMLearner.Nu_SVC


print 'ranked: no'

correct = 0
for ex in data:
    print ex['id'], l(ex)
    

