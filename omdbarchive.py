import conf as c
import define as d
import urllib, urllib2
import os
import json
import logging, sys
import re
log=logging.getLogger()

class CI():
	def __init__(s,*args,**kwargs):
		s.path=os.path.join(kwargs.get("path"),kwargs.get("t"))
		imdbid=s.getidbynfo(s.path)
		idfound=False
		try:
			# trying found nfo file
			if len(imdbid)>0:
				# get omdb entry by id
				# we take the first id, shouldn't be too many
				s.url='http://omdbapi.com/?i=%s' % imdbid[0]
				s.imdbQuery=json.loads(urllib2.urlopen(s.url).read())
				log.debug("added new CI by nfo-file: %s" % s.imdbQuery.get("Title"))
				if s.imdbQuery.get("Response") == "True": idfound=True
			# if no (usable) nfo file given
			if not idfound:
				# get omdb entry by title
				s.url="http://omdbapi.com/?%s" % (urllib.urlencode({"t":kwargs.get("t")}))
				s.imdbQuery=json.loads(urllib2.urlopen(s.url).read())
				if s.imdbQuery["Response"] == "True": 
					log.debug("added new CI: %s" % s.imdbQuery.get("Title"))
				else:
					log.warn("CI not found: %s" % kwargs)
			# set the imdb url
			s.imdburl="http://imdb.com/title/%s" % s.imdbQuery.get("imdbID")
		except urllib2.HTTPError, error:
			raise
		except urllib2.URLError, error:
			raise
		except Exception, e:
			raise
			
	def getidbynfo(s,path):
		nfos=[]
		retList=[]
		files=[]
		# walk path for
		for root,dirs,files in os.walk(path):
			# filter nfo files
			files=(filter(lambda x: x.endswith(".nfo"),files))
			for fl in files:
				nfos.append(os.path.join(root, fl))
		for nfo in nfos:
			f=open(nfo)
			retList.extend(re.findall(r'www.imdb.com/title/(tt[a-zA-Z0-9]*)', f.read()))
		return retList
	def getIMDB(s):
		return s.imdbQuery
	def toHTML(s):
		# builds html from define strings
		return d.ITEM % (s.imdburl,s.imdbQuery["Poster"],s.imdburl,s.imdburl,s.imdbQuery["Title"],s.imdbQuery["Released"],s.imdbQuery["Genre"],s.imdbQuery["Runtime"],s.imdbQuery["imdbRating"],s.imdbQuery["Plot"])
	def toDict(s):
		return {"imdburl":s.imdburl,"poster":s.imdbQuery["Poster"],"title":s.imdbQuery["Title"],"released":s.imdbQuery["Released"],"genre":s.imdbQuery["Genre"],"runtime":s.imdbQuery["Runtime"],"rating":s.imdbQuery["imdbRating"],"plot":s.imdbQuery["Plot"]}

class Folder():
	def __init__(s,path,name,**kwargs):
		s.name=name
		s.size=0
		s.path=path
		log.info("Parsing folder: %s" % s.name)
		s.flist=s.getList(**kwargs)
	def getList(s, **kwargs):
		# hier braeuchts kein path-argument, da s.path eingefuehrt
		retList=[]
		listdir=os.listdir(s.path)
		if kwargs.get("sorted"):
			log.debug("Folder %s will be sorted" % s.name)
			listdir=sorted(listdir)
		for item in listdir:
			try:
				currCI=CI(path=s.path,t=item)
				if currCI.getIMDB().get("imdbID"): retList.append(currCI)
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
	def toHTML(s):
		return d.HEAD % (c.stylesheet,c.title,"%s") + d.NEWLINE.join([ci.toHTML() for ci in s.flist]) + d.TAIL % (s.getSize(),len(s.flist))
	def toDict(s):
		return {"path":s.path,"name":s.name,"cis":[ci.toDict() for ci in s.flist], "size":s.getSize(), "count":len(s.flist)}
