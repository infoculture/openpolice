#!/usr/bin/env python
# -*- coding: utf8 -*-

from urlparse import urljoin
import sys, os, mechanize
from lxml import etree
from urllib import quote
from copy import copy
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from urllib2 import HTTPError
import simplejson as json
from pymongo import Connection

BASE_URL = 'http://112.ru'

OKRUG_URL = 'http://www.mvd.ru/?module=precinct&action=subject&federal=%s'
OKOGU_L1_URL = "http://www.mvd.ru/?module=precinct&action=administrativeunit&federal=%s&subject=%s"
OKOGU_L2_URL = "http://www.mvd.ru/?module=precinct&action=code3&federal=%s&subject=%s&code2=%s"
OKOGU_L3_URL = 'http://www.mvd.ru/?module=precinct&action=code4&federal=%s&subject=%s&code2=%s&code3=%s'
OKOGU_L4_URL = 'http://www.mvd.ru/?module=precinct&action=code5&federal=%s&subject=%s&code2=%s&code3=%s&code4=%s'


BASE_PERSON_URL_L1 = 'http://112.ru/publish/00/00/uum/%s/contents.xml'
BASE_PERSON_URL_L2 = 'http://112.ru/publish/00/00/uum/%s/%s/contents.xml'
BASE_PERSON_URL_L3 = 'http://112.ru/publish/00/00/uum/%s/%s/%s/contents.xml'

ROOT_PERSON_URL_L1 = 'http://112.ru/publish/00/00/uum/%s/'
ROOT_PERSON_URL_L2 = 'http://112.ru/publish/00/00/uum/%s/%s/'
ROOT_PERSON_URL_L3 = 'http://112.ru/publish/00/00/uum/%s/%s/%s/'

BASE_ORGS_URL_L1 = 'http://112.ru/publish/00/00/nearOrg/mvd/f%s.shtml'
BASE_ORGS_URL_L2 = 'http://112.ru/publish/00/00/nearOrg/mvd/%s/f%s.shtml'
BASE_ORGS_URL_L3 = 'http://112.ru/publish/00/00/nearOrg/mvd/%s/%s/f%s.shtml'

OKRUG_LIST = ['1', '2', '3', '4', '5', '6', '7', '8']

