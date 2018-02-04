pdxdisplay
==========

*A simple web application for viewing PDX (Product Data eXchange) XML
files*

Introduction
------------

From `the Wikipedia article on
PDX <https://en.wikipedia.org/wiki/PDX_(IPC-257X)>`__: “the PDX (Product
Data eXchange) standard for manufacturing is a multi-part standard,
represented by the IPC 2570 series of specifications.”

As the name implies, it is a standard for exchanging product definition
between companies or organizations, and can include bill of material
(BOM), approved manufacturer list, drawings, documents, etc.; pretty
much anything can be included if desired.

In simple terms, a \*.pdx file (usually exported from Agile/Oracle) is
really just a ZIP file that contains all the files (“attachments”)
associated with the product (assembly), plus a special XML file called
**pdx.xml**. This XML file contains the particulars of the various Items
and their properties/attributes, the relationship between the Items,
which forms the bill-of-materials (BOM), and also information about the
various files that are inside the PDX/ZIP file.

The DTD of this XML file (identified as “DTD 2571 200111”) can be found
on the `IPC
website <http://www.ipc.org/4.0_Knowledge/4.1_Standards/IPC-25xx-files/2571.zip>`__.
Free PDX viewers are available, one of the most popular being PDXViewer
from `PDXplorer <http://www.pdxplorer.com/>`__.

Since the \*.pdx file is simply a ZIP file, it is easy to extract all
the attachments (documents, schematics, drawings, etc.) from the ZIP
file, and there are several ways one can view XML files. However, trying
to make sense of the assembly from a generic XML viewer is not really
feasible, and although there are specialized free (and non-free)
viewers, there are times when you might want to extract the data for
your own use. To this end I have written a simple PDX XML file parser,
`pypdx <https://github.com/sid5432/pypdx>`__ for doing this (for
details, please head over to the github page or the `Python Package
Index <https://pypi.python.org/pypi/pypdx/>`__ site.

The *pypdx* program can be used as a Python module, but also as a
command-line stand-alone program that is more or less ready to use. But
after storing the data into the database, you have to figure out how to
view it. To make life easier for people who just want a quick view of
what the items and bill of materials looks like, there is now a separate
program **pdxdisplay** that will let you import and display the items.
(I had wanted to call it *pdxviewer*, but `that name is already
taken <http://www.pdxplorer.com/pdxplorer-pdx-viewer.htm>`__.)

The *pdxdisplay* program is a web application written in
`Flask <http://flask.pocoo.org/>`__ that provides a simple interface
(via a web browser) to upload and display a PDX XML file. The program
depends on the *pypdx* module.

Please note that this is not intended to be a full-fledged viewer for
PDX XML files (never mind managing the complete PDX file with all the
attachements). In particular it does not run on HTTPS (although it is
trivial to do that with a simple add-on module), there is no user
authentication, and it does not allow any editing of the data. There is
minimal sorting providing, but no additional filtering or searching.
Also note that some of the data from the PDX XML file is not included
(see the *pypdx* module). In particular, none of the
**AdditionalAttribute** fields in the XML file are included (I might add
those at a later time, but no promises).

Nevertheless, I hope this might still be useful to some people. This is
of course provided at no cost, and with no warranty. Use at your own
risk!

Installation and Usage
----------------------

To install the module and program, run

::

    pip install pdxdisplay

This should install all the necessary dependencies, and create an
executable pdxdisplay. Before you run this program, you will need a
database: either a `SQLite3 <https://www.sqlite.org/>`__ database or a
`PostgreSQL <https://www.postgresql.org/>`__ database, as described in
document for the *pypdx* module. You specify the DSN by setting up the
environment variable **PDX_DSN**; the *pdxdisplay* program will not run
without this.

If you are using the SQLite3 file-based database, do something like
this:

::

    % set PDX_DSN=mydatabase.sqlite3 
    % pdxdisplay

(the extension of the SQLite3 database file needs to end with the
extension *.sqlite3* for the program to recognize it as a SQLite3 file).
For a PostgreSQL database, do something like this

::

    % set PDX_DSN="dbname='pdx' user='pdxuser' host='localhost' password='billofmaterials' port=5432"
    $ pdxdisplay

If you are connecting to the default PostgreSQL database *pdx* (as
listed above), you can also use the short-hand:

::

    % set PDX_DSN=pg
    % pdxdisplay

Running the *pdxdisplay* program will start the Flask web server at

::

    http://localhost:5000/

You can then connect to this URL with your web browser.

By default *Flask* does not accept external connections (i.e.,
connections from outside your computer). If you really want to accept
external connections, set the environment variable *PDX_EXTACCESS* to 1:

::

    % export PDX_EXTACCESS=1

before running *pdxdisplay* (but keep in mind that the connection is not
encrypted, nor is there any authentication).

Note that you do not really need to install the PostgreSQL component if
you do not care for the PostgreSQL database. You should still be able to
use the program without installing the *psycopg2* module, since it is
not imported unless you specify the PostgreSQL database option. But
there maybe dependencies issues when trying to install this through
*pip*.

Issues with Python2 and Unicode
-------------------------------

The *pdxdisplay* program was tested primarily with Python3, and for best
results you should use the Python3. If you are running one of the Ubuntu
derivates, it is likely that your *python* is Python2, and Python3 is
listed as *python3*. In this case you may try to change “#!” line in the
*pdxdisplay* file to point to python3. The program *should* run under
Python2 also, but there were some issues having to do with non-ASCII
characters that caused the program to fail. Specifically, it seems that
non-ASCII characters sent to the *render_template()* method (from Flask)
will cause it to break. This only occurs with Python2; Python3 does not
have this problem.

As a work-around, the program will filter out all non-ASCII characters
in the *description* fields (of the Item, Attachments, etc. tables), but
**only if it detects the script running under Python2**. However, the
program does not check for this in other fields. If there are non-ASCII
characters in those fields, the program will likely crash (but, as I
said, only if you are using Python2).

Even in Python3, you need to watch out for the database encoding. For
postgreSQL, you may run into trouble if your database has ASCII
encoding, but your PDX XML file has UTF-8 characters. If you are trying
to run this in a `Ubuntu docker
container <https://hub.docker.com/_/ubuntu/>`__ for example, set the
environment variables to:

::

    % export LC_ALL=C.UTF-8
    % export LANG=C.UTF-8

Docker Container
----------------

If you have *docker* installed on your system and would like to try out
*pdxdisplay* with a PostgreSQL database, you can try the docker
container:

::

    docker pull sidneyli/pdx:latest

or build the container yourself (please see my `github
page <https://github.com/sid5432/pdx-docker>`__ for details).

Closing Remarks
---------------

I have only seen a very small number of PDX files, and there does not
seem to be any sample PDX files that you can download from the Internet
(likely because the only PDX files available contain proprietary
manufacturing information!). Naturally the testing of the *pypdx* module
and the *pdxdisplay* program has been very limited. While I believe the
implementation to be correct (if incomplete), there is always the
possibility of bugs. So use at your own risk; you have been warned!

(*Last Revised 2018-02-03*)
