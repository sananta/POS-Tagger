#!/usr/bin/python

# David Bamman
# 2/14/14
#
# Python port of train_hmm.pl:

# Noah A. Smith
# 2/21/08
# Code for maximum likelihood estimation of a bigram HMM from 
# column-formatted training data.

# Usage:  train_hmm.py tags text > hmm-file

# The training data should consist of one line per sequence, with
# states or symbols separated by whitespace and no trailing whitespace.
# The initial and final states should not be mentioned; they are 
# implied.  
# The output format is the HMM file format as described in viterbi.pl.

#2/13/18
#Srivarshini Ananta
# I have modified the code to account for both bigram and trigram values.

import sys,re
from itertools import izip
from collections import defaultdict

TAG_FILE=sys.argv[1]
TOKEN_FILE=sys.argv[2]

vocab={}
OOV_WORD="OOV"
INIT_STATE="init"
FINAL_STATE="final"
taglist = set() 

bigram_vocab = {}
bigram_transitions = {}
bigram_transitionsTotal = defaultdict(int)
emissions={}
transitions={}
transitionsTotal=defaultdict(int)
emissionsTotal=defaultdict(int)

with open(TAG_FILE) as tagFile, open(TOKEN_FILE) as tokenFile:
	for tagString, tokenString in izip(tagFile, tokenFile):

		tags=re.split("\s+", tagString.rstrip())
		tokens=re.split("\s+", tokenString.rstrip())
		pairs=zip(tags, tokens)

		prevtag=INIT_STATE

		for (tag, token) in pairs:

			# this block is a little trick to help with out-of-vocabulary (OOV)
			# words.  the first time we see *any* word token, we pretend it
			# is an OOV.  this lets our model decide the rate at which new
			# words of each POS-type should be expected (e.g., high for nouns,
			# low for determiners).

			if token not in bigram_vocab:
				bigram_vocab[token]=1

			if prevtag not in bigram_transitions:
				bigram_transitions[prevtag]=defaultdict(int)

			# increment the transition observation

			bigram_transitions[prevtag][tag]+=1
			#bigram_transitions[prevtag][OOV_WORD]+=1
			bigram_transitionsTotal[prevtag]+=1

			prevtag=tag

		# don't forget the stop probability for each sentence
		if prevtag not in bigram_transitions:
			bigram_transitions[prevtag]=defaultdict(int)

		bigram_transitions[prevtag][FINAL_STATE]+=1
		bigram_transitionsTotal[prevtag]+=1

for prevtag in bigram_transitions:
	for tag in bigram_transitions[prevtag]:
		print "bitrans %s %s %s" % (prevtag, tag, float(bigram_transitions[prevtag][tag]) / bigram_transitionsTotal[prevtag])

with open(TAG_FILE) as tagFile, open(TOKEN_FILE) as tokenFile:
	for tagString, tokenString in izip(tagFile, tokenFile):

		tags=re.split("\s+", tagString.rstrip())
		tokens=re.split("\s+", tokenString.rstrip())
		pairs=zip(tags, tokens)

		prevprevtag = INIT_STATE
		prevtag=INIT_STATE

		for (tag, token) in pairs:

			# this block is a little trick to help with out-of-vocabulary (OOV)
			# words.  the first time we see *any* word token, we pretend it
			# is an OOV.  this lets our model decide the rate at which new
			# words of each POS-type should be expected (e.g., high for nouns,
			# low for determiners).

			if token not in vocab:
				vocab[token]=1
				#token=OOV_WORD

			if tag not in emissions:
				emissions[tag]=defaultdict(int)
			if prevprevtag not in transitions:
				transitions[prevprevtag] = {}
			if prevtag not in transitions[prevprevtag]:
				transitions[prevprevtag][prevtag]=defaultdict(int)

			# increment the emission/transition observation
			emissions[tag][token]+=1
			emissions[tag][OOV_WORD] += 1
			emissionsTotal[tag]+=1

			if tag not in transitions:
				transitions[prevprevtag][prevtag][tag] = 1
			else:
				transitions[prevprevtag][prevtag][tag] += 1

			if prevprevtag not in transitionsTotal:
				transitionsTotal[prevprevtag] = {}
			if prevtag not in transitionsTotal[prevprevtag]:
				transitionsTotal[prevprevtag][prevtag] = 1
			else:
				transitionsTotal[prevprevtag][prevtag] += 1

			prevprevtag = prevtag
			prevtag=tag

		# don't forget the stop probability for each sentence
		#taglist = set(emissionsTotal)
		if prevprevtag not in transitions:
			transitions[prevprevtag] = {}
		if prevtag not in transitions[prevprevtag]:
			transitions[prevprevtag][prevtag]=defaultdict(int)

		transitions[prevprevtag][prevtag][FINAL_STATE]+=1

		if prevprevtag not in transitionsTotal:
			transitionsTotal[prevprevtag] = {}
		if prevtag not in transitionsTotal[prevprevtag]:
			transitionsTotal[prevprevtag][prevtag] =1
		else:
			transitionsTotal[prevprevtag][prevtag] += 1

for prevprevtag in transitions:
	for prevtag in transitions[prevprevtag]:
		for tag in transitions[prevprevtag][prevtag]:
			print "trans %s %s %s %s" % (prevprevtag, prevtag, tag, float(transitions[prevprevtag][prevtag][tag]) / transitionsTotal[prevprevtag][prevtag])

for tag in emissions:
	for token in emissions[tag]:
		print "emit %s %s %s " % (tag, token, float(emissions[tag][token]) / emissionsTotal[tag])
