#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import datetime
import time

from . import dbutils

def process(db,sortby):
    var = {}
    var['date'] = datetime.datetime.fromtimestamp( time.time() ).strftime('%Y-%m-%d %H:%M:%S')
    var['error'] = None
    
    # get list
    if sortby != None:
        var['sortby'] = "sort by "+sortby
    else:
        var['sortby'] = ''
    
    if sortby == 'Description':
        sortby = 'description'
    elif sortby == 'Item ID':
        sortby = 'itemidentifier'
    elif sortby == 'Category':
        sortby = 'category'
    else:
        # ignore
        var['sortby'] = ''
        sortby = None
    
    mstr = "select M.*, "+\
    "(select count(*) from attachment A where A.itemuniqueidentifier=M.itemuniqueidentifier) as acount, "+\
    "(select count(*) from approvedmfg G where G.itemuniqueidentifier=M.itemuniqueidentifier) as gcount "+\
    "from partsmaster M"
    if sortby != None:
        mstr = mstr + " order by "+sortby
        
    cur = db.conn.cursor()
    try:
        cur.execute(mstr)
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['itemlist'] = []
    rcount = 0
    for row in cur:
        var['itemlist'].append(row)
        rcount += 1
    
    var['itemcount'] = rcount
    return var
    
# =============================================================
if __name__ == '__main__':
    print("Tests TBD")
    