class MvdBot:
	def __init__(self):
		self.conn = Connection()
		self.db = self.conn['mvd']
		self.okato_coll = self.db['okato']
		self.okato_coll.ensure_index('code', 1)
		self.okato_coll.ensure_index('level', 1)
		self.okato_coll.ensure_index('closed', 1)
		self.uum_coll = self.db['uum']
		self.uum_coll.ensure_index('code', 1)
		self.uum_coll.ensure_index('closed', 1)
		
		self.persons_coll = self.db['persons']
		self.persons_coll.ensure_index('code', 1)
		self.persons_coll.ensure_index('url', 1)
		
		self.org_coll = self.db['org']
		self.org_coll.ensure_index('code', 1)
		self.org_coll.ensure_index('closed', 1)
	
	

	def process_url(self, url):
		br = mechanize.Browser()
		resp = br.open(url)
		print 'Processing', url
		value = json.loads(resp.read())
		if type(value) != type({}):
			return {}
		return value

	def save_reg(self, k, v, parent=None, verify=True):
		if verify:
			item = self.okato_coll.find_one({'code' : k})
			if item: return False
		item = {'code': k, 'name' : v, 'parent' : parent, 'closed' : False}
		self.okato_coll.save(item)
		return True
	
	def close_reg(self, k):
		item = self.okato_coll.find_one({'code' : k})
		if item is not None:
			item['closed'] = True
		self.okato_coll.save(item)
	
	def is_closed(self, k):
		item = self.okato_coll.find_one({'code' : k})
		if item is not None:
			return item['closed']
		return False
	
	def extract_all_okrug(self):
		for okrug in OKRUG_LIST:
			regs = self.process_url(OKRUG_URL % okrug)
			for k, v in regs.items():
				if self.is_closed(k): continue
				self.save_reg(k, v, None, True)
				l2_items = self.process_url(OKOGU_L1_URL % (okrug, k))
				for l2_k, l2_v in l2_items.items():
					if self.is_closed(l2_k): continue
					self.save_reg(l2_k, l2_v, None, True)
					l3_items = self.process_url(OKOGU_L2_URL % (okrug, k, l2_k))
					for l3_k, l3_v in l3_items.items():
						if self.is_closed(l3_k): continue
						self.save_reg(l3_k, l3_v, None, True)
						l4_items = self.process_url(OKOGU_L3_URL % (okrug, k, l2_k, l3_k))
						for l4_k, l4_v in l4_items.items():
							if self.is_closed(l4_k): continue
							self.save_reg(l4_k, l4_v, None, True)
							self.close_reg(l4_k)									
						self.close_reg(l3_k)  				
					self.close_reg(l2_k)
				self.close_reg(k)
		
		
	def enrich(self):
		for o in self.okato_coll.find():
			if o['parent'] is None and not o.has_key('level'):
				if int(o['code'][2:]) == 0:
					o['parent'] = None
					o['level'] = 1
					self.okato_coll.save(o)
				elif int(o['code'][5:]) == 0:
					o['parent'] = o['code'][0:2] + '000000000'
					o['level'] = 2
					self.okato_coll.save(o)
				elif int(o['code'][8:]) == 0:
					o['parent'] = o['code'][0:5] + '000000'
					o['level'] = 3
					self.okato_coll.save(o)
				else:
					o['parent'] = o['code'][0:8] + '000'
					o['level'] = 4
					self.okato_coll.save(o)
			print o

	def process_uum_url(self, reg, url):
		br = mechanize.Browser()
		try:
			resp = br.open(url)
		except HTTPError, e:
			print 'Error', url, reg['name'].encode('utf8')
			return None
		print 'Processing', url, reg['name'].encode('utf8')
		doc = etree.parse(resp)
		items = []
		documents = doc.xpath('//doc')
		for document in documents:
			view = document.xpath('view')[0]
			if reg['level'] == 2:
				url = ROOT_PERSON_URL_L2 % (reg['parent'], reg['code'])
			elif reg['level'] == 1:
				url = ROOT_PERSON_URL_L1 % (reg['code'],)
			elif reg['level'] == 3:
				url = ROOT_PERSON_URL_L3 % (self.okato_coll.find_one({'code': reg['parent']})['parent'], reg['parent'], reg['code'])
			item = [document.attrib['type'], view.attrib['file'], url]
			items.append(item)
		return items

	def extract_uum(self):
		# find by level 2
		for reg in self.okato_coll.find({'level' : 2}):
			if self.uum_coll.find_one({'code' : reg['code']}) is not None: continue
			url = BASE_PERSON_URL_L2 % (reg['parent'], reg['code'])
			items = self.process_uum_url(reg, url)
			uum = copy(reg)
			if items is not None:
				uum['raw'] = items
				uum['has_data'] = True
				print '- got items:', len(items)
			else:
				uum['has_data'] = False
				print '- no items'
			self.uum_coll.save(uum)
	# 		print '- got items:', len(items)
		# find by level 3
		for reg in self.okato_coll.find({'level' : 3}):
			if self.uum_coll.find_one({'code' : reg['code']}) is not None: continue
			url = BASE_PERSON_URL_L3 % (self.okato_coll.find_one({'code' : reg['parent']})['parent'], reg['parent'], reg['code'])
			items = self.process_uum_url(reg, url)
			uum = copy(reg)
			if items is not None:
				uum['raw'] = items
				uum['has_data'] = True
				print '- got items:', len(items)
			else:
				uum['has_data'] = False
				print '- no items'
			self.uum_coll.save(uum)
	# 		print '- got items:', len(items)

	def calc_stats(self):
		total = 0
		for o in self.uum_coll.find({'has_data' : True}):
			total += len(o['raw'])
		print total
		ranks = {}
		for o in self.persons_coll.find({'parsed': True}):#{'parsed' : {'$exists' : False}}):
			if not o.has_key('rank'): continue
			v = ranks.get(o['rank'], 0)
			ranks[o['rank']] = v + 1
		for k, v in ranks.items():
			s = u'%s\t%d' %(k, v)
			print s.encode('utf8')
	
	def dump_persons(self):
		keys = ['img', 'url', 'fullname', 'position', 'rank']
		ks = ['region_code', 'region_name', 'terr_code', 'terr_name']
		ks.extend(keys)
		ks.extend(['gender', 'ethnics'])
		print (u'\t'.join(ks)).encode('utf8')
		for o in self.persons_coll.find({'parsed': True}):#{'parsed' : {'$exists' : False}}):
			item = []
			okato = self.okato_coll.find_one({'code' : o['code']})
			if okato['level'] == 1:
				item = [okato['code'], okato['name'], okato['code'], okato['name']]
			elif  okato['level'] == 2:
				item = [okato['parent'], self.okato_coll.find_one({'code' : okato['parent']})['name'], okato['code'], okato['name']]
			elif okato['level'] == 3:
				p1 = self.okato_coll.find_one({'code' : okato['parent']})
				p2 = self.okato_coll.find_one({'code' : p1['parent']})
				item = [p2['code'], p2['name'], okato['code'], okato['name']]
			for k in keys:
				item.append(o[k])
			if o.has_key('namedata') and o['namedata']['parsed']:
				nd = o['namedata']
				item.extend([nd['gender'], ','.join(nd['ethnics'])])
			else:
				item.extend(['', ''])
