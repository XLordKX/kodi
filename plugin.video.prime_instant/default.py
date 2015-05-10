#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import mechanize
import cookielib
import sys
import re
import os
import json
import time
import string
import random
import shutil
import subprocess
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addonFolder = downloadScript = xbmc.translatePath('special://home/addons/'+addonID).decode('utf-8')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID).decode('utf-8')

icon = os.path.join(addonFolder, "icon.png").encode('utf-8')


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')
    
if not os.path.exists(os.path.join(addonUserDataFolder, "settings.xml")):
    xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30081)+',10000,'+icon+')')
    addon.openSettings()

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
cj = cookielib.MozillaCookieJar()
downloadScript = os.path.join(addonFolder, "download.py").encode('utf-8')
downloadScriptTV = os.path.join(addonFolder, "downloadTV.py").encode('utf-8')
cacheFolder = os.path.join(addonUserDataFolder, "cache")
cacheFolderCoversTMDB = os.path.join(cacheFolder, "covers")
cacheFolderFanartTMDB = os.path.join(cacheFolder, "fanart")
addonFolderResources = os.path.join(addonFolder, "resources")
defaultFanart = os.path.join(addonFolderResources, "fanart.png")
libraryFolder = os.path.join(addonUserDataFolder, "library")
libraryFolderMovies = os.path.join(libraryFolder, "Movies")
libraryFolderTV = os.path.join(libraryFolder, "TV")
cookieFile = os.path.join(addonUserDataFolder, "cookies")
debugFile = os.path.join(addonUserDataFolder, "debug")
preferAmazonTrailer = addon.getSetting("preferAmazonTrailer") == "true"
showNotification = addon.getSetting("showNotification") == "true"
showOriginals = addon.getSetting("showOriginals") == "true"
showLibrary = addon.getSetting("showLibrary") == "true"
showAvailability = addon.getSetting("showAvailability") == "true"
showKids = addon.getSetting("showKids") == "true"
forceView = addon.getSetting("forceView") == "true"
updateDB = addon.getSetting("updateDB") == "true"
useTMDb = addon.getSetting("useTMDb") == "true"
watchlistOrder = addon.getSetting("watchlistOrder")
watchlistOrder = ["DATE_ADDED_DESC", "TITLE_ASC"][int(watchlistOrder)]
maxBitrate = addon.getSetting("maxBitrate")
maxBitrate = [300, 600, 900, 1350, 2000, 2500, 4000, 6000, 10000, -1][int(maxBitrate)]
maxDevices = 3
maxDevicesWaitTime = 120
selectLanguage = addon.getSetting("selectLanguage")
siteVersion = addon.getSetting("siteVersion")
apiMain = ["atv-ps", "atv-ps-eu", "atv-ps-eu"][int(siteVersion)]
rtmpMain = ["azusfms", "azeufms", "azeufms"][int(siteVersion)]
siteVersion = ["com", "co.uk", "de"][int(siteVersion)]
viewIdMovies = addon.getSetting("viewIdMovies")
viewIdShows = addon.getSetting("viewIdShows")
viewIdSeasons = addon.getSetting("viewIdSeasons")
viewIdEpisodes = addon.getSetting("viewIdEpisodes")
viewIdDetails = addon.getSetting("viewIdDetails")
urlMain = "http://www.amazon."+siteVersion
urlMainS = "https://www.amazon."+siteVersion
addon.setSetting('email', '')
addon.setSetting('password', '')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (X11; U; Linux i686; de-DE) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.127 Large Screen Safari/533.4 GoogleTV/ 162671"
opener.addheaders = [('User-agent', userAgent)]
deviceTypeID = "A324MFXUEZFF7B"

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not os.path.isdir(cacheFolder):
    os.mkdir(cacheFolder)
if not os.path.isdir(cacheFolderCoversTMDB):
    os.mkdir(cacheFolderCoversTMDB)
if not os.path.isdir(cacheFolderFanartTMDB):
    os.mkdir(cacheFolderFanartTMDB)
if not os.path.isdir(libraryFolder):
    os.mkdir(libraryFolder)
if not os.path.isdir(libraryFolderMovies):
    os.mkdir(libraryFolderMovies)
if not os.path.isdir(libraryFolderTV):
    os.mkdir(libraryFolderTV)
if os.path.exists(cookieFile):
    cj.load(cookieFile)



def index():
    loginResult = login()
    if loginResult=="prime":
        addDir(translation(30002), "", 'browseMovies', "")
        addDir(translation(30003), "", 'browseTV', "")
        xbmcplugin.endOfDirectory(pluginhandle)
    elif loginResult=="noprime":
        listOriginals()
    elif loginResult=="none":
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30082)+',10000,'+icon+')')


