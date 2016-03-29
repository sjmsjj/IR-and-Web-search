import urllib2
import sys
from bs4 import BeautifulSoup as BT
from collections import defaultdict, OrderedDict

#calculate number of successors and find the predecessors for each url in the output 2000 urls using the url_2000.txt
def count_in_out_urls():
    out_pointed_urls = dict()
    in_pointed_urls = defaultdict(list)  #key: url, values: list of url's predecessors
    out_url_num = dict()   #key:url, value: number of url's successors
    old_score = OrderedDict() #key:url, value: 0.25

    with open('url_2000.txt', 'r') as f:
		for line in f:
			urls = line.rstrip('\n').split(',')
			out_pointed_urls[urls[0]] = urls[1:]
			old_score[urls[0]] = 0.25   #initialized the page score to be 0.25

		for key, values in out_pointed_urls.items():
			for value in values:
				if value in out_pointed_urls:
					in_pointed_urls[value].append(key)
					out_url_num[key] = out_url_num.get(key, 0) + 1

    return in_pointed_urls, out_url_num, old_score

def is_convergence(old_score, new_score, error = 0.001):
	return max(abs(old - new) for old, new in zip(old_score.values(), new_score.values())) < error

def get_page_rank(old_score, in_pointed_urls, out_url_num, N = 2000, d = 0.8, error = 0.001):
	new_score = OrderedDict()
	iteration = 0
	while True:
		iteration += 1
		for url in old_score:
			new_score[url] = (1 - d) / N
			for ur in in_pointed_urls[url]:
				new_score[url] += d * 1.0 / out_url_num[ur] * old_score[ur]
		if(is_convergence(old_score, new_score, error)):
			break
		else:
			old_score, new_score = new_score, old_score
	return new_score, iteration

if __name__ == "__main__":
	filename, error = sys.argv[1], float(sys.argv[2])
	in_pointed_urls, out_url_num, old_score= count_in_out_urls()
	page_score, iteration= get_page_rank(old_score, in_pointed_urls, out_url_num, 2000, 0.8, error)

	with open('PageRankURLs.txt', 'w') as f:
		for url, score in page_score.items():
			f.write(url + ' ' + str(score) + '\n')

