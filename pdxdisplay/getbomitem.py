#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import copy
import string

# only used for Python2
printable = set(string.printable)

from . import dbutils

def getbomitem(db, s_uid, t_uid):
    var = {}
    var['error'] = None
    
    mstr = "select * from partsmaster where itemuniqueidentifier = "
    ph = db.placeholder
    # print("***",mstr,t_uid)
    
    cur = db.conn.cursor()
    try:
        # get *target* info
        cur.execute(mstr+ph, [t_uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['item'] = None
    rcount = 0
    for xrow in cur:
        # NOTE: for postgres (psycopg2) we can modify row[name] directly,
        # but not with sqlite3
        row = copy.deepcopy( dict(xrow) )
        # there should be only one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
        if sys.version_info[0] < 3 and row['description'] != None:
            row['description'] = filter(lambda x: x in printable, row['description'])
        
        var['item'] = row
        rcount += 1
    
    var['itemcount'] = rcount
    cur.close()
    
    # now get bom entry ----------------
    mstr = "select * from bom where itemuniqueidentifier="+ph+" and billofmaterialitemuniqueidentifier="+ph
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr, [s_uid,t_uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['bom'] = None
    rcount = 0
    for xrow in cur:
        row = copy.deepcopy( dict(xrow) )
        # there should be only one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
        var['bom'] = row
        rcount += 1
    
    var['bcount'] = rcount
    cur.close()
    
    return var