def browseMovies():
    addDir(translation(30004), urlMain+"/gp/video/watchlist/movie/?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if showLibrary:
        addDir(translation(30005), urlMain+"/gp/video/library/movie?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if siteVersion=="de":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356018031&sort=popularity-rank", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015915031%2Cp_n_theme_browse-bin%3A3015972031%2Cp_85%3A3282148031&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031&sort=date-desc-rank", 'listMovies', "")
        addDir(translation(30009), urlMain+"/s/?n=4963842031", 'listMovies', "")
        addDir(translation(30999), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356018031%2Cn%3A4225009031&sort=popularity-rank", 'listMovies', "")
    elif siteVersion=="com":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613704011&sort=popularity-rank", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30012), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=feature_five_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30013), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613704011&pickerToList=feature_six_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_theme_browse-bin%3A2650365011&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613704011&sort=date-desc-rank", 'listMovies', "")
    elif siteVersion=="co.uk":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356010031&sort=popularity-rank", 'listMovies', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "movie")
        addDir(translation(30014), "", 'listDecadesMovie', "")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_theme_browse-bin%3A3046745031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356010031&sort=date-desc-rank", 'listMovies', "")
    addDir(translation(30015), "movies", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def browseTV():
    addDir(translation(30004), urlMain+"/gp/video/watchlist/tv/?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if showLibrary:
        addDir(translation(30005), urlMain+"/gp/video/library/tv/?ie=UTF8&show=all&sort="+watchlistOrder, 'listWatchList', "")
    if siteVersion=="de":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356019031&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356019031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015916031%2Cp_n_theme_browse-bin%3A3015972031%2Cp_85%3A3282148031&ie=UTF8", 'listShows', "")
        addDir(translation(30010), urlMain+"/gp/search/ajax/?_encoding=UTF8&keywords=[OV]&rh=n%3A3010075031%2Cn%3A3015916031%2Ck%3A[OV]%2Cp_85%3A3282148031&sort=date-desc-rank", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3279204031%2Cn%3A3010075031%2Cn%3A3015916031&sort=date-desc-rank", 'listShows', "")
        addDir(translation(30999), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356019031%2Cn%3A4225009031&sort=popularity-rank", 'listShows', "")
    elif siteVersion=="com":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30012), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_five_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        addDir(translation(30013), urlMain+"/gp/search/other/?rh=n%3A2676882011%2Cn%3A7613705011&pickerToList=feature_six_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613705011%2Cp_n_theme_browse-bin%3A2650365011&sort=csrank&ie=UTF8", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A2858778011%2Cn%3A7613705011&sort=date-desc-rank", 'listShows', "")
    elif siteVersion=="co.uk":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356011031&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356011031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356011031%2Cp_n_theme_browse-bin%3A3046745031&sort=popularity-rank&ie=UTF8", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010085031%2Cn%3A3356011031&sort=date-desc-rank", 'listShows', "")
    if showOriginals:
        addDir("Amazon Originals: Pilot Season 2015", "", 'listOriginals', "")
    addDir(translation(30015), "tv", 'search', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listDecadesMovie():
    if siteVersion=="de":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289642031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289643031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289644031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289645031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289646031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289647031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356018031%2Cp_n_feature_three_browse-bin%3A3289648031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    elif siteVersion=="com":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651255011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651256011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651257011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651258011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651259011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651260011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A2676882011%2Cn%3A7613704011%2Cp_n_feature_three_browse-bin%3A2651261011&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    elif siteVersion=="co.uk":
        addDir(translation(30016), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289666031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30017), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289667031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30018), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289668031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30019), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289669031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30020), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289670031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30021), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289671031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
        addDir(translation(30022), urlMain+"/gp/search/ajax/?rh=n%3A3280626031%2Cn%3A!3010086031%2Cn%3A3356010031%2Cp_n_feature_three_browse-bin%3A3289672031&sort=popularity-rank&ie=UTF8", 'listMovies', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listOriginals():
    if siteVersion=="de":
        content = opener.open(urlMain+"/b/?ie=UTF8&node=5457207031").read()
    elif siteVersion=="com":
        content = opener.open(urlMain+"/b/?ie=UTF8&node=9940930011").read()
    elif siteVersion=="co.uk":
        content = opener.open(urlMain+"/b/?ie=UTF8&node=5687760031").read()
    debug(content)
    #match = re.compile("token : '(.+?)'", re.DOTALL).findall(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    content = content[content.find('<map name="pilots'):]
    content = content[:content.find('</map>')]
    spl = content.split('shape="rect"')
    thumbs = {}
    thumbs['maninthehighcastle'] = 'http://ecx.images-amazon.com/images/I/5114a5G6oQL.jpg'
    thumbs['cocked'] = 'http://ecx.images-amazon.com/images/I/51ky16-xESL.jpg'
    thumbs['maddogs'] = 'http://ecx.images-amazon.com/images/I/61mWRYn7U2L.jpg'
    thumbs['thenewyorkerpresents'] = 'http://ecx.images-amazon.com/images/I/41Yb8SUjMzL.jpg'
    thumbs['pointofhonor'] = 'http://ecx.images-amazon.com/images/I/51OBmT5ARUL.jpg'
    thumbs['downdog'] = 'http://ecx.images-amazon.com/images/I/51N2zkhOxGL.jpg'
    thumbs['salemrogers'] = 'http://ecx.images-amazon.com/images/I/510nXRWkoaL.jpg'
    thumbs['table58'] = 'http://ecx.images-amazon.com/images/I/51AIPgzNiWL.jpg'
    thumbs['buddytechdetective'] = 'http://ecx.images-amazon.com/images/I/513pbjgDLYL.jpg'
    thumbs['sarasolvesit'] = 'http://ecx.images-amazon.com/images/I/51Y5G5RbLUL.jpg'
    thumbs['stinkyanddirty'] = 'http://ecx.images-amazon.com/images/I/51WzytCUmdL.jpg'
    thumbs['niko'] = 'http://ecx.images-amazon.com/images/I/51XjJrg9JLL.jpg'
    thumbs['justaddmagic'] = 'http://ecx.images-amazon.com/images/I/5159YFd0hQL.jpg'
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile("/gp/product/(.+?)/", re.DOTALL).findall(entry)
        videoID = match[0]
        match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        titleT = title.lower().replace(' ', '').strip()
        titleT = titleT.replace("pointofhonour", "pointofhonor")
        titleT = titleT.replace("buddytechdective", "buddytechdetective")
        titleT = titleT.replace("buddytechdetectives", "buddytechdetective")
        titleT = titleT.replace("thestinkyanddirtyshow", "stinkyanddirty")
        titleT = titleT.replace("nikkoandtheswordoflight", "niko")
        titleT = titleT.replace("nikoandtheswordoflight", "niko")
        thumb = ""
        if titleT in thumbs:
            thumb = thumbs[titleT]
        addShowDir(title, videoID, "listSeasons", thumb, "tv")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode(500)')

def parseWatchListNew(content):
    entries=re.compile('\<div\s+class\s*=\s*"grid-list-item\s+downloadable.+?$', re.DOTALL).findall(content)
    if entries:
        entry=entries[0]
        elements=[]

        # for all entries, do the same
        while True:
            # serach for beginning!
            match=re.compile('^\s*\<div\s+class\s*=\s*"grid-list-item\s+downloadable.*?\>', re.DOTALL).findall(entry)
            if match:
                index=entry.find(match[0])+len(match[0])
                entry=entry[index:]
                depth=1
                element=match[0]

                while depth > 0:
                    match=re.compile('^.*?\<div.*?\>', re.DOTALL).findall(entry)
                    matchend=re.compile('^.*?\<\/div\>', re.DOTALL).findall(match[0])
                    if matchend:
                        entry=entry[len(matchend[0]):]
                        depth=depth-1
                        element+=matchend[0]
                    else:
                        entry=entry[len(match[0]):]
                        depth=depth+1
                        element+=match[0]
                elements.append(element)
            else:
                break

    dlParams = []
    showEntries = []
    for entry in elements:
        if "/library/" in url or ("/watchlist/" in url and ("class='prime-meta'" in entry or 'class="prime-logo"' in entry or "class='item-green'" in entry or 'class="packshot-sash' in entry)):
            match = re.compile('data-prod-type="(.+?)"', re.DOTALL).findall(entry)
            if match:
                if match[0] == "downloadable_tv_season":
                    videoType = "tv"
                else:
                    videoType = "movie"
                match = re.compile('id="(.+?)"', re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                avail=''
                if showAvailability:
                    match = re.compile('\<span\s+class\s*=\s*"packshot-message"\s*\>(.+?)\<\/span\>', re.DOTALL).findall(entry)
                    if match:
                        avail=" - " + cleanInput(match[0])
                title = cleanTitle(title)+avail
                if videoType=="tv":
                    title = cleanSeasonTitle(title)+avail
                    if title in showEntries:
                        continue
                    showEntries.append(title)
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'thumb':thumbUrl, 'year':''})

    return dlParams

def parseWatchListOld(content):
    dlParams = []
    showEntries = []
    spl = content.split('<div class="innerItem"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</td>')]
        if "/library/" in url or ("/watchlist/" in url and ("class='prime-meta'" in entry or 'class="prime-logo"' in entry or "class='item-green'" in entry or 'class="packshot-sash' in entry)):
            match = re.compile('data-prod-type="(.+?)"', re.DOTALL).findall(entry)
            if match:
                videoType = match[0]
                match = re.compile('id="(.+?)"', re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                if videoType=="tv":
                    title = cleanSeasonTitle(title)
                    if title in showEntries:
                        continue
                    showEntries.append(title)
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'thumb':thumbUrl, 'year':''})
    return dlParams


