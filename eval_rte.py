#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Evaluate system's entailment predictions against human entailment judgements,
printing the accuracy score.
"""

# EM - 4/11/11

from xml.etree.cElementTree import iterparse


def evaluate(ref_fname, pred_fname):
    """
    Evaluate entailment predictions by comparing with human entailment
    judgements. Return accuracy score.
    """
    ref_id2label = parse_reference(ref_fname)
    pred_id2label = parse_predictions(pred_fname)
    assert len(ref_id2label) == len(pred_id2label)
    
    correct = [ id for id, label in ref_id2label.iteritems()
                if pred_id2label[id] == label ]
    
    accuracy = len(correct) / float(len(ref_id2label))
    
    return accuracy
    

def parse_reference(inf):
    """
    Read entailment reference form data file in RTE xml format including
    entailment judgements. Return a dict mapping pair id to entailment
    annotation.
    """
    id2label = {}

    for event, elem in iterparse(inf):
        if elem.tag == "pair":
            id2label[elem.get("id")] = elem.get("entailment")
            
    return id2label


def parse_predictions(inf):
    """
    Read entailment predictions from file containing entailment predictions in
    RTE output format. Return a dict mapping pair id to entailment prediction.
    """
    # first line as well as ranking are currently ignored,
    # because we are not computing Average Precision
    if isinstance(inf, basestring):
        inf = open(inf)
        
    # how NOT to use Python ;-)
    return dict(pair.split() for pair in inf.read().strip().split("\n")[1:])
        
    

    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    
    parser.add_argument(
        "ref_fname", 
        metavar="REFERENCE",
        help="data file in RTE xml format including entailment judgements")
    
    parser.add_argument(
        "pred_fname", 
        metavar="PREDICTION",
        help="file containing entailment predictions in RTE output format")

    args = parser.parse_args()
    
    print "Accuracy = %.4f" % evaluate(args.ref_fname, args.pred_fname)