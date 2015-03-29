#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, csv, json, datetime
from urllib2 import urlopen
from bs4 import BeautifulSoup
from pyparsing import Word, nums, alphas, oneOf, lineStart, lineEnd, Optional, restOfLine, Literal, ParseException, CaselessLiteral

URLPAT = 'http://xn--b1adsqdaof.xn--p1ai/site/info?id=%s'

TIME_PAT = Word(nums, exact=2).setResultsName('hour') + Optional(u':').suppress() + Word(nums, exact=2).setResultsName('minute')
RUS_MONTHS_LC = [u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря']
rulc_mname2mon = dict((m,i+1) for i,m in enumerate(RUS_MONTHS_LC) if m)
RUS_MONTHS_PAT = oneOf(RUS_MONTHS_LC).setParseAction(lambda t: rulc_mname2mon[t[0]])

RUS_YEARS = [u'г.', u'года']
RUS_YEARS_PAT = oneOf(RUS_YEARS)
DATE_PATTERN = Word(nums, min=1, max=2).setResultsName('day') + Optional(u',').suppress() + RUS_MONTHS_PAT.setResultsName('month') + Word(nums, exact=4).setResultsName('year') + Optional(RUS_YEARS_PAT).suppress() + Optional(u',').suppress() + TIME_PAT

def collect_data():
	f = open('raw/dtps.json', 'r')
	jsdata = json.load(f)
	i = 0
	records = []
	for r in jsdata:
		record = {}
		record['id'] = r[2]
		record['lng'] = r[0]
		record['lat'] = r[1]
		u = urlopen(URLPAT % r[2])
		record['raw_html'] = u.read()
		u.close()
		i += 1
		records.append(record)
		print i, record['id']
	f.close()
	f = open('raw/prepared.json', 'w')
	json.dump(records, f, sort_keys=True, indent=4)
	f.close()
	pass




def parse_data():
	f = open('raw/prepared.json', 'r')
	jsdata = json.load(f)
	i = 0
	records = []
	for r in jsdata:
		soup = BeautifulSoup(r['raw_html'])
#		print soup
		dtype_raw = soup.find('div', class_='dtp-type').text
		blocks = dtype_raw.split('\n')
		for b in blocks:
			b = b.strip()
			if len(b) == 0: continue
			if ord(b[0]) == 8212:  # '-'
				r['dtptype'] = b.split()[-1]
			else:
				parts = b.split(':')
				if parts[0] == u'транспортных средств':
					r['cars'] = int(parts[1].strip())
				elif parts[0] == u'участников':
					r['participants'] = int(parts[1].strip())
				else:
					print 'Warning! Unknown keyword %s' % b

		dtype_raw = soup.find('div', class_='dtp-casualties').text
		blocks = dtype_raw.split('\n')
		for b in blocks:
			b = b.strip()
			if len(b) == 0: continue
			parts = b.split(':')
			name = parts[0].strip().split()[-1]
			if name == u'Пострадавших':
					r['wounded'] = int(parts[1].strip())
			elif name == u'Погибших':
				r['dead'] = int(parts[1].strip())
			else:
				print 'Warning! Unknown keyword %s' % b

		dtype_raw = soup.find('div', class_='dtp-address').text
		address = dtype_raw.strip().split(' ', 1)[-1].strip()
		r['address'] = address
		raw = soup.find('div', class_='dtp-time')
#		print raw.text
#		print DATE_PATTERN
		thedate= DATE_PATTERN.parseString(raw.text)
		d = {}
		for k, v in thedate.items():
			d[k] = int(v)
		dt = datetime.datetime(**d)
		r['date'] = dt.isoformat()
		r['date_parsed'] = dict(thedate)
		del r['raw_html']
		records.append(r)
		print i, r['id']
	f.close()
	f = open('final/processed.json', 'w')
	json.dump(records, f, sort_keys=True, indent=4)
	f.close()
	pass




if __name__ == "__main__":
# Comment selected row if you want to run one-by-one process
	collect_data()
	parse_data()
	pass