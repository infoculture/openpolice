#!/usr/bin/env python

import sys, os, urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin

PAGE_NUMS = range(1, 5, 1)
PAGELIST_URL = "http://www.mvd.ru/presscenter/statistics/reports/page_%d/"
MVD_URL = 'http://www.mvd.ru'

def process_page(page_url):
#    print page_url
    o = urllib2.urlopen(page_url)
    data = o.read()
    soup = BeautifulSoup(data)
    allb = soup.findAll("div", attrs={'class' : 'news_block'})
    for b in allb:
        for u in b.findAll('a'):
	    url = urljoin(MVD_URL, u['href'])
	    text = u.string
	    s = ('\t'.join([url, text])).encode('utf8')
	    print s
    pass

def extract_reports():
    for i in PAGE_NUMS:
	process_page(PAGELIST_URL % i)
    
    pass

def extract_pdf_urls():
    f = open('reports.csv', 'r')
    for l in f:
	url, name = l.strip().split('\t')
	u = urllib2.urlopen(url)
	data = u.read()
	soup = BeautifulSoup(data)
	t = soup.find("div", attrs = {"class" : "news_block"})
#	print t
	if t is not None:
	    hrefs = t.findAll('a')
	    for h in hrefs:
		if h.has_key('id'): continue
		s = (u"%s\t%s\t%s" %(url, name.decode('utf8'), urljoin(MVD_URL, h['href']))).encode('utf8')
		print s
		filename = h['href'].rsplit('/', 1)[1]
		ul = urllib2.urlopen(urljoin(MVD_URL, h['href']))
		data = ul.read()
		f2 = open('docs/' + filename, 'w')
		f2.write(data)
		f2.close()
		
	u.close()
    f.close()

if __name__ == "__main__":
#    extract_reports()
    extract_pdf_urls()