#			item.append(o['terr'][0])
			print (u'\t'.join(item)).encode('utf8')
	

	def collect_all_uum(self):
		br = mechanize.Browser()
		total = 0
		for o in self.uum_coll.find({'has_data' : True}):
			for rec in o['raw']:		
				total += 1
				if total % 100 == 0:
					print total
				item = {'code' : o['code'], 'otype' : rec[0], 'filename' : rec[1], 'url' : rec[2] + rec[1]}		
				if self.persons_coll.find_one({'url' : item['url']}): continue
				resp = br.open(item['url'])
				item['raw'] = resp.read()
				self.persons_coll.save(item)
			#print item
		#	if rec[0] == 'opunkt'
			pass
		
	def parse_uum_data(self):
		for o in self.persons_coll.find({'parsed' : {'$exists' : False}}):
			soup = BeautifulSoup(o['raw'])
			if o['otype'] == 'opunkt': continue
			#print soup
	#		print o['raw']
			tr = soup.findAll('tr')[0]
			tds = tr.findAll('td')
			img = tds[0].find('img')['src']
			divs = tds[1].findAll('div')
			o['img'] = urljoin(BASE_URL, img)
			if len(divs) > 1:
				fio = divs[0].text
				position = divs[1].text
				print fio
				print position
				o['parsed'] = True
				o['fullname'] = fio
				parts = position.split(u'Телефон:')
				if len(parts) > 1:
					phone = parts[1].strip()
					print parts[0], '-', phone
				parts = parts[0].rsplit(',', 1)
				o['position'] = parts[0].strip()
				if len(parts) > 1:
					o['rank'] = parts[1].strip()
				if len(divs) > 2:
					items = divs[2].findAll('li')
					territories = []
					for t in items:
						territories.append(t.text)
						o['terr'] = territories
				self.persons_coll.save(o)
			else:
				o['parsed'] = False
			self.persons_coll.save(o)
			
#		print img

#		print o['raw'].encode('utf8')
	pass

	def get_gender(self, name):
		br = mechanize.Browser()
		resp  = br.open("http://apibeta.skyur.ru/names/parse/?text=%s" % quote(name.encode('utf8')))
		return json.loads(resp.read())


	def enrich_persons(self):
		for o in self.persons_coll.find({'parsed' : True, 'namedata' : {'$exists' : False}}):
			gender = self.get_gender(o['fullname'])
			o['namedata'] = gender
			print gender
			self.persons_coll.save(o)
