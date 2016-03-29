"""This program is created by Jianming Sang, jmsang"""

import urllib2
import re
import sys
from bs4 import BeautifulSoup as BT
from collections import deque, OrderedDict, defaultdict


def add_link(queue, urls, url_2000, u, link, base = None):
	if link.endswith('/'):
		link = link[:-1]
	if base:
		link = base + link   #handle relative link
	temp = link
	if link.startswith('https'):  #treat http:url == https:url
		temp = 'http' + link[5:]
	if link not in urls and temp not in urls: #add link if it has not been added to the urls
		urls[link] = 1
		queue.append(link)
	if link != u:
		url_2000[u].append(link)    #successors of u for later pagerank calculation (do not include itself)

def get_link(rootfile, nlinks = 2000):
	with open(rootfile, 'r') as f:
		root = f.readline().rstrip()
	root_s = 'https://www.eecs.umich.edu'
	urls = dict()  #contains all the urls to be potentially visited
	url_2000 = OrderedDict()

	queue = deque()
	queue.append(root)
	urls[root] = 1

	with open('URLs.txt', 'w') as f:
		while queue and nlinks:
			u = queue.popleft()
			try:
				page = urllib2.urlopen(u, timeout = 2).read()
			except Exception:    #ignore bad url
				continue
			url_2000[u] = []
			f.write(u+'\n')
			nlinks -= 1
			soup = BT(page)
			for a in soup.find_all('a'):
				link = a.get('href')
				if link:
					if link.startswith('http') and not link.startswith((root, root_s)):  #ignore the urls don't have the same domain as the root url
						continue
					if re.search(r'\.[^/(html)(cgi)]+$', link) and not link.endswith(('html','cgi')):  #ignore any files like .pdf, .txt ...
						continue
					if link.startswith((root, root_s)):
						add_link(queue, urls, url_2000, u, link)
					elif re.match(r'^/.+', link):
						add_link(queue, urls, url_2000, u, link, root)

    #output the 2000 urls and their successors for pagerank calculation
	with open("url_2000.txt", 'w') as f:
		for key, value in url_2000.items():
			f.write(key + ',')
			f.write(','.join(value))
			f.write('\n')



if __name__ == '__main__':
	rootfile, nlinks = sys.argv[1], int(sys.argv[2])
	get_link(rootfile, nlinks)