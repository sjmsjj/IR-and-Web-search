#homework 2 from Jianming Sang,   uniquename: jmsang

import os
import sys
import re
import math
from collections import defaultdict
from preprocess import process

#tokenize the text and calculate the term frequency
def processText(docContent):
	tokens = process(docContent)
	tokenFrequency = defaultdict(list)
	for token in tokens:
		tokenFrequency[token] = tokenFrequency.get(token, 0) + 1
	return set(tokens), tokenFrequency

#construct the dictinary: dictionary({term1:[df, {docID:tf, docID:tf, ...}], term2:[df, {docID:tf ...}]})
def indexDocument(docContent, docWeightScheme, queryWeightScheme, invertedIndex, docID, maxTF):
	tokens, tokenFrequency = processText(docContent)
	maxTF[docID] = max(tokenFrequency.values())   #max term frquency used in nxx doc term weight scheme
	for token in set(tokens):
		if token in invertedIndex:
			invertedIndex[token][0] += 1
			invertedIndex[token][1][docID] = tokenFrequency[token]
		else:
			invertedIndex[token].append(1)
			invertedIndex[token].append({docID : tokenFrequency[token]})
	return invertedIndex, maxTF

#calculate the doc term weight, return: dictionary({term1:{docID:tf, docID:tf, ...}, term2:{docID:tf ...}})
def getDocTermWeight(invertedIndex, docWeightScheme, maxTF):
	docTermWeight = defaultdict(dict)
	# tfidf weight scheme
	if docWeightScheme == 'tfidf':
		sumWeight = dict()
		for term in invertedIndex:
			for docID in invertedIndex[term][1]:
				tfIdf = invertedIndex[term][1][docID] * math.log10(N*1.0/invertedIndex[term][0])
				sumTfidf = 0
				if docID in sumWeight:
					sumTfidf = sumWeight[docID]
				else:
					for word in invertedIndex:
						if docID in invertedIndex[word][1]:
							sumTfidf += invertedIndex[word][1][docID] * math.log10(N*1.0/invertedIndex[word][0])
					sumWeight[docID] = sumTfidf
				docTermWeight[term][docID] = tfIdf*1.0/sumTfidf
	# nxx weight scheme
	else:
		for term in invertedIndex:
			for docID in invertedIndex[term][1]:
				docTermWeight[term][docID] = 0.5 + 0.5*invertedIndex[term][1][docID]/maxTF[docID]
	return docTermWeight

def getDocLength(invertedIndex, docTermWeight, docCollection):
	docLength = dict()
	for docID in docCollection:
		length= 0
		for term in invertedIndex:
			if docID in invertedIndex[term][1]:
				length += (docTermWeight[term][docID]) ** 2
		docLength[docID] = math.sqrt(length)
	return docLength
	
#calcaute the query term weight based on different weight scheme
def getQueryTermWeight(queryTF, invertedIndex, queryWeightScheme, queryTerms):
 	queryTermWeight = dict()
 	#tfidf query term weight scheme using tfx
 	if(queryWeightScheme == "tfidf"):
		for term in queryTerms:
			if term in invertedIndex:
				queryTermWeight[term] = queryTF[term]*1.0*math.log10(N*1.0/invertedIndex[term][0])
			else:
				queryTermWeight[term] = 0
	#probabilistic query term weight scheme
	else:	
		for term in queryTerms:
			if term in invertedIndex:
				n = invertedIndex[term][0]
				queryTermWeight[term] = math.log10((N - n)*1.0/n)
			else:
				queryTermWeight[term] = 0
	return queryTermWeight

def retrieveDocuments(query, invertedIndex, docWeightScheme, queryWeightScheme, docTermWeight, docLength):
 	queryTerms, queryTF = processText(query)
 	queryTermWeight = getQueryTermWeight(queryTF, invertedIndex, queryWeightScheme, queryTerms)
	queryLength = math.sqrt(sum(x**2 for x in queryTermWeight.values()))
	relevantDocs = dict()
	for term in queryTerms:
		if term in docTermWeight:
			for docID in docTermWeight[term]:
				if docID not in relevantDocs:
					temp = 0
					for word in queryTerms:
						if word in docTermWeight:
						    temp += queryTermWeight[word] * docTermWeight[word].get(docID, 0)
					relevantDocs[docID] = temp/(docLength[docID] * queryLength)
	relevantDocs = [[docID, similarity] for docID, similarity in relevantDocs.items()]
	relevantDocs = sorted(relevantDocs, key = lambda x: x[1], reverse = True)
	relevantDocs = filter(lambda x: x[1] > 0, relevantDocs)
	return relevantDocs

#calculat the macro precision and recall
def evalution(returnDoc, judgeDoc, rank = 10):
	precision = 0
	recall = 0
	for ID in returnDoc:
		hit = 0
		if rank <= len(returnDoc[ID]):
			hit = len(set([x[0] for x in returnDoc[ID][:rank]]) & set(judgeDoc[ID]))
		else:
			hit = len(set([x[0] for x in returnDoc[ID]]) & set(judgeDoc[ID]))
		precision += hit*1.0/rank
		recall += hit*1.0/len(judgeDoc[ID])
	return precision/len(returnDoc), recall/len(returnDoc)

#format the output and print the results
def printOutput(returnDoc):
	for queryID in returnDoc:
		for doc in returnDoc[queryID]:
			print queryID, doc[0], doc[1]

if __name__ == '__main__':
	docCollection = []   #store doc id
	maxTF = dict()   #store max term frequency for each doc
	invertedIndex = defaultdict(list)
	docID = 0
	for filename in os.listdir(sys.argv[3]):
		with open(sys.argv[3] + filename, 'r') as f:
			docID += 1
			docContent = f.read()
			docCollection.append(docID)
			invertedIndex, maxTF = indexDocument(docContent, sys.argv[1], sys.argv[2], invertedIndex, docID, maxTF)
	N = len(docCollection)
	docTermWeight = getDocTermWeight(invertedIndex, sys.argv[1], maxTF)
	docLength = getDocLength(invertedIndex, docTermWeight, docCollection)
	results = dict()
	with open(sys.argv[4], 'r') as f:
		for line in f:
			query = line.split()
			queryID = int(query[0])
			query = ' '.join(query[1:])
			results[queryID] = retrieveDocuments(query, invertedIndex, sys.argv[1], sys.argv[2], docTermWeight, docLength)

	judgeDoc = defaultdict(list)
	with open('cranfield.reljudge', 'r') as f:
		for line in f:
			line = line.split()
			key, val = int(line[0]), int(line[1])
			judgeDoc[key].append(val)

	# for n in [10, 50, 100, 500]:
	# 	print evalution(results, judgeDoc, n)

	printOutput(results)

