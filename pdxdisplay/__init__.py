#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import re
import signal
import tempfile
from flask import Flask
from flask import request,url_for,redirect,render_template,request,flash

__version__ = "0.0.1a1"

if __name__ == '__main__':
    cdir = os.path.dirname( os.path.realpath(__file__) )
    sys.path.insert(0, cdir+"/..")

import pypdx
from pypdx import dbconn

import pdxdisplay
from pdxdisplay import homepage
from pdxdisplay import partsmaster
from pdxdisplay import getitem
from pdxdisplay import upload
from pdxdisplay import bomtree
from pdxdisplay import getbomitem

ALLOWED_EXTENSIONS = set( ['xml'] )

debug = False
if 'FLASK_DEBUG' in os.environ and os.environ['FLASK_DEBUG'] == 1:
    print("** DEBUG MODE ON **")
    debug = True

dsn = None
if 'PDX_DSN' in os.environ:
    dsn = os.environ['PDX_DSN']

if dsn == None:
    print("You need to set the database DSN via the environment variable PDX_DSN")
    # need to use this to exit when using "flask run"
    os.kill( os.getpid(), signal.SIGTERM)
    # sys.exit(1)

def get_db( dsn ):
    var = {}
    db = None
    var['error'] = None
    try:
        if dsn == 'pg':
            dsn = "dbname='pdx' user='pdxuser' host='localhost' port=5432"
            db = dbconn.DBconn(dsn, dbtype='pg',debug=debug)
            db.placeholder = '%s'
        elif dsn[-8:] == '.sqlite3':
            # Note: cannot use in-memory (:memory:) here
            db = dbconn.DBconn(dsn, dbtype='sqlite3',debug=debug)
            db.placeholder = '?'
        elif re.match('dbname\s*=', dsn) != None:
            db = dbconn.DBconn(dsn, dbtype='pg',debug=debug)
            db.placeholder = '%s'
        elif dsn == ':memory:':
            var['error'] = "Sorry, can't use :memory: here"
        else:
            var['error'] = "Unrecognized DSN %s" % dsn
        
    except IOError as e:
        var['error'] = "Database connection failed "+e.__repr__()
    
    return db, var

# make sure we can connect
db, var = get_db(dsn)

if var['error'] != None or db == None:
    print(var['error'])
    os.kill( os.getpid(), signal.SIGTERM)

db.close()

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# =========================================================================
# load flask
app = Flask(__name__)
app.secret_key = "yskl6z5itoomanysecrets"

# -------------------------------------------------------------------------
@app.route("/",methods=['GET','POST'])
def homepage_app():
    db, var = get_db(dsn)
    if var['error'] != None or db == None:
        return render_template('error.html',var=var)
    
    dbtype = db.dbtype
    
    # proceeed....
    # see if this is an upload
    if request.method == 'POST':
        cleardata = request.values.get('clearall')
        cleardata = True if cleardata=='on' else False;

        # print("try to upload")
        xmlfile = ""
        if 'pdxfile' in request.files:
            xmldata = request.files['pdxfile']
            
            if xmldata.filename == '':
                flash("no file selected")
            elif xmldata and allowed_file(xmldata.filename):
                var = upload.process( xmldata, cleardata, dsn, dbtype, debug=debug )
                if var['error'] != None:
                    return render_template('error.html',var=var)
                else:
                    if cleardata:
                        flash("Old data removed by request.")
                    
                    flash("XML data successfully uploaded.")
            else:
                flash("File type not allowed")
        
        else:
            print("** no file **")
            pass
    
    # continue with display of top level items
    var = homepage.process(db)
    db.close()
    if var['error'] != None:
        return render_template('error.html',var=var)
    else:
        return render_template('homepage.html', var=var)

# -------------------------------------------------------------------------
@app.route("/partsmaster",methods=['GET','POST'])
def partsmaster_app():
    sortby = request.args.get('sort')
    db,var = get_db(dsn)
    if var['error'] != None or db == None:
        return render_template('error.html',var=var)
    
    var = partsmaster.process(db,sortby)
    db.close()
    
    if var['error'] != None:
        return render_template('error.html',var=var)
    else:
        return render_template('partsmaster.html',var=var)

# -------------------------------------------------------------------------
@app.route("/getitem",methods=['GET','POST'])
def getitem_app():
    uid = request.args.get('item')
    # var = { 'item': uid }
    db,var = get_db(dsn)
    if var['error'] != None or db == None:
        return render_template('error.html',var=var)
    
    var = getitem.getitem(db, uid)
    db.close()
    if var['error'] == None:
        return render_template('getitem.html',var=var)
    else:
        return render_template('error_insert.html',var=var)

# -------------------------------------------------------------------------
@app.route("/getbomitem",methods=['GET','POST'])
def getbomitem_app():
    s_uid = request.values.get('source')
    t_uid = request.values.get('target')
    
    db,var = get_db(dsn)
    if var['error'] != None or db == None:
        return render_template('error.html',var=var)
    
    var = getbomitem.getbomitem(db, s_uid, t_uid)
    db.close()
    if var['error'] == None:
        return render_template('getbomitem.html',var=var)
    else:
        return render_template('error_insert.html',var=var)

# -------------------------------------------------------------------------
@app.route("/bom",methods=['GET','POST'])
def bomtree_app():
    uid = request.args.get('item')
    db,var = get_db(dsn)
    if var['error'] != None or db == None:
        return render_template('error.html',var=var)
    
    var = bomtree.process(db, uid)
    db.close()
    if var['error'] == None:
        return render_template('bomtree.html',var=var)
    else:
        return render_template('error.html',var=var)
    

# -------------------------------------------------------------------------
@app.errorhandler(404)
def custom_401(error):
    var = {}
    var['error'] = error
    return render_template('error.html',var=var)

# --------------- static routes ------------------------------------------
@app.route("/img/<imagename>")
def load_img(imagename):
    return redirect( url_for('static', filename=('img/%s' % imagename)) )

@app.route("/javascripts/<sname>")
def loadjs(sname):
    return redirect( url_for('static', filename=('javascripts/%s' % sname)) )

@app.route("/stylesheets/<sname>")
def load_ss(sname):
    return redirect( url_for('static', filename=('stylesheets/%s' % sname)) )

def main():
    extra_files = ['templates/*.html']
    app.run( extra_files=extra_files, debug=debug )
    # app.run( ssl_context="adhoc" )
    

# =========================================================
if __name__ == '__main__':
    pdxdisplay.main()

