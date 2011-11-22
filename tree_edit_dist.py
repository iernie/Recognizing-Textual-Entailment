#!/usr/bin/env python
# -*- coding: utf-8 -*-
    
"""
Sample implementation of tree edit distance algorithm from 
Kaizhong Zhang & Dennis ShaSha, 
"Simple fast algorithms for the editing distance beteen trees and related problems",
SIAM Journal on Computing, Vol. 18, No. 6, pp. 1245-1262, 1989.

This is a fairly literal translation of the algorithm described in the paper.
It can probably be improved in several ways, e.g., by avoiding recursion in
the preprocessing.
"""

# EM - 11/2011


class Node(list):
    """
    Simple recursive representation of a tree as a labeled node with zero or
    more child nodes
    """

    def __init__(self, label, *children):
        self.label = label
        list.__init__(self, children)
        
    def is_leaf(self):
        return not self
    
    def left_child(self):
        return self[0]

    def __str__(self):
        """
        string representation of tree as a labeled bracket structure
        """
        if self.is_leaf():
            return self.label
        else:
            return ( self.label + 
                     "( " + 
                     " ".join([str(child) for child in self]) + 
                     ")" )
        
    def __repr__(self):
        return self.label
        
    
class ForestDist(dict):
    """
    ForestDist is a dictionary storing the distance between two forest.

    Keys are tuples of the form (forest1, forest2)

    forest1 is either a tuple (i1,j2) where
    i1 = start index of source forest1 and
    j1 = end index of source forest1,
    or None (i.e. empty forest)
    
    Likewise forest2 is eitehr a tuple (i2,j2) where 
    i2 = start index of target forest2 and
    j2 = end index of target forest2,
    or None (i.e. empty forest).
    
    Values are distances >= 0.
    
    By definition, 
    ForestDist(None,None) = 0 and
    forest (i,j) = None when i>j.
    """
    
    def __init__(self,*args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        # forestdist(Ø,Ø) = 0
        # (cf. Zhang & Shasha:p.1253)
        self[None,None] = 0
        
    def __getitem__(self, (forest1, forest2)):
        # If i>j, then T[i..j] = 0
        # (cf. Zhang & Shasha:p.1249)
        if forest1 is not None:
            i1, j1 = forest1
            if i1 > j1:
                forest1 = None
                
        if forest2 is not None:
            i2, j2 = forest2
            if i2 > j2:
                forest2 = None
                
        return dict.__getitem__(self, (forest1, forest2))
                
        
        
def unit_costs(node1, node2):
    """
    Defines unit cost for edit operation on pair of nodes,
    i.e. cost of insertion, deletion, substitution are all 1
    """
    # insertion cost
    if node1 is None:
        return 1
    
    # deletion cost
    if node2 is None:
        return 1
    
    # substitution cost
    if node1.label != node2.label:
        return 1
    else:
        return 0

    
def postorder(root_node):
    """
    Return a list of nodes resulting from a left-to-right postorder traversal
    of the tree rooted in root_node
    """
    # Cf.  Zhang & Shasha:p.1249:
    # "Let T[I] be the ith node in the tree according to the left-to-right
    # postordering"
    
    tree = list()
    tree.append(root_node)
    traversed_tree = list()
    
    while len(tree) > 0:
        node = tree.pop()
        for child in node:
            tree.append(child)
        traversed_tree.insert(0, node)
    
    return traversed_tree
    
    
    
def leftmost_leaf_descendant_indices(node_list):
    """
    Return a list of the *indices* of the leftmost leaf descendants according
    to a list of post-ordered nodes
    """
    # Cf.  Zhang & Shasha:p.1249:
    # "l(i) is the number of the leftmost leaf descendant of the subtree
    # rooted at T[i]. When T[i] is a leaft, l(i)=i."
    
    lld = list()
    tree = list()
    
    for child in node_list:
        tree.insert(0, child)
    
    while len(tree) > 0:
        node = tree.pop()
        if node.is_leaf():
            lld.append(list_index(node_list, node))
        else:
            tree.append(node.left_child())
    
    return lld
    
def list_index(my_list, my_element):
    i = 0
    for element in my_list:
        i += 1
        if element is my_element:
            return i
    
        
def key_root_indices(lld_indices):
    """
    Return a list of the *indices* of the key roots from a list of the indices
    of the leftmost leaf descendants
    """
    # Cf. Zhang & Shasha:p.1251: "LR_keyroots(T) = {k| there exists no k'>k
    # such that l(k)=l(k')}
    
    kr = dict()
    
    i = 1
    for lld in lld_indices:
        kr[lld] = i
        i += 1
    
    return sorted(kr.values())
    
    
def distance(t1, t2, costs=unit_costs):
    """
    Compute edit distance between tree t1 and tree t2
    Unit costs are used if no explicit costs are provided.
    """
    # Cf. Zhang & Shasha:p.1252-1253

    # Use an embedded function, so T1,T2, l1,l2, and TD are available from the
    # name space of the outer function and don't need to be dragged around in
    # each function call
    def edit_dist(i, j):
        """
        compute edit distance between two subtrees rooted in nodes i and j
        respectively
        """
        # temporary array for forest distances
        FD = ForestDist()
        
        for n in range(l1[i], i):
            FD[ (l1[i],n), None ] = ( FD[ (l1[i],n-1), None ] + 
                                      costs(T1[n], None) )
            
        for m in range(l2[j], j):
            FD[ None, (l2[j],m) ] = ( FD[ None, (l2[j],m-1) ] + 
                                      costs(None, T2[m]) )
            
        for n in xrange(l1[i], i):
            for m in xrange(l2[j], j):
                if l1[n] == l1[i] and l2[m] == l2[j]:
                    FD[((l1[i], n), (l2[j], m))] = min(
                        (
                            FD[ (l1[i],n-1), (l2[j], m)] +
                            costs(T1[n], None)
                        ),
                        (
                            FD[ (l1[i],n), (l2[j], m-1)] +
                            costs(None, T2[m])
                        ),
                        (
                            FD[ (l1[i],n-1), (l2[j], m-1)] +
                            costs(T1[n], T2[m])
                        )
                    )
                    TD[n, m] = FD[((l1[i], n), (l2[j], m))]
                else:
                    FD[((l1[i], n), (l2[j], m))] = min(
                        (
                            FD[ (l1[i],n-1), (l2[j], m)] +
                            costs(T1[n], None)
                        ),
                        (
                            FD[ (l1[i],n), (l2[j], m-1)] +
                            costs(None, T2[m])
                        ),
                        (
                            FD[ (l1[i],n-1), (l2[j], m-1)] +
                            TD[n, m]
                        )
                    )
                    
        return TD[i, j]
    
    
    # Compute T1[] and T2[]
    T1 = postorder(t1)
    T2 = postorder(t2)
    
    # Compute l()
    l1 = leftmost_leaf_descendant_indices(T1)
    l2 = leftmost_leaf_descendant_indices(T2)
    
    # LR_keyroots1 and LR_keyroots2
    kr1 = key_root_indices(l1)
    kr2 = key_root_indices(l2)
    
    # permanent treedist array
    TD = dict()
    
    for i in range(len(T1)):
        for j in range(len(T2)):
            TD[i, j] = 0

    for i in kr1:
        for j in kr2:
            edit_dist(i-1, j-1)
            
    print_matrix(T1, T2, TD)
    
    return TD[i-1,j-1]
            
    
        
def print_matrix(T1, T2, TD):
    print "   " + "".join([("%-3s" % n.label) for n in T2])
    for i in range(len(T1)):
        print "%-2s" % T1[i].label,
        for j in range(len(T2)):
            print "%-2s" % TD[i,j],
        print
    print

    
if __name__ == '__main__':
    # Cf. Zhang & Shasha: Fig. 4 and Fig. 8
    
    t1 = Node("f",
             Node("d",
                  Node("a"),
                  Node("c",
                       Node("b"))),
             Node("e"))
    

    
    t2 = Node("f",
              Node("c",
                   Node("d",
                        Node("a"),
                        Node("b"))),
              Node("e"))

    print "t1 =", t1    
    print "t2 =", t2
    print
    
    d = distance(t1, t2) 
    print "distance =", d


