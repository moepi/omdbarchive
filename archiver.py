#!/usr/bin/env python
import omdbapi as o
import logging, sys, os
import urllib2
import jinja2
import datetime
import itertools
import re
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log=logging.getLogger()

class Folder():
        def __init__(s,path,name,**kwargs):
                s.name=name
                s.size=0
                s.path=path
                log.info("Parsing folder: %s" % s.name)
                s.flist=s.getList(**kwargs)
        def getList(s, **kwargs):
                retList=[]
                listdir=os.listdir(s.path)
                if kwargs.get("sorted", True):
                        log.debug("Folder %s will be sorted" % s.name)
                        listdir=sorted(listdir)
                for item in listdir:
                        try:
                                currCI=o.CI(path=s.path,t=item)
                                if currCI.imdbQuery.get("imdbID"): retList.append(currCI)
                        except urllib2.HTTPError, error:
                                raise
                        except urllib2.URLError, error:
                                raise
                        except Exception, e:
                                raise
                return retList
        def getSize(s):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(s.path):
                        for f in filenames:
                                fp = os.path.join(dirpath, f)
                                total_size += os.path.getsize(fp)
                return "%.2f" % (total_size/1024**3)
        def toDict(s):
                return {"path":s.path,"name":s.name,"cis":[ci.toDict() for ci in s.flist], "size":s.getSize(), "count":len(s.flist)}

def ignore_articles(string):
	retStr=re.sub(r'(the |a )*','',string.lower())
	return retStr

def sort_by_name(folders):
	for folder in folders:
		folder["cis"] = sorted(folder["cis"], key=lambda k: ignore_articles(k['Title']))
	return folders

def walk_dirs(dirlist):
	folders=[]
	index=[]
	for curr_dir in dirlist:
		try:
			# build folder html files
			folders.append(Folder(curr_dir,curr_dir.strip("/").rsplit('/',1)[-1]).toDict())
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
	return (folders,index)

def download_poster(CIlist,outputdir):
	CIlist=list(itertools.chain.from_iterable([folder["cis"] for folder in folders]))
	CIlist=o.overwrite_posters(CIlist,os.path.join(outputdir,"posters"))

def build_html(folders,index,templatepath,outputdir):
	# load templates
	templateLoader = jinja2.FileSystemLoader([templatepath])
	templateEnv = jinja2.Environment(loader=templateLoader)
	template_index=templateEnv.get_template('index.html')
	template_folder=templateEnv.get_template('folder.html')
	
	# generate index.html
	indexsite=template_index.render(navitems=index)
	
	# write index.html
	try:
		f = open(os.path.join(outputdir,"index.html"),'w')
		f.write(indexsite.encode("UTF-8"))
	except IOError, e:
		log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
		sys.exit()
	
	# create per folder html files
	for folder in folders:
		s=template_folder.render(navitems=index, releases=folder["cis"], folder={"size":folder["size"],"count":folder["count"],"gendate":str(datetime.datetime.today())})
		try:
			f = open(os.path.join(outputdir,folder["name"])+".html",'w')
			f.write(s.encode("UTF-8"))
		except IOError, e:
			log.error("Could not write file: %s (%s)" % (e.strerror,e.errno))
			sys.exit()
		f.close()

if __name__=="__main__":
	if len(sys.argv)<4:
		print "Usage:\n python %s templates output /path/to/movies/ [/path/to/whatever]*" % sys.argv[0]
		sys.exit()
	templatedir = sys.argv[1]
	outputdir = sys.argv[2]
	searchfolders = sys.argv[3:]
	folders,index = walk_dirs(searchfolders)
	folders=sort_by_name(folders)
	download_poster([cis for cis in folders],outputdir)
	build_html(folders,index,templatedir,outputdir)
