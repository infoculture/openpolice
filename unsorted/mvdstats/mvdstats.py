# -*- coding: utf8 -*-


import sys, os, mechanize
from BeautifulSoup import BeautifulSoup
MVDSTAT112_URL = 'http://ps.112.ru/portal/dt?PortalMainContainer.setSelected=DefStatistics&last=false'

keys = ['year', 'month', 'reg_name', 'ind_bribery', 'ind_robbery', 'ind_rape', 'ind_steal', 'ind_drugs', 'ind_peculation', 'ind_brigadary', 'ind_death', 'ind_harm', 'ind_ruffian']
def extract_mvd_stats(year, month):
    br = mechanize.Browser()
    resp = br.open(MVDSTAT112_URL)
    for form in br.forms():
	br.select_form(nr=0) # to select the first form
    
    br.find_control('page').readonly = False
    br.find_control('month').readonly = False
    br.find_control('year').readonly = False
    br['page'] = '2'
    br['month'] = str(month)
    br['year'] = str(year)
    resp = br.submit()
    soup = BeautifulSoup(resp.read())
    table = soup.find('table', attrs={"class": "stattab"})
    i = 0
    for row in table.findAll('tr'):
	i += 1
	if i == 1: continue
	parts = [str(year), str(month)]
	for td in row.findAll('td'):
	    parts.append(td.text.replace('&nbsp;', ' ').strip())
	print ('\t'.join(parts)).encode('utf8')

def extract_all():
    print '\t'.join(keys)
    for year in range(2009, 2012):
	for month in range(1, 13):
	    extract_mvd_stats(year, month)
    for year in range(2012, 2013):
	for month in range(1, 10):
	    extract_mvd_stats(year, month)
	    
if __name__ == "__main__":
    extract_all()
    