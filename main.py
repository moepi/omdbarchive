#!/usr/bin/env python
import conf as c
import define as d
import omdbarchive as o
import logging, sys, os
import urllib2
log=logging.getLogger()

folders=[]
index=[]
for path in c.directories:
	try:
		# build folder html files
		folders.append(o.Folder(path,path.strip("/").rsplit('/',1)[-1],sorted=c.sorted))
		# update index
		index.append(d.INDEX % (folders[-1].name+".html",folders[-1].name))
	except urllib2.HTTPError, error:
		log.error("HTTPError %s" % e.code)
		sys.exit()
	except urllib2.URLError, error:
		log.error("URLError %s" % error.args)
		sys.exit()
	except Exception, e:
		log.error("%s. exiting" % str(e))
		sys.exit()

# writing index.html
indexsite=d.INDEXHTML % (c.stylesheet,c.title,u" - ".join(index))
try:
	f = open(os.path.join(c.outputdir,"index.html"),'w')
	f.write(indexsite.encode("UTF-8"))
except IOError, e:
	log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
	sys.exit()

# create per folder html files
for folder in folders:
	s= folder.toHTML() % (u" - ".join(index))
	try:
		f = open(os.path.join(c.outputdir,folder.name)+".html",'w')
		f.write(s.encode("UTF-8"))
	except IOError, e:
		log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
		sys.exit()
	f.close()
