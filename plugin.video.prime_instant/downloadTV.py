#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import base64
import xbmc
import json
import xbmcaddon
import urllib
import urllib2
import shutil
from operator import itemgetter


def download(jsonParams):
    for item in jsonParams:
        videoType = item['type'].encode('utf-8')
        videoID = item['id'].encode('utf-8')
        title = item['title'].encode('utf-8')
        year = item['year'].encode('utf-8')
        filename = (''.join(c for c in unicode(videoID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
        filenameNone = (''.join(c for c in unicode(videoID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".none"
        fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
        fanartFileNone = os.path.join(cacheFolderFanartTMDB, filenameNone)
        coverFile = os.path.join(cacheFolderCoversTMDB, filename)
        coverFileNone = os.path.join(cacheFolderCoversTMDB, filenameNone)
        if not os.path.exists(coverFile) and not os.path.exists(coverFileNone):
            content = opener.open("http://api.themoviedb.org/3/search/"+videoType+"?api_key="+data+"&query="+urllib.quote_plus(title.strip())+"&year="+urllib.quote_plus(year)+"&language=en").read()
            content = json.loads(content)
            #content = sorted(content['results'], key=itemgetter('popularity'), reverse=True)
            try:
                #coverUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+content[0]['poster_path']
                coverUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+content['results'][0]['poster_path']
                contentJPG = opener.open(coverUrl).read()
                fh = open(coverFile, 'wb')
                fh.write(contentJPG)
                fh.close()
            except:
                fh = open(coverFileNone, 'w')
                fh.write("")
                fh.close()
            try:
                #fanartUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+content[0]['backdrop_path']
                fanartUrl = "http://d3gtl9l2a4fn1j.cloudfront.net/t/p/original"+content['results'][0]['backdrop_path']
                contentJPG = opener.open(fanartUrl).read()
                fh = open(fanartFile, 'wb')
                fh.write(contentJPG)
                fh.close()
            except:
                pass

addonID = 'plugin.video.prime_instant'
addon = xbmcaddon.Addon(id=addonID)
data = base64.b64decode("NDE1MDk1NjI4MWNkZTczMWJhZDRkZTMxNTUwNzU4MWI=")
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
opener = urllib2.build_opener()
userAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"
opener.addheaders = [('User-agent', userAgent)]

params = json.loads(urllib.unquote_plus(sys.argv[1]))

try:
    download(params)
except:
    pass
