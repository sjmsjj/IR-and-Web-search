
#homework 1 from Jianming Sang,   uniquename: jmsang


import math
import os
import sys


#calulate the log probability of some text belonging to some language
def logP(text, charCount, biCount):
	prob = 0
	V = len(charCount)   #number of vocabulary for smoothing
	for i in xrange(len(text)-1):
		prob += (1 + biCount.get(text[i:i+2], 0)) * 1.0 / (V + charCount.get(text[i], 0))
	return prob

#format the output of predicted languages for each line
def outputPredict(predict):
	for i in xrange(len(predict)):
		print 'Line{} {}'.format(str(i+1), predict[i])

#traning the model, calculate the frequency of each character and each bigram
def trainBigramLanguageModel(trainText):
	charFrequency = dict()   #used to store character frequency
	bigramFrequency = dict()  #used to store bigram frequency
	for i in xrange(len(trainText) - 1):
		charFrequency[trainText[i]] = charFrequency.get(trainText[i], 0) + 1
		bigramFrequency[trainText[i:i+2]] = bigramFrequency.get(trainText[i:i+2], 0) + 1
	charFrequency[trainText[i+1]] = charFrequency.get(trainText[i+1], 0) + 1  #the above loop did not count the last character
	return charFrequency, bigramFrequency

#predict the language of each in the test file 
def identifyLanguage(textList, singleChar, biChar):
	predict = list()
	for text in textList:
		probs = [logP(text, charCount, biCount) for charCount, biCount in zip(singleChar, biChar)]
		index_max = probs.index(max(probs))  #calculate the probability for each candidate languages and find the index of the max one
		predict.append(languages[index_max])
	return predict


if __name__ == '__main__':
	testFile = sys.argv[1]
	baseDir = sys.argv[1].split('/')[0]
	trainingFile = os.path.join(baseDir, 'training')
	languages = os.listdir(trainingFile)  #store all the candidate languages for training
	numLanguages = len(languages)

	singleChar, biChar = [0]*numLanguages, [0]*numLanguages  #list of dict for storing the char/bigram frequency dict
	for i in xrange(numLanguages):
	    with open(os.path.join(baseDir, 'training/' + languages[i]), 'r') as f:
	    	text = f.read()
	    	singleChar[i], biChar[i] = trainBigramLanguageModel(text)
    
    #idenfity the language of each line in the test file
	with open(baseDir + '/test') as f:
		predict = identifyLanguage(f.readlines(), singleChar, biChar)

	outputPredict(predict)

    #calculate the identification accuracy
	i = accuracy = 0
	with open(baseDir+'/solution') as f:
		for line in f:
			if line.split()[1] == predict[i]:
				accuracy += 1
			i += 1

    #output the accuracy to the file answer2
	with open('answer2.txt', 'w') as f:
		f.write('Jianming Sang\jmsang\n')
		f.write('\n')
		f.write('Accuracy of the language identifier: ' + str(accuracy*1.0/len(predict)))






