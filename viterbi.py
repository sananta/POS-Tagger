#Srivarshini Ananta
#2/13/18
#I have modified this code to create a trigram viterbi with backoff model

import sys
import re
import math
import itertools
from pprint import pprint
from collections import *


INIT_STATE = 'init'
FINAL_STATE = 'final'
OOV_SYMBOL = 'OOV'

hmmfile = sys.argv[1] 

tags = set() # i.e. K in the slides, a set of unique POS tags
trans = {} # transitions
bitrans = {} # bigram transitions 
emit_values = {} 
tag_values = defaultdict(int) 
voc = {} # encountered words

"""
This part parses the my.hmm file you have generated and obtain the transition and emission values.
"""
with open(hmmfile) as hmmfile:
    for line in hmmfile.read().splitlines():
        bitrans_reg = 'bitrans\s+(\S+)\s+(\S+)\s+(\S+)'
        trans_reg = 'trans\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
        emit_reg = 'emit\s+(\S+)\s+(\S+)\s+(\S+)'
        bitrans_match = re.match(bitrans_reg, line) 
        trans_match = re.match(trans_reg, line)
        emit_match = re.match(emit_reg, line)

        if bitrans_match:
            qq, q, p = bitrans_match.groups()
            bitrans[(qq, q)] = math.log(float(p))
            #tags.update([qq, q])
        elif trans_match:
            qqq, qq, q, p = trans_match.groups()
            # creating an entry in trans with the POS tag pair
            # e.g. (init, NNP) = log(probability for seeing that transition)
            #if qqq not in trans:
                #trans[qqq] = {}
            #if qq not in trans[qqq]:
                #trans[qqq][qq] = {}
            #if q not in trans[qqq][qq]:
                #trans[qqq][qq][q] = math.log(float(p))
            trans[(qqq, qq, q)] = math.log(float(p))
            # add the encountered POS tags to set
            #tags.update([qqq, qq, q])
        elif emit_match:
            q, w, e = emit_match.groups()
            # creating an entry in emit with the tag and word pair
            # e.g. (NNP, "python") = log(probability for seeing that word with that tag)
            #if q not in emit_values:
                #emit_values[q] = {}
            #if w not in emit_values[q]:
                #emit_values[q][w] = math.log(float(e))
            emit_values[(q, w)] = math.log(float(e))
            # adding the word to encountered words
            voc[w] = w
            # add the encountered POS tags to set
            tags.update([q])
        else:
            #print 'no'
            pass

def get_possible_states(k):
    if k == -1:
        return {INIT_STATE}
    elif k == 0:
        return {INIT_STATE}
    else:
        return tags

def get_max(score, max_score, max_tag, v) :
    
    if score > max_score:
        max_score = score
        max_tag = v

    return max_score, max_tag

def print_bigram_results(n, foundgoal, last_bp, bp):
    if foundgoal:
        tagset = deque()
        tagset.append(last_bp)
        noun = 'NN'

        for i, k in enumerate(range(n, 1, -1)):
            if (k, tagset[i]) not in bp:
                tagset.append(noun)
            else:
                tagset.append(bp[(k, tagset[i])])

        for i, k in enumerate(tagset):
            if k == None:
                tagset[i] = 'NN'

        tagset.reverse()

        print " ".join(tagset)

def print_trigram_results(foundgoal, n, v_max, u_max, bp, testing_sentence):
    if foundgoal:
        tagset = deque() 
        tagset.append(v_max)
        tagset.append(u_max)

        for i, k in enumerate(range(n-2, 0, -1)):
            if(k+2, tagset[i+1], tagset[i]) in bp:
                tagset.append(bp[(k+2, tagset[i+1], tagset[i])])
        tagset.reverse()

        print " ".join(tagset)
        
    else:
        bigram_viterbi(testing_sentence) 
       

def bigram_viterbi(testing_sentence):

    pi = {}
    pi[(0, INIT_STATE)] = 0.0
    
    bp = {}
    last_bp = INIT_STATE

    score = 0 
    last_score = float('-Inf')
    
    foundgoal = False
    
    test_words = []
    for word in testing_sentence:
        if word in voc:
            test_words.append(word)
        else:
            test_words.append(OOV_SYMBOL)
            
    n = len(test_words)
    for k in range(1, n+1):
        for u in tags:
            max_score = float('-Inf')
            max_tag = None
            for v in tags:
                if (v, u) in bitrans and (u, test_words[k-1]) in emit_values:
                    if (k-1, v) not in pi:
                        score = bitrans[(v, u)]
                    else:
                        score = pi[(k-1, v)] + bitrans[(v, u)]
                    score = score + emit_values[(u, test_words[k-1])]
                    
                else:
                    score = float('-Inf')

                max_score, max_tag = get_max(score, max_score, max_tag, v)

            bp[(k, u)] = max_tag                   
            pi[(k, u)] = max_score
            

    max_score = float('-Inf')

    for v in tags:
        if (v, FINAL_STATE) in bitrans:
            if (n, v) in pi:
                last_score = pi[(n, v)] + bitrans[(v, FINAL_STATE)]

        if not foundgoal:
            max_score = last_score
            last_bp = v
            foundgoal = True

        elif last_score > max_score:
            max_score = last_score
            last_bp = v
            foundgoal = True

    print_bigram_results(n, foundgoal, last_bp, bp)

    

def trigram_viterbi(testing_words) :

    pi = defaultdict(float)
    pi[(0, INIT_STATE, INIT_STATE)] = 0.0
    bp = {}

    final_max_score = float('-Inf')
    score = 0 

    for testing_sentence in testing_words:
        foundgoal = False
        u_max = None
        v_max = None
        test_words = []
        
        for word in testing_sentence:
            if word in voc:
                test_words.append(word)
            else:
                test_words.append(OOV_SYMBOL)
                
        n = len(test_words)
        for k in range(1, n+1):
            for u in get_possible_states(k-1):
                for v in get_possible_states(k):
                    max_score = float('-Inf') 
                    max_tag = None
                    for w in get_possible_states(k - 2):
                        if (w, u, v) in trans:
                            if (v, test_words[k-1]) in emit_values:
                                if (k-1, w, u) in pi:
                                    score = pi[(k-1, w, u)] + trans[(w,u,v)] + emit_values[(v, test_words[k-1])]
                        else:
                            score = float('-Inf')

                        max_score, max_tag = get_max(score, max_score, max_tag, w)

                    bp[(k, u, v)] = max_tag
                    pi[(k, u, v)] = max_score 

        
        for u in get_possible_states(n-1):
            for v in get_possible_states(n):
                if (u, v, FINAL_STATE) in trans:
                    if (n, u, v) in pi:
                        score = pi[(n, u, v)] + trans[(u,v,FINAL_STATE)]
                    if score > final_max_score:
                        final_max_score = score
                        u_max = u
                        v_max = v
                        foundgoal = True

        print_trigram_results(foundgoal, n, v_max, u_max, bp, testing_sentence)

        
        

def main() :   

    testing_words = []
    for sentence in sys.stdin:
        modified_sentence = sentence.split(' ')[:-1]
        testing_words.append(modified_sentence)

    trigram_viterbi(testing_words)

main() 


        

        
    
