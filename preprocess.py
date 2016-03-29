#homework 1 from Jianming Sang,   uniquename: jmsang

import os
import sys
import re
import math
import PorterStemmer as stem



def removeSGML(text):
	text = re.sub('<.*?>', ' ', text)
	return text

def tokenizeText(text):
	#token date for pattern like: 01/08/2015, January 18, January 18, 2015, Jan. 18, 2015, Jan. 18
	month1 = '[(January)|(February)|(March)|(April)|(May)|(June)|(July)|(August)|(September)|(October)|(November)|(December)]+'
	month2 = '[(Jan)|(Feb)|(Mar)|(Apr)|(May)|(Jun)|(Jul)|(Aug)|(Sept)|(Oct)|(Nov)|(Dec)]+'
	datePattern = ['\d+/\d+/\d+', month1 + ' ' + '\d+, ' + '\d+', month1+ ' \d+',\
	           month2 + ' ' + '\d+, ' + '\d+', month2 + ' \d+', \
	           month2 + '\. ' + '\d+ ' + '\d+', month2 + '\. \d+']
	dates = []  #used to store the date token
	for pattern in datePattern:
		dates.extend(re.findall(pattern, text))
		text = re.sub(pattern, '', text)

	hyphenPattern = ['[A-Za-z]+-[A-Za-z]+', ' -\d+'] #untokenize - when it's between two characters or negative number
	hyphens = []
	for pattern in hyphenPattern:
		hyphens.extend(re.findall(pattern, text))
		text = re.sub(pattern, '', text)

	commas = re.findall('\d+,\d+', text) #untokenize comma when it is in a number
	text = re.sub('\d+,\d+', '', text)

	for p in re.finditer('[a-z]+\'[a-z]+]', text):
		if p in contraction:
			text = text.replace(p, contraction[p])   #expand the '
		else:
			one, two = p.split('\'')   #split '
			text = text.replace(p, one + ' ' + '\''+ two)
	
	text = re.sub('[()/\_]', ' ', text)  #remove ( ) \ / _ from the file

    #after extracting the untokenized items, we can safely replace the peroid, comma, space with space
	text = re.sub(',', ' ', text)
	text = re.sub('-', ' ', text)
	text = re.sub(' +\.', ' ', text)
	text = re.sub('\. +', ' ', text)

	tokens = re.split('\s+', text)   #splite the string into tokens

	tokens += dates + hyphens + commas
	tokens = filter(lambda x: x != '', tokens)   #remove any empty space in the token list
	tokens += dates + hyphens + commas
	return tokens

def removeStopwords(tokens):
	for token in tokens[:]:
		if token in stopwords:
			tokens.remove(token)
	return tokens

def stemWords(tokens):
	p = stem.PorterStemmer()
	tokens = [p.stem(word, 0, len(word)-1) for word in tokens]
	return tokens

#process the text file using the above methods
def process(text):
	text = removeSGML(text)
	tokens = tokenizeText(text)
	tokens = removeStopwords(tokens)
	tokens = stemWords(tokens)
	return tokens

#output the results to the console based on the requirement
def outPut(totalWords, totalItems, topWords):
	print 'Words', totalWords
	print 'Vocabulary', totalItems
	print 'Top 50 words'
	for i in xrange(50):
		print '{} {}'.format(topWords[i][0], str(topWords[i][1]))

if __name__ == '__main__':
	#get the contraction list from the contracton file for expanding during tokenzing apostrophe
	contraction = dict()
	with open('contraction.csv', 'r') as f:
		for line in f:
			key, val = line.rstrip().split(',')
			contraction[key] = val

	stopwords = []
	with open('stopwords.txt', 'r') as f:
		for line in f:
			stopwords.append(line.rstrip())

	words = dict()
	words1 = dict()
	words2 = dict()
	flag = 0

	for filename in os.listdir(sys.argv[1]):
		with open(sys.argv[1] + filename, 'r') as f:
			text = f.read()
			for token in process(text):
				words[token] = words.get(token, 0) + 1
                #the following is for picking up two subsets of the dataset
				if flag%2 == 0:
					words1[token] = words1.get(token, 0)  + 1
				if flag%5 == 0:
					words2[token] = words2.get(token, 0) + 1
			flag += 1
    
    #calulate the total number of words, vocabulary
	totalWords = sum(words.values())
	totalItems = len(words)

	#sort the words based on their frequency
	topWords = sorted([(x, y) for x, y in words.items()], key = lambda item: item[1], reverse=True)
	#output the results to the console
	outPut(totalWords, totalItems, topWords)

    #find the min number of unique words which counts 25% of the total number of words
	numOfWords = 0
	target = totalWords*0.25
	for num in xrange(totalItems):
		numOfWords += topWords[num][1]
		if numOfWords >= target:
			break

    #calculate the beta and k values based on the heap's law equation
	w1, v1 = sum(words1.values()), len(words1)
	w2, v2 = sum(words2.values()), len(words2)
	beta = math.log(v1*1.0/v2, w1*1.0/w2)
	k = v1/math.pow(w1, beta)

    #predict the vocabulary size based on the heap's law
	size1 = int(k*math.pow(1000000, beta))
	size2 = int(k*math.pow(1000000000, beta))

    #output the results to answer1.txt
	with open('answer1.txt', 'w') as f:
		f.write('Jianming Sang/jmsang\n')
		f.write('\n')
		f.write('Total number of words in the Cranfield collection: ' + str(totalWords) + '\n')
		f.write('Vocabulary size of the Cranfield colleection: ' + str(totalItems)+ '\n')
		f.write('Top 50 words:\n')
		for i in xrange(50):
			f.write('{} {}'.format(topWords[i][0], str(topWords[i][1]))+ '\n')
		f.write('The minimus number of unique words accouting for 25% of the total number of words: ' + str(num)+ '\n')
		f.write('Beta = ' + str(beta)+ '\n')
		f.write('K = ' + str(k)+ '\n')
		f.write('Predicted vocabulary size when n = 1000000: ' + str(size1)+ '\n')
		f.write('Predicted vovabulary size when n = 1000000000: ' + str(size2)+ '\n')

	






