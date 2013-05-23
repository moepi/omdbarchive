#!/usr/bin/env python
import omdbapi as o
import logging, sys, os
import urllib2
import jinja2
import datetime
import itertools
log=logging.getLogger()

TEMPLATEDIR="/home/moepi/projects/omdbapi/templates"
SEARCHFOLDERS=["/home/moepi/Filer/TV/","/home/moepi/Filer/Movies"]
OUTPUTDIR="output"

folders=[]
index=[]
for path in SEARCHFOLDERS:
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

cis=list(itertools.chain.from_iterable([folder["cis"] for folder in folders]))
cis=o.overwrite_posters(cis,os.path.join(OUTPUTDIR,"posters"))

# load templates
templateLoader = jinja2.FileSystemLoader([TEMPLATEDIR])
templateEnv = jinja2.Environment(loader=templateLoader)
template_index=templateEnv.get_template('index.html')
template_folder=templateEnv.get_template('folder.html')

# generate index.html
indexsite=template_index.render(navitems=index)

# write index.html
try:
	f = open(os.path.join(OUTPUTDIR,"index.html"),'w')
	f.write(indexsite.encode("UTF-8"))
except IOError, e:
	log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
	sys.exit()

# create per folder html files
for folder in folders:
	s=template_folder.render(navitems=index, releases=folder["cis"], folder={"size":folder["size"],"count":folder["count"],"gendate":str(datetime.datetime.today())})
	#s= folder.toHTML() % (u" - ".join(index))
	try:
		f = open(os.path.join(OUTPUTDIR,folder["name"])+".html",'w')
		f.write(s.encode("UTF-8"))
	except IOError, e:
		log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
		sys.exit()
	f.close()