def listWatchList(url):
    content = opener.open(url).read()
    debug(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])

    dlParams = []
    if "grid-list-item" in content:
        dlParams = parseWatchListNew(content)
    else:
        dlParams = parseWatchListOld(content)

    videoType = ""
    for entry in dlParams:
        videoType = entry['type']
        if entry['type'] == "movie":
            addLinkR(entry['title'], entry['id'], "playVideo", entry['thumb'], entry['type'])
        else:
            addShowDirR(entry['title'], entry['id'], "playVideo", entry['thumb'], entry['type'])

    if videoType == "movie":
        xbmcplugin.setContent(pluginhandle, "movies")
    else:
        xbmcplugin.setContent(pluginhandle, "tvshows")
    if useTMDb and videoType == "movie":
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(str(dlParams))+')')
    elif useTMDb:
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(str(dlParams))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        if videoType == "movie":
            xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')
        else:
            xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listMovies(url):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(url).read()
    debug(content)
    content = content.replace("\\","")
    if 'id="catCorResults"' in content:
        content = content[:content.find('id="catCorResults"')]
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('id="result_')
    dlParams = []
    match = re.compile('\<\/span\>(\<a class="a-link-normal a-text-normal" href=".+?"\>.+?\<\/a\>)', re.DOTALL).findall(content)
    if match:
        textMatch=re.compile('\>(.+?)\<', re.DOTALL).findall(match[0])
        linkMatch=re.compile('href="(.+?)"\>', re.DOTALL).findall(match[0])
        addDir(textMatch[0], urlMain+linkMatch[0].replace("&amp;","&"), "listMovies", "DefaultTVShows.png")
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('asin="(.+?)"', re.DOTALL).findall(entry)
        if match and ">Prime Instant Video<" in entry:
            videoID = match[0]
            match1 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('class="ilt2">(.+?)<', re.DOTALL).findall(entry)
            title = ""
            if match1:
                title = match1[0]
            elif match2:
                title = match2[0]
            title = cleanTitle(title)
            match1 = re.compile('class="a-size-small a-color-secondary">(.+?)<', re.DOTALL).findall(entry)
            match2 = re.compile('class="med reg subt">(.+?)<', re.DOTALL).findall(entry)
            year = ""
            if match1:
                year = match1[0].strip()
            if match2:
                year = match2[0].strip()
            dlParams.append({'type':'movie', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':year})
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumbUrl = match[0].replace(".jpg", "")
            thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
            match = re.compile('data-action="s-watchlist-add".+?class="a-button a-button-small(.+?)"', re.DOTALL).findall(entry)
            if match and match[0]==" s-hidden":
                addLinkR(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
            else:
                addLink(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
    if useTMDb:
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(str(dlParams))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listMovies", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listShows(url):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = opener.open(url).read()
    debug(content)
    content = content.replace("\\","")
    if 'id="catCorResults"' in content:
        content = content[:content.find('id="catCorResults"')]
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('id="result_')
    showEntries = []
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('asin="(.+?)"', re.DOTALL).findall(entry)
        if match and ">Prime Instant Video<" in entry:
            videoID = match[0]
            match1 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('class="ilt2">(.+?)<', re.DOTALL).findall(entry)
            title = ""
            if match1:
                title = match1[0]
            elif match2:
                title = match2[0]
            title = cleanTitle(title)
            title = cleanSeasonTitle(title)
            if title in showEntries:
                continue
            showEntries.append(title)
            match1 = re.compile('class="a-size-small a-color-secondary">(.+?)<', re.DOTALL).findall(entry)
            match2 = re.compile('class="med reg subt">(.+?)<', re.DOTALL).findall(entry)
            year = ""
            if match1:
                year = match1[0].strip()
            if match2:
                year = match2[0].strip()
            dlParams.append({'type':'tv', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':year})
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumbUrl = match[0].replace(".jpg", "")
            thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
            match = re.compile('data-action="s-watchlist-add".+?class="a-button a-button-small(.*?)"', re.DOTALL).findall(entry)
            if match and match[0]==" s-hidden":
                addShowDirR(title, videoID, "listSeasons", thumbUrl, "tv")
            else:
                addShowDir(title, videoID, "listSeasons", thumbUrl, "tv")
    if useTMDb:
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(str(dlParams))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listShows", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSimilarMovies(videoID):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = opener.open(urlMain+"/gp/product/"+videoID).read()
    debug(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('<li class="packshot')
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        if 'packshot-sash-prime' in entry:
            match = re.compile("data-type='downloadable_(.+?)'", re.DOTALL).findall(entry)
            if match:
                videoType = match[0]
                match = re.compile("asin='(.+?)'", re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                dlParams.append({'type':'movie', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                if videoType == "movie":
                    addLinkR(title, videoID, "playVideo", thumbUrl, videoType)
    if useTMDb:
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(str(dlParams))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listSimilarShows(videoID):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = opener.open(urlMain+"/gp/product/"+videoID).read()
    debug(content)
    match = re.compile("token : '(.+?)'", re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    spl = content.split('<li class="packshot')
    showEntries = []
    dlParams = []
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        if 'packshot-sash-prime' in entry:
            match = re.compile("data-type='downloadable_(.+?)'", re.DOTALL).findall(entry)
            if match:
                videoType = match[0]
                match = re.compile("asin='(.+?)'", re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('alt="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]
                title = cleanTitle(title)
                dlParams.append({'type':'tv', 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = match[0].replace(".jpg", "")
                    thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                if videoType=="tv_season":
                    videoType="tv"
                    title = cleanSeasonTitle(title)
                    if title in showEntries:
                        continue
                    showEntries.append(title)
                    addShowDirR(title, videoID, "listSeasons", thumbUrl, videoType)
    if useTMDb:
        dlParams = json.dumps(unicode(dlParams))
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(str(dlParams))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSeasons(seriesName, seriesID, thumb):
    xbmcplugin.setContent(pluginhandle, "seasons")
    content = opener.open(urlMain+"/gp/product/"+seriesID).read()
    debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    contentMain = content
    content = content[content.find('<select name="seasonAsinAndRef"'):]
    content = content[:content.find('</select>')]
    match = re.compile('<option value="(.+?):.+?data-a-html-content="(.+?)"', re.DOTALL).findall(content)
    if match:
        for seasonID, title in match:
            if "dv-dropdown-prime" in title:
                if "\n" in title:
                    title = title[:title.find("\n")]
                addSeasonDir(title, seasonID, 'listEpisodes', thumb, seriesName, seriesID)
        xbmcplugin.endOfDirectory(pluginhandle)
        xbmc.sleep(100)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIdSeasons+')')
    else:
        listEpisodes(seriesID, seriesID, thumb, contentMain)


def listEpisodes(seriesID, seasonID, thumb, content="", seriesName=""):
    xbmcplugin.setContent(pluginhandle, "episodes")
    if not content:
        content = opener.open(urlMain+"/gp/product/"+seasonID).read()
    debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    matchSeason = re.compile('"seasonNumber":"(.+?)"', re.DOTALL).findall(content)
    seasonNr="0"
    if matchSeason:
        seasonNr=matchSeason[0]
    spl = content.split('href="'+urlMain+'/gp/product')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        match = re.compile('class="episode-title">(.+?)<', re.DOTALL).findall(entry)
        if match and ('class="prime-logo-small"' in entry or 'class="episode-status cell-free"' in entry or 'class="episode-status cell-owned"' in entry):
            title = match[0]
            title = cleanTitle(title)
            episodeNr = title[:title.find('.')]
            title = title[title.find('.')+1:].strip()
            match = re.compile('/(.+?)/', re.DOTALL).findall(entry)
            episodeID = match[0]
            match = re.compile('<p>.+?</span>\s*(.+?)\s*</p>', re.DOTALL).findall(entry)
            desc = ""
            if match:
                desc = cleanTitle(match[0])
            length = ""
            match1 = re.compile('class="dv-badge runtime">(.+?)h(.+?)min<', re.DOTALL).findall(entry)
            match2 = re.compile('class="dv-badge runtime">(.+?)Std.(.+?)Min.<', re.DOTALL).findall(entry)
            match3 = re.compile('class="dv-badge runtime">(.+?)min<', re.DOTALL).findall(entry)
            match4 = re.compile('class="dv-badge runtime">(.+?)Min.<', re.DOTALL).findall(entry)
            if match1:
                length = str(int(match1[0][0].strip())*60+int(match1[0][1].strip()))
            elif match2:
                length = str(int(match2[0][0].strip())*60+int(match2[0][1].strip()))
            elif match3:
                length = match3[0].strip()
            elif match4:
                length = match4[0].strip()
            match = re.compile('class="dv-badge release-date">(.+?)<', re.DOTALL).findall(entry)
            aired = ""
            if match:
                aired = match[0]+"-01-01"
            match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            if match:
                thumb = match[0].replace("._SX133_QL80_.jpg","._SX400_.jpg")
            match = re.compile('class="progress-bar">.+?width: (.+?)%', re.DOTALL).findall(entry)
            playcount = 0
            if match:
                percentage = match[0]
                if int(percentage)>95:
                    playcount = 1
            addEpisodeLink(title, episodeID, 'playVideo', thumb, desc, length, seasonNr, episodeNr, seriesID, playcount, aired, seriesName)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdEpisodes+')')


def listGenres(url, videoType):
    content = opener.open(url).read()
    debug(content)
    content = content[content.find('<ul class="column vPage1">'):]
    content = content[:content.find('</div>')]
    match = re.compile('href="(.+?)">.+?>(.+?)</span>.+?>(.+?)<', re.DOTALL).findall(content)
    for url, title, nr in match:
        if videoType=="movie":
            addDir(cleanTitle(title)+nr.replace("&nbsp;"," "), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listMovies', "")
        else:
            addDir(cleanTitle(title), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listShows', "")
    xbmcplugin.endOfDirectory(pluginhandle)

def printLogInline(ptext):
    if (True):
        print(ptext)

def selectLang(content):
    content = content[content.find('class="dv-toggle-box dv-tb-closed">'):content.find('<span id="dv-mta-submit-announce"')]
    matchlo = re.compile('<option value="(.+?)".*?>(.+?)</option>', re.DOTALL).findall(content)
    if len(matchlo) > 0:
        opt = []
        for i,val in enumerate(matchlo):
            opt.append([val[0].strip(), val[1].strip()])
        return opt
    return None

def playVideo(videoID, selectQuality=False, playTrailer=False):
    streamTitles = []
    streamURLs = []
    cMenu = False
    if selectQuality:
        cMenu = True
    if maxBitrate==-1:
        selectQuality = True
    content=opener.open(urlMain+"/dp/"+videoID).read()
    hasTrailer = False
    if '"hasTrailer":true' in content:
        hasTrailer = True
    matchCID=re.compile('"customerID":"(.+?)"').findall(content)
    if matchCID:
        matchTitle=re.compile('"contentRating":".+?","name":"(.+?)"', re.DOTALL).findall(content)
        matchThumb=re.compile('"video":.+?"thumbnailUrl":"(.+?)"', re.DOTALL).findall(content)
        matchToken=re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
        matchMID=re.compile('"marketplaceID":"(.+?)"').findall(content)
        avail_langs = selectLang(content)
        if not playTrailer or (playTrailer and hasTrailer and preferAmazonTrailer and siteVersion!="com"):
            content=opener.open(urlMainS+'/gp/video/streaming/player-token.json?callback=jQuery1640'+''.join(random.choice(string.digits) for x in range(18))+'_'+str(int(time.time()*1000))+'&csrftoken='+urllib.quote_plus(matchToken[0])+'&_='+str(int(time.time()*1000))).read()
            matchToken=re.compile('"token":"(.+?)"', re.DOTALL).findall(content)
        content = ""
        if playTrailer and hasTrailer and preferAmazonTrailer and siteVersion!="com":
            content = opener.open('https://'+apiMain+'.amazon.com/cdp/catalog/GetStreamingTrailerUrls?version=1&format=json&firmware=WIN%2011,7,700,224%20PlugIn&marketplaceID='+urllib.quote_plus(matchMID[0])+'&token='+urllib.quote_plus(matchToken[0])+'&deviceTypeID='+deviceTypeID+'&asin='+videoID+'&customerID='+urllib.quote_plus(matchCID[0])+'&deviceID='+urllib.quote_plus(matchCID[0])+str(int(time.time()*1000))+videoID).read()
        elif not playTrailer:
            if (selectLanguage == "1") and (avail_langs is not None):
                dialog = xbmcgui.Dialog()
                sel_lang = []
                for val in avail_langs:
                    sel_lang.append(val[1])
                lnr = dialog.select(translation(30050), sel_lang)
                if lnr>=0:
                    playlanguage = "&audioTrackId=" + avail_langs[lnr][0]
                else:
                    playlanguage = ""
            else:
                playlanguage = ""
            content = opener.open('https://'+apiMain+'.amazon.com/cdp/catalog/GetStreamingUrlSets?version=1&format=json&firmware=WIN%2011,7,700,224%20PlugIn'+playlanguage+'&marketplaceID='+urllib.quote_plus(matchMID[0])+'&token='+urllib.quote_plus(matchToken[0])+'&deviceTypeID='+deviceTypeID+'&asin='+videoID+'&customerID='+urllib.quote_plus(matchCID[0])+'&deviceID='+urllib.quote_plus(matchCID[0])+str(int(time.time()*1000))+videoID).read()
        elif playTrailer:
            try:
                strT = ""
                if siteVersion=="de":
                    strT = "+german"
                contentT = opener.open("http://gdata.youtube.com/feeds/api/videos?vq="+cleanTitle(matchTitle[0]).replace(" ", "+")+"+trailer"+strT+"&racy=include&orderby=relevance").read()
                match = re.compile('<id>http://gdata.youtube.com/feeds/api/videos/(.+?)</id>', re.DOTALL).findall(contentT.split('<entry>')[1])
                xbmc.Player().play("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + match[0])
            except:
                pass
        debug(content)
        if content:
            if not "SUCCESS" in str(content):
                content = json.loads(content)
                ediag = xbmcgui.Dialog()
                acode = str(content['message']['body']['code'])
                amessage = str(content['message']['body']['message'])
                ediag.ok('Amazon meldet: '+ acode, amessage)
            else:
                content = json.loads(content)
                thumbUrl = matchThumb[0].replace(".jpg", "")
                thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
                contentT = ""
                try:
                    contentT = content['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
                except:
                    try:
                        contentT = content['message']['body']['streamingURLInfoSet']['streamingURLInfo']
                    except:
                        pass
                if contentT:
                    url = ''
                    for item in contentT:
                        if selectQuality:
                            streamTitles.append(str(item['bitrate'])+"kb")
                            streamURLs.append(item['url'])
                            url = item['url']
                        elif item['bitrate']<=maxBitrate:
                            url = item['url']
                    if not rtmpMain in url:
                        try:
                            if selectQuality:
                                streamTitles = []
                                streamURLs = []
                            for item in content['message']['body']['urlSets']['streamingURLInfoSet'][1]['streamingURLInfo']:
                                if selectQuality:
                                    streamTitles.append(str(item['bitrate'])+"kb")
                                    streamURLs.append(item['url'])
                                elif item['bitrate']<=maxBitrate:
                                    url = item['url']
                        except:
                            pass
                    if url:
                        if selectQuality:
                            dialog = xbmcgui.Dialog()
                            nr=dialog.select(translation(30059), streamTitles)
                            if nr>=0:
                              url=streamURLs[nr]
                        if url.startswith("rtmpe"):
                            url = 'http://'+rtmpMain+'-vodfs.fplive.net/' + url[url.find('mp4:')+4:]
                            if playTrailer or (selectQuality and cMenu):
                                listitem = xbmcgui.ListItem(cleanTitle(matchTitle[0]), path=url, thumbnailImage=thumbUrl)
                                xbmc.Player().play(url, listitem)
                            else:
                                listitem = xbmcgui.ListItem(cleanTitle(matchTitle[0]), path=url, thumbnailImage=thumbUrl)
                                xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
                        elif url.startswith("http"):
                            dialog = xbmcgui.Dialog()
                            if dialog.yesno('Info', translation(30085)):
                                content=opener.open(urlMainS+"/gp/video/settings/ajax/player-preferences-endpoint.html", "rurl="+urllib.quote_plus(urlMainS+"/gp/video/settings")+"&csrfToken="+urllib.quote_plus(addon.getSetting('csrfToken'))+"&aiv-pp-toggle=flash").read()
                                xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30086)+',10000,'+icon+')')
                                playVideo(videoID, selectQuality)
                    else:
                        url = ''
                        diag = xbmcgui.Dialog()
                        diag.ok(translation(30092), translation(30093))
                else:
                    diag = xbmcgui.Dialog()
                    diag.ok(translation(30094), translation(30095))
    else:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30082)+',10000,'+icon+')')
   

def showInfo(videoID):
    xbmcplugin.setContent(pluginhandle, "movies")
    content=opener.open(urlMain+"/dp/"+videoID+"?_encoding=UTF8").read()

    match=re.compile('property="og:title" content="Watch (.+?) Online - Amazon Instant Video"', re.DOTALL).findall(content)
    title = match[0]
    match=re.compile('class="release-year".*?>(.+?)<', re.DOTALL).findall(content)
    year = match[0]
    title = title+" ("+year+")"
    title = cleanTitle(title)
    match=re.compile('property="og:image" content="(.+?)"', re.DOTALL).findall(content)
    thumb = match[0].replace(".jpg", "")
    thumb = thumb[:thumb.rfind(".")]+".jpg"
    match=re.compile('"director":.+?"name":"(.+?)"', re.DOTALL).findall(content)
    director = match[0].replace(",",", ")
    match=re.compile('"actor":.+?"name":"(.+?)"', re.DOTALL).findall(content)
    actors = match[0].replace(",",", ")
    match=re.compile('property="og:duration" content="(.+?)"', re.DOTALL).findall(content)
    length = str(int(match[0])/60)+" min."
    match=re.compile('property="og:rating" content="(.+?)"', re.DOTALL).findall(content)
    rating = match[0]
    match=re.compile('property="og:rating_count" content="(.+?)"', re.DOTALL).findall(content)
    ratingCount = match[0]
    match=re.compile('property="og:description" content="(.+?)"', re.DOTALL).findall(content)
    description = cleanTitle(match[0])
    match=re.compile('"genre":"(.+?)"', re.DOTALL).findall(content)
    genre = ""
    if match:
        genre = cleanTitle(match[0])
    addLink(title, videoID, "playVideo", thumb, videoType="movie", desc=description, duration=length, year=year, mpaa="", director=director, genre=genre, rating=rating)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdDetails+')')
    try:
        wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        wnd.getControl(wnd.getFocusId()).selectItem(1)
    except:
        pass
        

def deleteCookies():
    if os.path.exists(cookieFile):
        os.remove(cookieFile)


def deleteCache():
    if os.path.exists(cacheFolder):
        try:
            shutil.rmtree(cacheFolder)
        except:
            shutil.rmtree(cacheFolder)


def search(type):
    keyboard = xbmc.Keyboard('', translation(30015))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        if siteVersion=="de":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356018031&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356019031&field-keywords="+search_string)
        elif siteVersion=="com":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613704011&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613705011&field-keywords="+search_string)
        elif siteVersion=="co.uk":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356010031&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356011031&field-keywords="+search_string)
        


def addToQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = opener.open(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_add?token="+urllib.quote_plus(addon.getSetting('csrfToken'))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video").read()
    if showNotification:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30088)+',3000,'+icon+')')


def removeFromQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = opener.open(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_remove?token="+urllib.quote_plus(addon.getSetting('csrfToken'))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video").read()
    xbmc.executebuiltin("Container.Refresh")
    if showNotification:
        xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30089)+',3000,'+icon+')')


def login():
    content = opener.open(urlMain).read()
    if '"isPrime":1' in content:
        return "prime"
    elif 'id="nav-item-signout"' in content:
        return "noprime"
    else:
        content = ""
        keyboard = xbmc.Keyboard('', translation(30090))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            email = keyboard.getText()
            keyboard = xbmc.Keyboard('', translation(30091), True)
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                password = keyboard.getText()
                br = mechanize.Browser()
                br.set_cookiejar(cj)
                br.set_handle_robots(False)
                br.addheaders = [('User-agent', userAgent)]
                content = br.open(urlMainS+"/gp/sign-in.html")
                br.select_form(name="signIn")
                br["email"] = email
                br["password"] = password
                content = br.submit().read()
                cj.save(cookieFile)
                content = opener.open(urlMain).read()
        if '"isPrime":1' in content:
            return "prime"
        elif 'id="nav-item-signout"' in content:
            return "noprime"
        else:
            return "none"


def cleanInput(str):

    str = str.replace("&amp;","&").replace("&#39;","'").replace("&eacute;","é").replace("&auml;","ä").replace("&ouml;","ö").replace("&uuml;","ü").replace("&Auml;","Ä").replace("&Ouml;","Ö").replace("&Uuml;","Ü").replace("&szlig;","ß").replace("&hellip;","…")
    str = str.replace("&#233;","é").replace("&#228;","ä").replace("&#246;","ö").replace("&#252;","ü").replace("&#196;","Ä").replace("&#214;","Ö").replace("&#220;","Ü").replace("&#223;","ß").replace("&euml;","ë").replace("&Euml;","Ë")
    str = str.replace('&quot;','"').replace('&gt;','>').replace('&lt;','<').replace("&euro;","€").replace("&ntilde;","ñ").replace("&pound;","£").replace("&sect;","§").replace("&oslash;","ø")
    str = str.replace("&acirc;","â").replace("&aacute;","á").replace("&agrave;","à").replace("&ecirc;","ê").replace("&eacute;","é").replace("&egrave;","è").replace("&icirc;","î").replace("&iacute;","í").replace("&igrave;","ì")
    str = str.replace("&ocirc;","ô").replace("&oacute;","ó").replace("&ograve;","ò").replace("&ucirc;","û").replace("&uacute;","ú").replace("&ugrave;","ù").replace("&ccedil;","ç")

    printable = string.printable+"€£ñêéèëäöüËÄÖÜßâáàôóòûúùîíìøç…"
    
    newStr=''
    lastByte='\xff'
    for c in str:
        if c == '\xe4' or ( lastByte == '\x00' and c == '\xe4' ) or ( lastByte == '\xc3' and c == '\xa4'):
            newStr+='\xc3\xa4'
            lastByte=c
        elif c == '\xf6' or ( lastByte == '\x00' and c == '\xf6' ) or ( lastByte == '\xc3' and c == '\xb6'):
            newStr+='\xc3\xb6'
            lastByte=c
        elif c == '\xfc' or ( lastByte == '\x00' and c == '\xfc' ) or ( lastByte == '\xc3' and c == '\xbc') or ( lastByte == '\xc3' and ( c != '\xa4' and c != '\xb6' and c != '\x84' and c != '\x69' and c != '\x9c' and c != '\x9f' and c != '\xa9' ) ):
            newStr+='\xc3\xbc'
            lastByte=c
        elif c == '\xc4' or ( lastByte == '\x00' and c == '\xc4' ) or ( lastByte == '\xc3' and c == '\x84'):
            newStr+='\xc3\x84'
            lastByte=c
        elif c == '\xd6' or ( lastByte == '\x00' and c == '\xd6' ) or ( lastByte == '\xc3' and c == '\x69'):
            newStr+='\xc3\x96'
            lastByte=c
        elif c == '\xdc' or ( lastByte == '\x00' and c == '\xdc' ) or ( lastByte == '\xc3' and c == '\x9c'):
            newStr+='\xc3\x9c'
            lastByte=c
        elif c == '\xdf' or ( lastByte == '\x00' and c == '\xdf' ) or ( lastByte == '\xc3' and c == '\x9f'):
            newStr+='\xc3\x9f'
            lastByte=c
        elif c == '\xe9' or ( lastByte == '\x00' and c == '\xe9' ) or ( lastByte == '\xc3' and c == '\xa9'):
            newStr+='\xc3\xa9'
            lastByte=c
        elif c == '\x00' or c == '\xc3':
            lastByte=c
        else:
            newStr+=c
            lastByte=c

    newStr = filter(lambda c: c in printable, newStr)
    return newStr


def cleanTitle(title):
    if "[HD]" in title:
        title = title[:title.find("[HD]")]
    return cleanInput(title)


def cleanSeasonTitle(title):
    if ": The Complete" in title:
        title = title[:title.rfind(": The Complete")]
    if "Season" in title:
        title = title[:title.rfind("Season")]
    if "Staffel" in title:
        title = title[:title.rfind("Staffel")]
    if "Volume" in title:
        title = title[:title.rfind("Volume")]
    if "Series" in title:
        title = title[:title.rfind("Series")]
    return title.strip(" -,")


def cleanTitleTMDB(title):
    if "[" in title:
        title = title[:title.find("[")]    
    if " OmU" in title:
        title = title[:title.find(" OmU")]    
    return title


def addMovieToLibrary(movieID, title):
    movieFolderName = (''.join(c for c in unicode(title, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
    dir = os.path.join(libraryFolderMovies, movieFolderName)
    if not os.path.isdir(dir):
        xbmcvfs.mkdir(dir)
        fh = xbmcvfs.File(os.path.join(dir, "movie.strm"), 'w')
        fh.write('plugin://'+addonID+'/?mode=playVideo&url='+movieID)
        fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


def addSeasonToLibrary(seriesID, seriesTitle, seasonID):
    seriesFolderName = (''.join(c for c in unicode(seriesTitle, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
    seriesDir = os.path.join(libraryFolderTV, seriesFolderName)
    if not os.path.isdir(seriesDir):
        xbmcvfs.mkdir(seriesDir)
    content = opener.open(urlMain+"/gp/product/"+seasonID).read()
    matchSeason = re.compile('"seasonNumber":"(.+?)"', re.DOTALL).findall(content)
    spl = content.split('href="'+urlMain+'/gp/product')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('class="episode-title">(.+?)<', re.DOTALL).findall(entry)
        if match:
            title = match[0]
            title = cleanTitle(title)
            episodeNr = title[:title.find('.')]
            title = title[title.find('.')+1:].strip()
            match = re.compile('/(.+?)/', re.DOTALL).findall(entry)
            episodeID = match[0]
            if len(episodeNr) > 2:
                episodeNr = ''.join(re.findall(r'\d+', episodeNr))
            if len(episodeNr) == 1:
                episodeNr = "0"+episodeNr
            seasonNr = matchSeason[0]
            if len(seasonNr) == 1:
                seasonNr = "0"+seasonNr
            filename = "S"+seasonNr+"E"+episodeNr+" - "+title+".strm"
            filename = (''.join(c for c in unicode(filename, 'utf-8') if c not in '/\\:?"*|<>')).strip(' .')
            fh = xbmcvfs.File(os.path.join(seriesDir, filename), 'w')
            fh.write('plugin://'+addonID+'/?mode=playVideo&url='+episodeID)
            fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


def debug(content):
    fh=open(debugFile, "w")
    fh.write(content)
    fh.close()
        

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, videoType=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&videoType="+urllib.quote_plus(videoType)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&name="+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url)+'&videoType='+urllib.quote_plus(videoType)+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDirR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage)+"&name="+urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url)+'&videoType='+urllib.quote_plus(videoType)+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addLink(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url)+'&selectQuality=true)',))
    if videoType != "episode":
        entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url)+')',))
        entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url)+')',))
        entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url)+'&videoType='+urllib.quote_plus(videoType)+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+urllib.quote_plus(titleTemp)+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url)+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addLinkR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&thumb="+urllib.quote_plus(iconimage)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url)+'&selectQuality=true)',))
    entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url)+'&videoType='+urllib.quote_plus(videoType)+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url)+'&name='+urllib.quote_plus(titleTemp)+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url)+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url)+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addSeasonDir(name, url, mode, iconimage, seriesName, seriesID):
    filename = (''.join(c for c in unicode(seriesID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&seriesID="+urllib.quote_plus(seriesID)+"&thumb="+urllib.quote_plus(iconimage)+"&name="+urllib.quote_plus(seriesName)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "TVShowTitle": seriesName})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30056), 'RunPlugin(plugin://'+addonID+'/?mode=addSeasonToLibrary&url='+urllib.quote_plus(url)+'&seriesID='+urllib.quote_plus(seriesID)+'&name='+urllib.quote_plus(seriesName.strip())+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addEpisodeLink(name, url, mode, iconimage, desc="", duration="", season="", episodeNr="", seriesID="", playcount="", aired="", seriesName=""):
    filename = (''.join(c for c in unicode(seriesID, 'utf-8') if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "season": season, "episode": episodeNr, "aired": aired, "playcount": playcount, "TVShowTitle": seriesName})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url)+'&selectQuality=true)',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
name = urllib.unquote_plus(params.get('name', ''))
season = urllib.unquote_plus(params.get('season', ''))
seriesID = urllib.unquote_plus(params.get('seriesID', ''))
videoType = urllib.unquote_plus(params.get('videoType', ''))
selectQuality = urllib.unquote_plus(params.get('selectQuality', ''))

if mode == 'listMovies':
    listMovies(url)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listWatchList':
    listWatchList(url)
elif mode == 'listGenres':
    listGenres(url, videoType)
elif mode == 'addToQueue':
    addToQueue(url, videoType)
elif mode == 'removeFromQueue':
    removeFromQueue(url, videoType)
elif mode == 'playVideo':
    playVideo(url, selectQuality=="true")
elif mode == 'playVideoSelect':
    playVideo(url, True)
elif mode == 'browseMovies':
    browseMovies()
elif mode == 'browseTV':
    browseTV()
elif mode == 'search':
    search(url)
elif mode == 'login':
    login()
elif mode == 'listDecadesMovie':
    listDecadesMovie()
elif mode == 'listOriginals':
    listOriginals()
elif mode == 'listSeasons':
    listSeasons(name, url, thumb)
elif mode == 'listEpisodes':
    listEpisodes(seriesID, url, thumb, "", name)
elif mode == 'deleteCookies':
    deleteCookies()
elif mode == 'deleteCache':
    deleteCache()
elif mode == 'playTrailer':
    playVideo(url, selectQuality=="true", True)
elif mode == 'listSimilarMovies':
    listSimilarMovies(url)
elif mode == 'listSimilarShows':
    listSimilarShows(url)
elif mode == 'showInfo':
    showInfo(url)
elif mode == 'addMyListToLibrary':
    addMyListToLibrary()
elif mode == 'addMovieToLibrary':
    addMovieToLibrary(url, name)
elif mode == 'addSeasonToLibrary':
    addSeasonToLibrary(seriesID, name, url)
else:
    index()