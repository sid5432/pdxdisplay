#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import datetime
import time

from . import dbutils

def process(db):
    var = {}
    var['date'] = datetime.datetime.fromtimestamp( time.time() ).strftime('%Y-%m-%d %H:%M:%S')
    var['error'] = None
    
    # get list of top-level
    cur = db.conn.cursor()
    try:
        cur.execute("select * from partsmaster where istoplevel order by itemuniqueidentifier")
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
    print("TBD")
    sys.exit()
    
    
