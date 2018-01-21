#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import copy
import string

# only used for Python2
printable = set(string.printable)

from . import dbutils

def getitem(db, uid):
    var = {}
    var['error'] = None
    
    # mstr = "select * from partsmaster where itemuniqueidentifier='"+uid+"';"
    mstr = "select * from partsmaster where itemuniqueidentifier = "
    placeholder = db.placeholder
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr+placeholder, [uid])
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
    
    # now get attachments --------------------------------------------------
    mstr = "select * from attachment where itemuniqueidentifier = "
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr+placeholder, [uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['attachment'] = []
    rcount = 0
    for xrow in cur:
        row = copy.deepcopy( dict(xrow) )
        # there can be more than one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
        if sys.version_info[0] < 3 and row['description'] != None:
            row['description'] = filter(lambda x: x in printable, row['description'])
        
        var['attachment'].append(row)
        rcount += 1
    
    var['atcount'] = rcount
    cur.close()
    
    # now get approved mfg --------------------------------------------------
    mstr = "select * from approvedmfg where itemuniqueidentifier = "
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr+placeholder, [uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['mfg'] = []
    rcount = 0
    for xrow in cur:
        row = copy.deepcopy( dict(xrow) )
        # there can be more than one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
        if sys.version_info[0] < 3 and row['description'] != None:
            row['description'] = filter(lambda x: x in printable, row['description'])
        
        var['mfg'].append(row)
        rcount += 1
    
    var['mfgcount'] = rcount
    cur.close()
    
    return var
