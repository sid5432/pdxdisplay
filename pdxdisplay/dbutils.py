#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals

def dberrmsg(db, e):
    if db.dbtype == 'sqlite3':
        return e
    else:
        msg = ""
        if e.pgerror != None:
            msg += e.pgerror+"; "
        if e.diag.message_detail != None:
            msg += e.diag.message_detail
        
        return msg

