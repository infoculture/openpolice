#!/usr/bin/env python
# -*- coding: utf8 -*-


import sys, os, mechanize
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
MVDDKO_URL = 'http://www.dko-mvd.ru'

keys = ['name', 'url']
def extract_mvd_edu():
    br = mechanize.Browser()
    resp = br.open(MVDDKO_URL)
    soup = BeautifulSoup(resp.read())
    tag = soup.find('option', attrs={'value' : 'index-1308.html'})
    tag = tag.parent
    values = tag.findAll('option')
    for val in values:
	if val.has_key('value'):
            print ('\t'.join([val.text, urljoin(MVDDKO_URL, val['value'])])).encode('utf8')
        #.text, val.attrs['value']
	    
if __name__ == "__main__":
    extract_mvd_edu()
    