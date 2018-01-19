#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os

from . import dbutils

def getitem(db, uid):
    var = {}
    var['error'] = None
    
    # mstr = "select * from partsmaster where itemuniqueidentifier='"+uid+"';"
    mstr = "select * from partsmaster where itemuniqueidentifier = "
    placeholder = "%s"
    if db.dbtype == 'sqlite3':
        placeholder = "?"
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr+placeholder, [uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['item'] = None
    rcount = 0
    for row in cur:
        # there should be only one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
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
    for row in cur:
        # there can be more than one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
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
    for row in cur:
        # there can be more than one item
        for name in row.keys():
            if name[:2] == 'is':
                row[name] = 'Yes' if row[name] else 'No'
        
        var['mfg'].append(row)
        rcount += 1
    
    var['mfgcount'] = rcount
    cur.close()
    
    return var
    
        
