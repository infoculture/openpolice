#!/usr/bin/env python
# -*- coding: utf8 -*-.

from pymongo import Connection

FABULA = u'Описание преступления (краткая фабула)'

def process():
    c = Connection()
    db = c['proc']
    coll = db['pskov']
    cursor = coll.find({'requisites' : {'$exists': True}})
    n = 0
    keys = ['id', 'fabula']
    print '\t'.join(keys)
    for item in cursor:
        id = item['id']
        req = item['requisites']
        keys = req.keys()
        
        if FABULA in keys:
            n += 1
            print '\t'.join([str(id), req[FABULA].encode('utf8')])
 
if __name__ == "__main__":
    process()

