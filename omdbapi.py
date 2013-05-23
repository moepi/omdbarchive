import urllib, urllib2
import os
import json
import logging
import sys
import re
log=logging.getLogger()

MISSINGPOSTERURL="http://i.media-imdb.com/images/mobile/film-40x54.png"

class CI():
	def __init__(s,*args,**kwargs):
		s.path=os.path.join(kwargs.get("path"),kwargs.get("t"))
		imdbid=s.getidbynfo(s.path)
		idfound=False
		try:
			# trying found nfo file
			if imdbid is not None:
				# get omdb entry by id
				# we take the first id, shouldn't be too many
				s.url='http://omdbapi.com/?i=%s' % imdbid
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
		# return first found id, or None
		if not retList:
			return None
		else:
			return retList[0]
	def toDict(s):
		s.imdbQuery.update({"imdbURL":s.imdburl})
		return s.imdbQuery

def overwrite_posters(CIlist,posterdir):
        """
        CIlist is a list of CI Objects.
        posterdir is the directory in which the posters will be downloaded.
        """
        if not os.path.isdir(posterdir): os.makedirs(posterdir)
        posters = os.listdir(posterdir)
	for ci in CIlist:
		if ci["imdbID"]+".jpg" in posters:
			ci["Poster"]="posters/%s.jpg" % ci["imdbID"]
		else:
			if download_poster(ci["Poster"],os.path.join(posterdir,ci["imdbID"]+".jpg")):
				ci["Poster"]="posters/%s.jpg" % ci["imdbID"]
			else:
				if not "missing.jpg" in posters:
					download_poster(MISSINGPOSTERURL,os.path.join(posterdir,"missing.jpg"))
				ci["Poster"]="posters/%s.jpg" % "missing"
	return CIlist

def download_poster(link,filename):
        """
        link is the URL to the poster.
        filename is the destination the file will be downloaded to. Must contain whole path.
        """
        try:
                poster=urllib2.urlopen(link)
                output = open(filename,'wb')
                output.write(poster.read())
                output.close()
        except:
                return False
        return True