#		print gender

	def process_org_url(self, reg, url):
		br = mechanize.Browser()
		try:
			resp = br.open(url)
		except HTTPError, e:
			print 'Error', url, reg['name'].encode('utf8')
			return None
		print 'Processing', url, reg['name'].encode('utf8')
		items = []
		soup = BeautifulSoup(resp.read(), fromEncoding='utf8')
		trs = soup.findAll('tr')
		for tr in trs:
			item =[]
			for td in tr.findAll('td'):
				item.append(td.text)
			items.append(item)
		return items


	def extract_orgs(self):
	   # find by level 1
		for reg in self.okato_coll.find({'level' : 1}):
			if self.org_coll.find_one({'code' : reg['code']}) is not None: continue
			url = BASE_ORGS_URL_L1 % (reg['code'], )
			items = self.process_org_url(reg, url)
			org = copy(reg)
			if items is not None:
				org['raw'] = items
				org['has_data'] = True
				print '- got items:', len(items)
			else:
				org['has_data'] = False
				print '- no items'
			self.org_coll.save(org)		# find by level 2
		for reg in self.okato_coll.find({'level' : 2}):
			if self.org_coll.find_one({'code' : reg['code']}) is not None: continue
			url = BASE_ORGS_URL_L2 % (reg['parent'], reg['code'])
			items = self.process_org_url(reg, url)
			org = copy(reg)
			if items is not None:
				org['raw'] = items
				org['has_data'] = True
				print '- got items:', len(items)
			else:
				org['has_data'] = False
				print '- no items'
			self.org_coll.save(org)
		return
# 		print '- got items:', len(items)
		# find by level 3
		for reg in self.okato_coll.find({'level' : 3}):
			if self.org_coll.find_one({'code' : reg['code']}) is not None: continue
			url = BASE_ORGS_URL_L3 % (self.okato_coll.find_one({'code' : reg['parent']})['parent'], reg['parent'], reg['code'])
			items = self.process_org_url(reg, url)
			org = copy(reg)
			if items is not None:
				org['raw'] = items
				org['has_data'] = True
				print '- got items:', len(items)
			else:
				org['has_data'] = False
				print '- no items'
			self.org_coll.save(org)
# 		print '- got items:', len(items)

	def dump_orgs(self):
		keys = ['level', 'regcode', 'regname', 'areacode', 'areaname', 'orgname', 'phone', 'address', 'schedule']
		print '\t'.join(keys)
		all = self.org_coll.find({'level' : 1, 'has_data' : True})
		for o in all:
			for org in o['raw']:
				item = [o['level'], o['code'], o['name'], "", "", org[0], org[1], org[2], org[4]]
				item = map(unicode, item)
				s = ('\t'.join(item)).encode('utf8')
				print s

		all = self.org_coll.find({'level' : 2, 'has_data' : True})
		for o in all:
			parent = self.okato_coll.find_one({'code' : o['parent']})
			for org in o['raw']:
				item = [o['level'], parent['code'], parent['name'], o['code'], o['name'], org[0], org[1], org[2], org[4]]
				item = map(unicode, item)
				s = ('\t'.join(item)).encode('utf8')
				print s
		

	def clean_up(self):
		for org in self.uum_coll.find():
			if org.has_key('raw') and len(org['raw']) > 0 and type(org['raw'][0]) == type([]) and len(org['raw'][0]) > 0 and org['raw'][0][0] not in ['doc', 'opunkt']:
				self.uum_coll.remove(org['_id'])
#				print org
		pass

if __name__ == "__main__":
	bot = MvdBot()
#	bot.extract_all_okrug()
#	bot.enrich()
#	bot.extract_uum()
#	bot.calc_stats() 
	bot.dump_persons()
#	bot.collect_all_uum()
#	bot.parse_uum_data()  
#	bot.enrich_persons()
#	bot.dump_orgs()
#	bot.extract_orgs()
#	bot.clean_up()
 