#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import copy
import tempfile

from . import dbutils
import pypdx

def process(xmldata, cleardata, dsn, dbtype, debug=False):
    var = {}
    var['error'] = None
    
    xmlfilename = tempfile.mkstemp(suffix=".xml")[1]
    xmldata.save(xmlfilename)
    
    if dsn == 'pg':
        dsn = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
    
    try:
        if debug:
            print("* DSN: "+dsn);
            print("* XML file: "+xmlfilename)
            print("* dbtype: "+dbtype)
        
        mypdx = pypdx.PDX(xmlfilename, dsn, dbtype=dbtype, debug=debug)
    except Exception as e:
        var['error'] = e
        return var
    
    if cleardata:
        if debug:
            print("*** remove old records at user request ***")
        
        mypdx.removeall()
    
    status = mypdx.fillparts()
    if status != 'ok':
        var['error'] = status
    
    # clean-up
    try:
        if debug:
            print("remove file "+xmlfile)
        
        os.remove(xmlfilename)
        pass
    except IOError as e:
        var['error'] = e
    
    return var

