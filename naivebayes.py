#homework 3 from Jianming Sang,   uniquename: jmsang

#implement naivebayes for text classification

import os
import sys
import re
import math
from collections import defaultdict
from preprocess import removeSGML, tokenizeText, removeStopwords, stemWords

# process the text file
def processText(text, stopwords = False, stem = False):
	tokens = removeSGML(text)
	tokens = tokenizeText(tokens)
	if stopwords:
		tokens = removeStopwords(tokens)
	if stem:
		tokens = stemWords(tokens)
	return tokens

def trainNaiveBayes(trainFile, fileTokenList):
	N = len(trainFile)
	nlie = ntrue = 0  #number of lie files and number of true files
	tokens = defaultdict(list) #class label as key, value is the all the tokens belonging to that class
	ntokens = dict()  #number of tokens for each class
	tokenFrequency = defaultdict(dict)
	vocabulary = []
	condProb = defaultdict(dict)
	key = 'lie'
	keys = ['lie', 'true']  #we only have two classes

	for filename in trainFile:
		if filename.startswith('lie'):
			nlie += 1
			key = 'lie'
		else:
			ntrue += 1
			key = 'true'
		tokens[key].extend(fileTokenList[filename])
	
	pLie, pTrue = nlie * 1.0 / N, ntrue * 1.0 / N

	for key in keys:
		vocabulary += list(set(tokens[key]))
		for item in tokens[key]:
			tokenFrequency[key][item] = tokenFrequency[key].get(item, 0) + 1
		ntokens[key] = len(tokens[key])

	vocabularySize  = len(vocabulary)
	for key in keys:
		for item in vocabulary:
			condProb[key][item] = (tokenFrequency[key].get(item, 0) + 1) * 1.0 / (ntokens[key] + vocabularySize)
	return pLie, pTrue, condProb

def textNaiveBayes(testFile, fileTokenList, pLie, pTrue, condProb):
	p = {'lie':pLie, 'true':pTrue}
	for key in p:
		for item in fileTokenList[testFile]:
			p[key] *= condProb[key].get(item, 1)   #calculate the accumulate probability for each class
	if p['lie'] > p['true']:
		return 'lie'
	else:
		return 'true'

#print the top 10 words 
def printTop10Words(condProb):
	print 'top 10 words with highest conditional probability: '
	for key in condProb:
		print 'label: ', key
		for word, prob in sorted(condProb[key].items(), key = lambda x: x[1], reverse = True)[:10]:
			print word, prob

if __name__ == '__main__':
	fileList = []
	fileTokenList = defaultdict(dict)  #store tokens for each file under different implementation (whethre remove the stopwords or stem the words)

	stopwordsFT = [False, True]
	stemFT = [False, True]

	for filename in os.listdir(sys.argv[1]):
		fileList.append(filename)
		with open(sys.argv[1] + filename, 'r') as f:
			text = f.read()
			for stopwords in stopwordsFT:
				for stem in stemFT:
					fileTokenList[(stopwords, stem)][filename] = processText(text, stopwords, stem)

	hit = dict()
	for stopwords in stopwordsFT:
		for stem in stemFT:
			hit[(stopwords, stem)] = 0
			for i in range(len(fileList)):
				testFile = fileList[i]
				trainFile = fileList[0:i] + fileList[i+1: ]
				pLie, pTrue, condProb = trainNaiveBayes(trainFile, fileTokenList[(stopwords, stem)])
				predict = textNaiveBayes(testFile, fileTokenList[(stopwords, stem)], pLie, pTrue, condProb)
				if not stopwords and not stem:
					print testFile, predict
				if testFile.startswith(predict):
					hit[(stopwords, stem)] += 1
			hit[(stopwords, stem)] *= 1.0/len(fileList)
			print 'remove stopwords:', stopwords, 'apply stem:', stem
			print 'accuracy:', hit[(stopwords, stem)]
			print
	#print the top 10 words with highest conditional probability 
	# _, _, condProb = trainNaiveBayes(fileList, fileTokenList[(False, False)])
	# printTop10Words(condProb)







