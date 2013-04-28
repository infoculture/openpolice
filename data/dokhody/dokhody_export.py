#!/usr/bin/env python
# coding: utf8


import sys, os
from pymongo import Connection


person_keys = ['person_id', 'person', 'family_size', 'gender', 'position', 'personal_income', 'couple_income', 'couple_share', 'property_abroad', 'total_income', 'total_share']
min_keys = ['person_id', 'person']
fam_keys = ['income', 'ptype', 'name', 'transport_raw']
prop_keys = ['country', 'prop_plot', 'prop_type', 'psize']

from copy import copy

class ExportDkhody:
	def __init__(self):
		self.conn = Connection()
		self.db = self.conn['dokhody']
		self.coll = self.db['int_min_2009']

	def export_persons_csv(self):
	    print '\t'.join(person_keys)
	    for item in self.coll.find():
    		val = []
    		for k in person_keys:
    		    val.append(unicode(item[k]))
    		print ('\t'.join(val)).encode('utf8')

	def export_family_csv(self):
	    keys = copy(min_keys)
	    keys.extend(fam_keys)
	    print '\t'.join(keys)
	    for item in self.coll.find():
    		for fam in item['family']:
    		    val = []
    		    for k in min_keys:			
    			val.append(unicode(item[k]) if item.has_key(k) else "")
    		    for k in fam_keys:
    			val.append(unicode(fam[k]) if fam.has_key(k) else "")
    		    print ('\t'.join(val)).encode('utf8')

	def export_prop_csv(self):
	    keys = copy(min_keys)
	    keys.extend(fam_keys)
	    keys.extend(prop_keys)
	    print '\t'.join(keys)
	    for item in self.coll.find():
    		for fam in item['family']:
    		    if not fam.has_key('own_property'): continue
    		    for prop in fam['own_property']['list']:
    			val = []
    			for k in min_keys:			
    			    val.append(unicode(item[k]) if item.has_key(k) else "")
    			for k in fam_keys:
    			    val.append(unicode(fam[k]) if fam.has_key(k) else "")
    			for k in prop_keys:
    			    val.append(unicode(prop[k]) if prop.has_key(k) else "")
			print ('\t'.join(val)).encode('utf8')


    
    		
if __name__ == "__main__":
    ex = ExportDkhody()
#    ex.export_persons_csv()
#    ex.export_family_csv()
    ex.export_prop_csv()
 