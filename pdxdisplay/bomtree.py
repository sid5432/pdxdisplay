#!/usr/bin/python
from __future__ import absolute_import, print_function, unicode_literals
import sys
import os
import copy
from flask import flash
import copy
import string

# only used for Python2
printable = set(string.printable)

from . import dbutils

def process(db, uid):
    var = {}
    var['error'] = None
    
    ph = db.placeholder
    
    # root item
    mstr = "select * from partsmaster where itemuniqueidentifier="+ph
    cur = db.conn.cursor()
    try:
        cur.execute(mstr, [uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    var['root'] = None
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
        
        var['root'] = row
    
    cur.close()
    
    var['maxlevel'] = 10; # limit level of BOM to avoid accidental infinite recursion!
    level = 0
    
    var['expand_all'] = ""
    var['collapse_all'] = ""
    var['set_expand_buttons'] = ""
    var['title_complete'] = False
    var['contents'] = ""
    var['itemcount'] = 0
    multiplier = 1
    
    find_children( uid, level, multiplier, db, var )
    
    return var
    
# ---------------------------------------------------------------------------------
def add_expand_button(uid,var):
    
    icount = var['itemcount']

    button  = ("document.getElementById('hold-%s').style.background = \"#0000FF\";\n" % uid)
    button += ("document.getElementById('cbox-%s').disabled = false;\n" % uid)
    
    var['expand_all'] += "   document.getElementById('cbox-%s').checked = true;\n" % uid
    var['expand_all'] += "   $('#div-%d').show('fast');\n" % icount
    
    var['collapse_all'] += "   document.getElementById('cbox-%s').checked = false;\n" % uid
    var['collapse_all'] += "   $('#div-%d').hide('fast');\n" % icount

    return button

# ---------------------------------------------------------------------------------
def find_children( uid, level, multiplier, db, var ):
    ph = db.placeholder
    mstr = "select *,"+\
    "(select itemidentifier from partsmaster P where P.itemuniqueidentifier=B.itemuniqueidentifier) as itemidentifier,"+\
    "(select revisionidentifier from partsmaster P where P.itemuniqueidentifier=B.itemuniqueidentifier) as revision,"+\
    "(select description from partsmaster P where P.itemuniqueidentifier=B.billofmaterialitemuniqueidentifier) as tdescription "+\
    " from bom B where itemuniqueidentifier="+ph+" order by billofmaterialitemuniqueidentifier"
    
    cur = db.conn.cursor()
    try:
        cur.execute(mstr, [uid])
    except db.dbmodule.Error as e:
        var['error'] = dbutils.dberrmsg(db, e)
        return var
    
    display = "block" if (level == 0) else "none"
    stp_par = uid
    
    indent = "%dpt" % (8+level*8)
    
    results = cur.fetchall()
    
    if len(results) == 0:
        return
    
    if level > 0:
        # UID stp_par has children! add expansion button
        var['set_expand_buttons'] += add_expand_button(uid,var)
    
    # check if we hit max level
    if level >= var['maxlevel']:
        msg = "<p><b>WARNING:</b> reached max depth of $level; not going any deeper. "+\
        "Make sure there is not an circular reference somewhere!\n";
        flash(msg)
        return
    
    # margin:2pt $indent 2pt $indent
    pad = "0" if level == 0 else "25pt"
    
    var['contents'] += ("\n<div ID='div-%s' " % var['itemcount'])
    var['contents'] += " style='padding-left:%s;padding-right:25pt;display:%s;border:1px solid #CCCCCC;'>\n" % (pad,display)
    
    for xrow in results:
        # NOTE: for postgres (psycopg2) we can modify row[name] directly,
        # but not with sqlite3
        row = copy.deepcopy( dict(xrow) )
        if sys.version_info[0] < 3 and row['tdescription'] != None:
            row['tdescription'] = filter(lambda x: x in printable, row['tdescription'])
        
        var['itemcount'] += 1
        icount = var['itemcount']
        # print("got ",row)
        if level == 0 and var['title_complete'] == False:
            var['title_complete'] = True
        
        qty = row['itemquantity'] if row['itemquantity'] != None else 1
        tmult = multiplier * row['itemquantity']
        
        source = row['itemuniqueidentifier']
        s_id   = row['itemidentifier']
        target = row['billofmaterialitemuniqueidentifier']
        t_id   = row['billofmaterialitemidentifier']
        rev = row['revision'] if row['revision']!=None else "unknown"
        
        ttitle = row['tdescription'] if row['tdescription']!=None else "(missing)"
        
        cbox = ("<span ID='hold-%s' style='padding:4pt 1pt 1pt 1pt;background:#DDDDDD;border:1px solid #DDDDDD'>\n" % (target))
        cbox += "<INPUT TYPE='checkbox' ID='cbox-%s' onChange=\"javascript:expand_tree('%d')\" disabled='true'" % (target,icount)
        cbox += "style='margin:2pt 2pt 2pt 2pt;foreground:green'></span>\n"
         
        link2link = "<A style='color:red' HREF=\"#it%d\" onClick=\"javascript:show_bomdetails('%s','%s',event)\">" % \
        (var['itemcount'],source,target)
        link2link += "<i>%s</i></A>" % (t_id)
        
        var['contents'] += ("<p style='margin:2pt 2pt 2pt 2pt;'><A NAME=\"it%d\"></A>" % var['itemcount'])
        var['contents'] += cbox+" "+link2link+(" [qty %d]: " % qty)
        var['contents'] += ("<A HREF='#it%d' onClick=\"javascript:show_details('%s',event)\">" % (var['itemcount'],target))
        var['contents'] += ttitle+"</A>" + ("&nbsp;<span style='font-style:italic;color:#888888'>(rev %s)</span>" % rev)
        
        child = target
        find_children( child, level+1, multiplier, db, var )
    
    var['contents'] += "\n</div>\n"
    
    return
    
