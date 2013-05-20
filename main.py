#!/usr/bin/env python
import conf as c
import define as d
import omdbarchive as o
import logging, sys, os
import urllib2
import jinja2
log=logging.getLogger()

folders=[]
index=[]
for path in c.directories:
	try:
		# build folder html files
		folders.append(o.Folder(path,path.strip("/").rsplit('/',1)[-1],sorted=c.sorted).toDict())
		# update index
		index.append({"title":folders[-1]["name"],"link":folders[-1]["name"]+".html"})
	except urllib2.HTTPError, error:
		log.error("HTTPError %s" % e.code)
		sys.exit()
	except urllib2.URLError, error:
		log.error("URLError %s" % error.args)
		sys.exit()
	except Exception, e:
		log.error("%s. exiting" % str(e))
		sys.exit()

# load templates
templateLoader = jinja2.FileSystemLoader(['templates'])
templateEnv = jinja2.Environment(loader=templateLoader)
template_index=templateEnv.get_template('index.html')
template_folder=templateEnv.get_template('folder.html')
template_style=templateEnv.get_template('style.css')

doc={"stylesheet":c.stylesheet,"title":c.title}

# generate index.html
indexsite=template_index.render(doc=doc,navitems=index)
stylesheet=template_style.render()

# write index.html and style.css
try:
	f = open(os.path.join(c.outputdir,"style.css"),'w')
	f.write(stylesheet.encode("UTF-8"))
	f = open(os.path.join(c.outputdir,"index.html"),'w')
	f.write(indexsite.encode("UTF-8"))
except IOError, e:
	log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
	sys.exit()

# create per folder html files
for folder in folders:
	s=template_folder.render(doc=doc, navitems=index, releases=folder["cis"], folder={"size":folder["size"],"count":folder["count"]})
	#s= folder.toHTML() % (u" - ".join(index))
	try:
		f = open(os.path.join(c.outputdir,folder["name"])+".html",'w')
		f.write(s.encode("UTF-8"))
	except IOError, e:
		log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
		sys.exit()
	f.close()
