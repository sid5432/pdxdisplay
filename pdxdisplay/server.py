#!/usr/bin/python3
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import re
from flask import Flask
from flask import request,url_for,redirect,render_template,request

if __name__ == '__main__':
    cdir = os.path.dirname( os.path.realpath(__file__) )
    sys.path.insert(0, cdir+"/..")

import pypdx
from pypdx import dbconn

import pdxdisplay
from pdxdisplay import homepage
from pdxdisplay import partsmaster
from pdxdisplay import getitem

if len(sys.argv) < 2:
    print("USAGE: %s DNS-string")
    sys.exit(1)

dns = sys.argv[1]
debug = True # ---------- turn off for production

try:
    if dns == 'pg':
        dns = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
        db = dbconn.DBconn(dns, dbtype='pg',debug=debug)
    elif dns[-8:] == '.sqlite3':
        db = dbconn.DBconn(dns, dbtype='sqlite3',debug=debug)
    elif re.match('dbname\s*=', dns) != None:
        db = dbconn.DBconn(dns, dbtype='pg',debug=debug)
    else:
        print("Unrecognized DNS %s" % dns)
        sys.exit()

except IOError as e:
    print("Connection Failed ",e)
    sys.exit(1)

# =========================================================================
# load flask
app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def homepage_app():
    if request.method == 'POST':
        return "Hello World! POST"
    else:
        var = homepage.process(dns,db)
        if var['error'] != None:
            return render_template('error.html',var=var)
        else:
            return render_template('homepage.html', var=var)

@app.route("/upload")
def upload():
    return "upload PDX file"

@app.route("/partsmaster",methods=['GET','POST'])
def partsmaster_app():
    sortby = request.args.get('sort')
    
    var = partsmaster.process(db,sortby)
    if var['error'] != None:
        return render_template('error.html',var=var)
    else:
        return render_template('partsmaster.html',var=var)

@app.route("/getitem",methods=['GET','POST'])
def getitem_app():
    uid = request.args.get('item')
    # var = { 'item': uid }
    var = getitem.getitem(db, uid)
    if var['error'] == None:
        return render_template('getitem.html',var=var)
    else:
        return render_template('error_insert.html',var=var)

@app.errorhandler(404)
def custom_401(error):
    var = {}
    var['error'] = error
    return render_template('error.html',var=var)

# -------- static routes ---------------------------
@app.route("/img/<imagename>")
def load_img(imagename):
    return redirect( url_for('static', filename=('img/%s' % imagename)) )

@app.route("/javascripts/<sname>")
def loadjs(sname):
    return redirect( url_for('static', filename=('javascripts/%s' % sname)) )

@app.route("/stylesheets/<sname>")
def load_ss(sname):
    return redirect( url_for('static', filename=('stylesheets/%s' % sname)) )

# =========================================================
if __name__ == '__main__':
    extra_files = ['templates/*.html']
    
    app.run( extra_files=extra_files, debug=debug )
    # app.run( ssl_context="adhoc" )
    
    
