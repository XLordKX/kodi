
from __future__ import unicode_literals
import urllib
import urlparse
import urllib2
#import requests
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
import base64
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
from HTMLParser import HTMLParser
import resources.lib.ScrapeUtils as ScrapeUtils

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addonFolder = downloadScript = xbmc.translatePath('special://home/addons/'+addonID).decode('utf-8')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID).decode('utf-8')

icon = os.path.join(addonFolder, "icon.png")#.encode('utf-8')


def translation(id):
    return addon.getLocalizedString(id) #.encode('utf-8')
    
if not os.path.exists(os.path.join(addonUserDataFolder, "settings.xml")):
    xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30081)+',10000,'+icon+')').encode("utf-8"))
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
debugFile = os.path.join(addonUserDataFolder, "debug")
preferAmazonTrailer = addon.getSetting("preferAmazonTrailer") == "true"
showNotification = addon.getSetting("showNotification") == "true"
showOriginals = addon.getSetting("showOriginals") == "true"
showLibrary = addon.getSetting("showLibrary") == "true"
showAvailability = addon.getSetting("showAvailability") == "true"
showPaidVideos = addon.getSetting("showPaidVideos") == "true"
showKids = addon.getSetting("showKids") == "true"
forceView = addon.getSetting("forceView") == "true"
updateDB = addon.getSetting("updateDB") == "true"
useTMDb = addon.getSetting("useTMDb") == "true"
usePrimeProxy = False #addon.getSetting("usePrimeProxy") == "true"
useWLSeriesComplete = addon.getSetting("useWLSeriesComplete") == "true"
watchlistOrder = addon.getSetting("watchlistOrder")
watchlistOrder = ["DATE_ADDED_DESC", "TITLE_ASC"][int(watchlistOrder)]
watchlistTVOrder = addon.getSetting("watchlistTVOrder")
watchlistTVOrder = ["DATE_ADDED_DESC", "TITLE_ASC"][int(watchlistTVOrder)]
maxBitrate = addon.getSetting("maxBitrate")
maxBitrate = [300, 600, 900, 1350, 2000, 2500, 4000, 6000, 10000, -1][int(maxBitrate)]
maxDevices = 3
maxDevicesWaitTime = 120
selectLanguage = addon.getSetting("selectLanguage")
siteVersion = addon.getSetting("siteVersion")
apiMain = ["atv-ps", "atv-ps-eu", "atv-ps-eu"][int(siteVersion)]
rtmpMain = ["azusfms", "azeufms", "azeufms"][int(siteVersion)]
siteVersionsList = ["com", "co.uk", "de"]
siteVersion = siteVersionsList[int(siteVersion)]
viewIdMovies = addon.getSetting("viewIdMovies")
viewIdShows = addon.getSetting("viewIdShows")
viewIdSeasons = addon.getSetting("viewIdSeasons")
viewIdEpisodes = addon.getSetting("viewIdEpisodes")
viewIdDetails = addon.getSetting("viewIdDetails")
urlMain = "http://www.amazon."+siteVersion
urlMainS = "https://www.amazon."+siteVersion
addon.setSetting('email', '')
addon.setSetting('password', '')
#deviceTypeID = "A324MFXUEZFF7B"
deviceTypeID = "A35LWR0L7KC0TJ"

cookieFile = os.path.join(addonUserDataFolder, siteVersion + ".cookies")

NODEBUG = False #True

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (X11; U; Linux i686; en-EN) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.127 Large Screen Safari/533.4 GoogleTV/ 162671"
opener.addheaders = [('User-agent', userAgent)]



def index():
    loginResult = login()
    if loginResult=="prime" or loginResult=="noprime":
        addDir(translation(30002), "", 'browseMovies', "")
        addDir(translation(30003), "", 'browseTV', "")
        xbmcplugin.endOfDirectory(pluginhandle)
    # elif loginResult=="noprime":
    #     listOriginals()
    elif loginResult=="none":
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30082)+',10000,'+icon+')').encode("utf-8"))


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
        addDir(translation(30009), urlMain+"/s/?n=4963842031&_encoding=UTF", 'listMovies', "")
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
    addDir(translation(30004), urlMain+"/gp/video/watchlist/tv/?ie=UTF8&show=all&sort="+watchlistTVOrder, 'listWatchList', "")
    if showLibrary:
        addDir(translation(30005), urlMain+"/gp/video/library/tv/?ie=UTF8&show=all&sort="+watchlistTVOrder, 'listWatchList', "")
    if siteVersion=="de":
        addDir(translation(30006), urlMain+"/gp/search/ajax/?_encoding=UTF8&rh=n%3A3010075031%2Cn%3A3356019031&sort=popularity-rank", 'listShows', "")
        addDir(translation(30011), urlMain+"/gp/search/other/?rh=n%3A3279204031%2Cn%3A!3010076031%2Cn%3A3356019031&pickerToList=theme_browse-bin&ie=UTF8", 'listGenres', "", "tv")
        if showKids:
            addDir(translation(30007), urlMain+"/gp/search/ajax/?rh=n%3A3010075031%2Cn%3A!3010076031%2Cn%3A3015916031%2Cp_n_theme_browse-bin%3A3015972031%2Cp_85%3A3282148031&ie=UTF8", 'listShows', "")
        addDir(translation(30010), urlMain+"/gp/search/ajax/?_encoding=UTF8&keywords=[OV]&rh=n%3A3010075031%2Cn%3A3015916031%2Ck%3A[OV]%2Cp_85%3A3282148031&sort=date-desc-rank", 'listShows', "")
        addDir(translation(30008), urlMain+"/gp/search/ajax/?_encoding=UTF8&bbn=3279204031&rh=n%3A3279204031%2Cn%3A3010075031%2Cn%3A3015916031&sort=date-desc-rank", 'listShows', "")
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
    content = ""
    if siteVersion=="de":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=5457207031")
    elif siteVersion=="com":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=9940930011")
    elif siteVersion=="co.uk":
        content = getUnicodePage(urlMain+"/b/?ie=UTF8&node=5687760031")
    debug(content)
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    content = content[content.find('<map name="pilots'):]
    content = content[:content.find('</map>')]
    #spl = content.split('shape="rect"')
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
    pilotsmatch = re.compile('<area.+?alt="(.+?)".+?href="(.+?)"', re.DOTALL).findall(content)
    for pilotval in pilotsmatch:
        match = re.compile("/gp/product/(.+?)/", re.DOTALL).findall(pilotval[1])
        videoID = match[0]
        title = pilotval[0]
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
        addShowDir(title, videoID, "listSeasons", thumb, "tv", showAll=True)
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode(500)')

def listWatchList(url):
    content = getUnicodePage(url)
    #fp = open(os.path.join(addonFolder, "videolib.html"), "r")
    #content = unicode(fp.read(), "iso-8859-15")
    #fp.close()
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    showEntries = []
    items = []
    dlParams = []
    videoType = None
    delim = ''
    oldstyle = False
    if '<div class="grid-list-item' in content:
        delim = '<div class="grid-list-item'
        beginarea = content.find(delim)
        area = content[beginarea:content.find('<div id="navFooter">', beginarea)]
    elif '<div class="lib-item"' in content:
        delim = '<div class="lib-item"'
        beginarea = content.find(delim)
        area = content[beginarea:content.find('</table>', beginarea)]
    else:
        delim = '<div class="innerItem"'
        beginarea = content.find(delim)
        area = content[beginarea:]
    itemc = area.count(delim)
    for i in range(0, itemc, 1):
        if (i < itemc):
            elementend = area.find(delim, 1)
            items.append(area[:elementend])
            area = area[elementend:]
        else:
            items.append(area)
    for i in range(0, len(items), 1):
        entry = items[i]
        if oldstyle:
            entry = entry[:entry.find('</td>')]
        if "/library/" in url or ("/watchlist/" in url and ("class='prime-meta'" in entry or 'class="prime-logo"' in entry or "class='item-green'" in entry or 'class="packshot-' in entry)):
            match = re.compile('data-prod-type="(.+?)"', re.DOTALL).findall(entry)
            if not match:
                match = re.compile('type="(.+?)" asin=', re.DOTALL).findall(entry)
            if match:
                if match[0] == "downloadable_tv_season" or match[0] == "tv" or match[0] == "season":
                    videoType = "tv"
                elif match[0] == "downloadable_movie" or match[0] == "movie":
                    videoType = "movie"
                else:
                    print match[0]
                    return
                match = re.compile('" asin="(.+?)"', re.DOTALL).findall(entry)
                if not match:
                    match = re.compile('id="(.+?)"', re.DOTALL).findall(entry)
                videoID = match[0]
                match = re.compile('<img alt="(.+?)" height', re.DOTALL).findall(entry)
                if not match:
                    match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
                title = match[0]


                match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
                thumbUrl = ""
                if match:
                    thumbUrl = ScrapeUtils.VideoImage().ImageFile(match[0])
                avail=''
                if showAvailability:
                    match = re.compile('\<span\s+class\s*=\s*"packshot-message"\s*\>(.+?)\<\/span\>', re.DOTALL).findall(entry)
                    if match:
                        avail=" - " + cleanInput(match[0])                        

                if videoType=="tv":
                    if useWLSeriesComplete:
                        dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanSeasonTitle(title)), 'year':''})
                        title = cleanSeasonTitle(title)+avail

                        if title in showEntries:
                            continue
                        
                        addShowDirR(cleanTitleTMDB(title) + avail, videoID, "listSeasons", thumbUrl, videoType, showAll=True)
                        showEntries.append(title)
                    else:
                        title = cleanTitle(title)
                        dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanTitle(title)), 'year':''})
                        addShowDirR(cleanTitleTMDB(title) + avail, videoID, "listEpisodes", thumbUrl, videoType)

                else: #movie
                    title = cleanTitle(title)
                    dlParams.append({'type':videoType, 'id':videoID, 'title':cleanTitleTMDB(cleanTitle(title)), 'year':''})
                    addLinkR(cleanTitleTMDB(title) + avail, videoID, "playVideo", thumbUrl, videoType)
                    
                    
    
    match_nextpage = re.compile('<a href=".+?dv_web_wtls_pg_nxt.+?&page=(.+?)&.+?">', re.DOTALL).findall(content)
    if match_nextpage:
        addDir(translation(30001), url + "&page=" + match_nextpage[0].strip(), "listWatchList", "DefaultTVShows.png")
    if videoType == "movie":
        xbmcplugin.setContent(pluginhandle, "movies")
    else:
        xbmcplugin.setContent(pluginhandle, "tvshows")
    if useTMDb and videoType == "movie":
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    elif useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        if videoType == "movie":
            xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')
        else:
            xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listMovies(url):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUnicodePage(url)
    debug(content)
    content = content.replace("\\","")
    if 'id="catCorResults"' in content:
        content = content[:content.find('id="catCorResults"')]
    match = re.compile('csrf":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    
    args = urlparse.parse_qs(url[1:])
    page = args.get('page', None)
    if page is not None:
        if int(page[0]) > 1:
            content = content[content.find('breadcrumb.breadcrumbSearch'):]
    
    spl = content.split('id="result_')
    dlParams = []
    videoimage = ScrapeUtils.VideoImage()
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('asin="(.+?)"', re.DOTALL).findall(entry)
        if match and ">Prime Instant Video<" in entry:
            videoID = match[0]
            match1 = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
            match2 = re.compile('class="ilt2">(.+?)<', re.DOTALL).findall(entry)
            title = None
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
            #thumbUrl = match[0].replace(".jpg", "")
            #thumbUrl = thumbUrl[:thumbUrl.rfind(".")]+".jpg"
            thumbUrl = videoimage.ImageFile(match[0])
            match = re.compile('data-action="s-watchlist-add".+?class="a-button a-button-small(.+?)"', re.DOTALL).findall(entry)
            if match and match[0]==" s-hidden":
                addLinkR(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
            else:
                addLink(title, videoID, "playVideo", thumbUrl, "movie", "", "", year)
    if useTMDb:
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listMovies", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listShows(url):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = getUnicodePage(url)
    debug(content)
    content = content.replace("\\","")
    if 'id="catcorresults"' in content:
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
        isPaidVideo = False
        if showPaidVideos:
            if ">Shop Instant Video<" in entry:
                isPaidVideo = True
            if ">Amazon Video:<" in entry:
                isPaidVideo = True
        #if match and ">Prime Instant Video<" in entry:
        if match and ((">Prime Instant Video<" in entry) or (isPaidVideo)):
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
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    match = re.compile('class="pagnNext".*?href="(.+?)"', re.DOTALL).findall(content)
    if match:
        addDir(translation(30001), urlMain+match[0].replace("&amp;","&"), "listShows", "DefaultTVShows.png")
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSimilarMovies(videoID):
    xbmcplugin.setContent(pluginhandle, "movies")
    content = getUnicodePage(urlMain+"/gp/product/"+videoID)
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
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScript+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdMovies+')')


def listSimilarShows(videoID):
    xbmcplugin.setContent(pluginhandle, "tvshows")
    content = getUnicodePage(urlMain+"/gp/product/"+videoID)
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
        dlParams = json.dumps(dlParams)
        xbmc.executebuiltin('XBMC.RunScript('+downloadScriptTV+', '+urllib.quote_plus(dlParams.encode("utf8"))+')')
    xbmcplugin.endOfDirectory(pluginhandle)
    xbmc.sleep(100)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIdShows+')')


def listSeasons(seriesName, seriesID, thumb, showAll = False):
    xbmcplugin.setContent(pluginhandle, "seasons")
    content = getUnicodePage(urlMain+"/gp/product/"+seriesID)
    debug("listSeasons")
    debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    if '<select name="seasonAsinAndRef"' in content:
        content = content[content.find('<select name="seasonAsinAndRef"'):]
        content = content[:content.find('</select>')]
        match = re.compile('<option value="(.+?):.+?data-a-html-content="(.+?)"', re.DOTALL).findall(content)
        if match:
            for seasonID, title in match:
                if "dv-dropdown-prime" in title or showAll or showPaidVideos:
                    if "\n" in title:
                        title = title[:title.find("\n")]
                    addSeasonDir(title, seasonID, 'listEpisodes', thumb, seriesName, seriesID)
            xbmcplugin.endOfDirectory(pluginhandle)
            xbmc.sleep(100)
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdSeasons+')')
    elif '<div class="dv-dropdown-single">' in content:
        content = content[content.find('<div class="dv-dropdown-single">'):]
        content = content[:content.find('<li class="selected-episode')]
        match = re.compile('<div class="dv-dropdown-single">(.+?)<', re.DOTALL).findall(content)
        if match:
            for title in match:
                title = title.strip()
                if "dv-dropdown-prime" in content or showAll or showPaidVideos:
                    addSeasonDir(title, seriesID, 'listEpisodes', thumb, seriesName, seriesID)
            xbmcplugin.endOfDirectory(pluginhandle)
            xbmc.sleep(100)
            if forceView:
                xbmc.executebuiltin('Container.SetViewMode('+viewIdSeasons+')')
    else:
        # listEpisodes(seriesID, seriesID, thumb, contentMain)
        listEpisodes(seriesID, seriesID, thumb)


def listEpisodes(seriesID, seasonID, thumb, content="", seriesName=""):
    xbmcplugin.setContent(pluginhandle, "episodes")
    if not content:
        content = getUnicodePage(urlMain+"/gp/product/"+seasonID)
    debug("listEpisodes")
    debug(content)
    match = re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
    if match:
        addon.setSetting('csrfToken', match[0])
    matchSeason = re.compile('"seasonNumber":"(.+?)"', re.DOTALL).findall(content)
    seasonNr="0"
    if matchSeason:
        seasonNr=matchSeason[0]
    
    epliststart = content.rfind("<li ", 0, content.find("first-episode"))
    eplistend = content.find("</ul>", epliststart)
    content = content[epliststart:eplistend]
    spl = content.split('<li ')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        entry = entry[:entry.find('</li>')]
        match = re.compile('class="episode-title">(.+?)<', re.DOTALL).findall(entry)
        #if match and ('class="prime-logo-small"' in entry or 'class="episode-status cell-free"' in entry or 'class="episode-status cell-owned"' in entry or 'class="episode-status cell-unavailable"' in entry):
        if match and checkEpisodeStatus(entry):
            title = match[0]
            title = cleanTitle(title)
            episodeNr = title[:title.find('.')]
            title = title[title.find('.')+1:].strip()
            match = re.compile('/gp/product/(.+?)/', re.DOTALL).findall(entry)
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
    content = getUnicodePage(url)
    debug(content)
    content = content[content.find('<ul class="column vPage1">'):]
    content = content[:content.find('</div>')]
    match = re.compile('href="(.+?)">.+?>(.+?)</span>.+?>(.+?)<', re.DOTALL).findall(content)
    for url, title, nr in match:
        if videoType=="movie":
            addDir(cleanTitle(title), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listMovies', "")
        else:
            addDir(cleanTitle(title), urlMain+url.replace("/s/","/mn/search/ajax/").replace("&amp;","&"), 'listShows', "")
    xbmcplugin.endOfDirectory(pluginhandle)

def selectLang(content):
    content = content[content.find('class="dv-toggle-box dv-tb-closed">'):content.find('<span id="dv-mta-submit-announce"')]
    matchlo = re.compile('<option value="(.+?)".*?>(.+?)</option>', re.DOTALL).findall(content)
    if len(matchlo) > 0:
        opt = []
        for i,val in enumerate(matchlo):
            opt.append([val[0].strip(), val[1].strip()])
        return opt
    return None

def changeStream(videoID):
    args = urlparse.parse_qs(sys.argv[2][1:])
    title = args.get('title', videoID)[0]
    thumburl = args.get('thumbnailimage', '')[0]
    xbmc.Player().pause()
    listitem = xbmcgui.ListItem(title, path="http://127.0.0.1:59950/"+videoID + ".mp4", thumbnailImage=thumburl)
    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('TotalTime', str(xbmc.Player().getTotalTime()))
    listitem.setProperty('ResumeTime', str(xbmc.Player().getTime()))
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def helloPrimeProxy():
    try:
        s = socket.create_connection(("127.0.0.1", 59910),1)
        primeproxyjson = base64.b64encode(json.dumps({"hello": True})) + "\r\n"
        s.sendall(primeproxyjson)
        pcdata = ""
        while not "\r\n" in pcdata:
            pcdata += s.recv(1024)
            pass
        s.close()
        pcdata = json.loads(base64.b64decode(pcdata.strip()))
        if pcdata['status'] == "success":
            return True
    except:
        return False

def playVideo(videoID, selectQuality=False, playTrailer=False):
    streamTitles = []
    streamBitrates = []
    streamURLs = []
    cMenu = False
    if selectQuality:
        cMenu = True
    if maxBitrate==-1:
        selectQuality = True
    try: content = getUnicodePage(urlMain+"/dp/"+videoID + "/?_encoding=UTF8")
    except: content = getUnicodePage(urlMainS+"/dp/"+videoID + "/?_encoding=UTF8")
    if login(content, statusOnly=True) == "none":
        qlogin = login()
        if qlogin == "noprime" or qlogin == "prime":
            content = getUnicodePage(urlMain+"/dp/"+videoID + "/?_encoding=UTF8")
    
    hasTrailer = False
    #if '&quot;playTrailer&quot;:true' in content:
    #    hasTrailer = True
    matchCID=re.compile('"customerID":"(.+?)"').findall(content)
    if matchCID:
        # prepare swf contents as fallback
        noFlash = False # this var does not specify if player uses http or rtmp!!!
        matchSWFUrl=re.compile('<script type="text/javascript" src="(.+?webplayer.+?webplayer.+?js)"', re.DOTALL).findall(content)
        if matchSWFUrl:
            flashContent = getUnicodePage(matchSWFUrl[0])
            matchSWF=re.compile('LEGACY_FLASH_SWF="(.+?)"').findall(flashContent)
            matchDID=re.compile('FLASH_GOOGLE_TV="(.+?)"').findall(flashContent)
            if not matchDID:
                matchDID = [deviceTypeID]
        else:
            noFlash = True
            matchDID = [deviceTypeID]
        #if '"episode":{"name":"' in content:
        #    matchTitle=re.compile('"episode":{"name":"(.+?)"', re.DOTALL).findall(content)
        #else:
        #    matchTitle=re.compile('"contentRating":".+?","name":"(.+?)"', re.DOTALL).findall(content)
        matchThumb=re.compile('"video":.+?"thumbnailUrl":"(.+?)"', re.DOTALL).findall(content)
        matchToken=re.compile('"csrfToken":"(.+?)"', re.DOTALL).findall(content)
        matchMID=re.compile('"marketplaceID":"(.+?)"').findall(content)
        asincontent = getUnicodePage('https://'+apiMain+'.amazon.com/cdp/catalog/GetASINDetails?version=2&format=json&asinlist='+videoID+'&deviceID='+urllib.quote_plus(matchCID[0].encode("utf8"))+'&includeRestrictions=true&deviceTypeID='+matchDID[0]+'&firmware=WIN%2017,0,0,188%20PlugIn&NumberOfResults=1')
        asininfo = json.loads(asincontent)
        matchTitle = [asininfo["message"]["body"]["titles"][0]["title"]]
        hasTrailer = asininfo["message"]["body"]["titles"][0]["trailerAvailable"]
        asinruntime = asininfo["message"]["body"]["titles"][0]["runtime"]["valueMillis"]
        avail_langs = selectLang(content)
        if not playTrailer or (playTrailer and hasTrailer and preferAmazonTrailer and siteVersion!="com"):
            content = getUnicodePage(urlMainS+'/gp/video/streaming/player-token.json?callback=jQuery1640'+''.join(random.choice(string.digits) for x in range(18))+'_'+str(int(time.time()*1000))+'&csrftoken='+urllib.quote_plus(matchToken[0].encode("utf8"))+'&_='+str(int(time.time()*1000)))
            matchToken=re.compile('"token":"(.+?)"', re.DOTALL).findall(content)
        content = ""
        if playTrailer and hasTrailer and preferAmazonTrailer and siteVersion!="com":
            content = getUnicodePage('https://'+apiMain+'.amazon.com/cdp/catalog/GetStreamingTrailerUrls?version=1&format=json&firmware=WIN%2011,7,700,224%20PlugIn&marketplaceID='+urllib.quote_plus(matchMID[0].encode("utf8"))+'&token='+urllib.quote_plus(matchToken[0].encode("utf8"))+'&deviceTypeID='+matchDID[0]+'&asin='+videoID+'&customerID='+urllib.quote_plus(matchCID[0].encode("utf8"))+'&deviceID='+urllib.quote_plus(matchCID[0].encode("utf8"))+str(int(time.time()*1000))+videoID)
            selectQuality = True
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
            content = getUnicodePage('https://'+apiMain+'.amazon.com/cdp/catalog/GetStreamingUrlSets?version=1&format=json&firmware=WIN%2011,7,700,224%20PlugIn'+playlanguage+'&marketplaceID='+urllib.quote_plus(matchMID[0].encode("utf8"))+'&token='+urllib.quote_plus(matchToken[0].encode("utf8"))+'&deviceTypeID='+matchDID[0]+'&asin='+videoID+'&customerID='+urllib.quote_plus(matchCID[0].encode("utf8"))+'&deviceID='+urllib.quote_plus(matchCID[0].encode("utf8"))+str(int(time.time()*1000))+videoID)
        elif playTrailer:
            try:
                strT = ""
                if siteVersion=="de":
                    strT = "+german"
                myYoutubeApiKey = cipherKey("bXHbr7m5hoHjuHY0OIx1N/7gfeYPe9ePDewCOb2X8wvn0XOAjy+C")
                queryString = urllib.quote_plus(cleanTitle(matchTitle[0]).encode("utf-8"))+"+trailer"+strT
                queryUrl = "https://www.googleapis.com/youtube/v3/search?part=id&q=" + queryString + "&order=relevance&key=" + myYoutubeApiKey
                searchRes = getUnicodePage(queryUrl)
                searchResJson = json.loads(searchRes)
                vidid = searchResJson['items'][0]['id']['videoId']
                xbmc.Player().play("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + vidid)
            except Exception as e:
                xbmc.executebuiltin('XBMC.Notification(Info:,' + str(e) + ',10000,'+icon+')')
                pass
        debug(content)
        if content:
            if not "SUCCESS" in unicode(content):
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
                        if selectQuality or usePrimeProxy:
                            streamTitles.append(str(item['bitrate'])+"kb")
                            streamBitrates.append(item['bitrate'])
                            streamURLs.append(item['url'])
                            url = item['url']
                        elif item['bitrate']<=maxBitrate:
                            url = item['url']
                    if not rtmpMain in url or ("mp4?" in url and "auth=" in url):
                        debug("no azvod server in list 0")
                        debug(contentT)
                        if len(content['message']['body']['urlSets']['streamingURLInfoSet']) > 1:
                            if selectQuality or usePrimeProxy:
                                streamTitles = []
                                streamBitrates = []
                                streamURLs = []
                            for item in content['message']['body']['urlSets']['streamingURLInfoSet'][1]['streamingURLInfo']:
                                if selectQuality or usePrimeProxy:
                                    streamTitles.append(str(item['bitrate'])+"kb")
                                    streamBitrates.append(item['bitrate'])
                                    streamURLs.append(item['url'])
                                elif item['bitrate']<=maxBitrate:
                                    url = item['url']
                            debug("using alternative list index 1")
                            debug(content['message']['body']['urlSets']['streamingURLInfoSet'][1]['streamingURLInfo'])
                        else:
                            debug("unable to use alternative list, flash playback with rtmp will be used")
                            pass
                    if url:
                        if selectQuality:
                            dialog = xbmcgui.Dialog()
                            nr=dialog.select(translation(30059), streamTitles)
                            if nr>=0:
                              url=streamURLs[nr]
                        if url.startswith("rtmpe"):
                            urlproto = "rtmpe://"
                            urlsite = url[len(urlproto):url.find("/", len(urlproto))]
                            urlrequest = url[url.find('mp4:')+4:]
                            if (not rtmpMain in urlsite or ("mp4?" in url and "auth=" in url)) and not noFlash:
                                debug("Using flash playback")
                                flash_req1 = url[url.find(urlsite)+len(urlsite) + 1:url.find('/mp4:')]
                                flash_tcUrl = urlproto + urlsite + ":1935/" + flash_req1 + "/"
                                flash_app = flash_req1
                                flash_playpath = url[url.find('mp4:'):]
                                flash_url = url.replace('rtmpe','rtmp')
                                url = flash_url+' swfVfy=1 swfUrl='+matchSWF[0]+' pageUrl='+urlMain+'/dp/'+videoID+' app='+flash_app+' playpath='+flash_playpath+' tcUrl=' + flash_tcUrl
                            else:
                                debug("Using http playback")
                                url = 'http://' + urlsite + "/" + urlrequest
                            if playTrailer or (selectQuality and cMenu):
                                title = matchTitle[0]
                                listitem = xbmcgui.ListItem(title, path=url, thumbnailImage=thumbUrl)
                                xbmc.Player().play(url, listitem)
                            else:
                                if not usePrimeProxy: # or not helloPrimeProxy():
                                    if usePrimeProxy:
                                        xbmc.executebuiltin('XBMC.Notification(Info:,' + "PrimeProxy connection failed" + ',10000,'+icon+')')
                                    title = matchTitle[0]
                                    listitem = xbmcgui.ListItem(title, path=url, thumbnailImage=thumbUrl)
                                    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
                                else:
                                    useStreamingIndex = 0
                                    title = matchTitle[0]
                                    for w,i in enumerate(streamURLs):
                                        wurl = i
                                        wproto = "rtmpe://"
                                        wsite = wurl[len(wproto):wurl.find("/", len(wproto))]
                                        wrequest = wurl[wurl.find('mp4:')+4:]
                                        streamURLs[w] = { 'url' : 'http://' + wsite + "/" + wrequest, 'bitrate': streamBitrates[w]}
                                        if url == streamURLs[w]['url']:
                                            useStreamingIndex = w
                                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    primeproxyjson = json.dumps({"asin": videoID, "setProperties": {"StreamingIndex": useStreamingIndex, "Runtime" : asinruntime, "StreamingList": streamURLs, "ThumbnailImage": thumbUrl, "Title": title}})
                                    primeproxyjson = base64.b64encode(primeproxyjson) + "\r\n"
                                    s.connect(("127.0.0.1", 59910))
                                    s.sendall(primeproxyjson)
                                    pcdata = ""
                                    while not "\r\n" in pcdata:
                                        pcdata += s.recv(1024)
                                        pass
                                    s.close()
                                    title = matchTitle[0]
                                    listitem = xbmcgui.ListItem(title, path="http://127.0.0.1:59950/"+videoID + ".mp4", thumbnailImage=thumbUrl)
                                    pcdata = json.loads(base64.b64decode(pcdata))
                                    if "status" in pcdata and pcdata["status"] == "success":
                                        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
                                    else:
                                        xbmcplugin.setResolvedUrl(pluginhandle, False, listitem)


                        elif url.startswith("http"):
                            dialog = xbmcgui.Dialog()
                            if dialog.yesno('Info', translation(30085)):
                                content = getUnicodePage(urlMainS+"/gp/video/settings/ajax/player-preferences-endpoint.html", "rurl="+urllib.quote_plus(str(urlMainS+"/gp/video/settings","utf8"))+"&csrfToken="+urllib.quote_plus(addon.getSetting('csrfToken').encode("utf8"))+"&aiv-pp-toggle=flash")
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
    content = getUnicodePage(urlMain+"/dp/"+videoID + "/?_encoding=UTF8")
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
    genre = u""
    if match:
        genre = match[0]
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

def getUnicodePage(url):

    req = opener.open(url)
    content = ""
    if "content-type" in req.headers and "charset=" in req.headers['content-type']:
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = unicode(req.read(), encoding)
    else:
        content = unicode(req.read(), "utf-8")
    return content

def getAsciiPage(url):
    req = opener.open(url)
    content = req.read()
    if "content-type" in req.headers and "charset=" in req.headers['content-type']:
        encoding=req.headers['content-type'].split('charset=')[-1]
        content = unicode(content, encoding)
    else:
        content = unicode(content, "utf-8")
    return content.encode("utf-8")

def cipherKey(s, key="xlordkx"):
    key = unicode(key).encode("utf-8")
    keyarr = map(ord, key)
    key = b""
    for i in range(len(keyarr)):
        key += str(keyarr[i])
    s = base64.b64decode(s)
    random.seed(long(key))
    bytearr = map (ord, s )
    o = b""
    for i in range(len(bytearr)):
        o += (chr(bytearr[i] ^ random.randint(0, 255)))
    return unicode(o)

def search(type):
    keyboard = xbmc.Keyboard('', translation(30015))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = unicode(keyboard.getText(), "utf-8").replace(" ", "+")
        search_string = urllib.quote_plus(search_string.encode("utf8"))
        if siteVersion=="de":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356018031&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356019031&field-keywords="+search_string)
        elif siteVersion=="com":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613704011&field-keywords="+search_string)
            elif type=="tv":
                if not showPaidVideos:
                    listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D7613705011&field-keywords="+search_string)
                else:
                    listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D2858778011&field-keywords="+search_string)
        elif siteVersion=="co.uk":
            if type=="movies":
                listMovies(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356010031&field-keywords="+search_string)
            elif type=="tv":
                listShows(urlMain+"/mn/search/ajax/?_encoding=UTF8&url=node%3D3356011031&field-keywords="+search_string)
        


def addToQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = getUnicodePage(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_add?token="+urllib.quote_plus(addon.getSetting('csrfToken').encode("utf8"))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video")
    if showNotification:
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30088)+',3000,'+icon+')').encode("utf-8"))


def removeFromQueue(videoID, videoType):
    if videoType=="tv":
        videoType = "tv_episode"
    content = getUnicodePage(urlMain+"/gp/video/watchlist/ajax/addRemove.html/ref=sr_1_1_watchlist_remove?token="+urllib.quote_plus(addon.getSetting('csrfToken').encode("utf8"))+"&dataType=json&prodType="+videoType+"&ASIN="+videoID+"&pageType=Search&subPageType=SASLeafSingleSearch&store=instant-video")
    xbmc.executebuiltin("Container.Refresh")
    if showNotification:
        xbmc.executebuiltin(unicode('XBMC.Notification(Info:,'+translation(30089)+',3000,'+icon+')').encode("utf-8"))


def login(content = None, statusOnly = False):
    if content is None:
        content = getUnicodePage(urlMain)
    signoutmatch = re.compile("declare\('config.signOutText',(.+?)\);", re.DOTALL).findall(content)
    if '","isPrime":1' in content: # 
        return "prime"
    elif signoutmatch[0].strip() != "null":
        return "noprime"
    else:
        if statusOnly:
            return "none"

        deleteCookies()
        content = ""
        keyboard = xbmc.Keyboard('', translation(30090))
        keyboard.doModal()
        if keyboard.isConfirmed() and unicode(keyboard.getText(), "utf-8"):
            email = unicode(keyboard.getText(), "utf-8")
            keyboard = xbmc.Keyboard('', translation(30091), True)
            keyboard.setHiddenInput(True)
            keyboard.doModal()
            if keyboard.isConfirmed() and unicode(keyboard.getText(), "utf-8"):
                password = unicode(keyboard.getText(), "utf-8")
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
                cj.load(cookieFile)
                content = getUnicodePage(urlMain)
        signoutmatch = re.compile("declare\('config.signOutText',(.+?)\);", re.DOTALL).findall(content)
        if '","isPrime":1' in content: # 
            return "prime"
        elif signoutmatch[0].strip() != "null":
            return "noprime"
        else:
            return "none"


def cleanInput(str):
    if type(str) is not unicode:
        str = unicode(str, "iso-8859-15")
        xmlc = re.compile('&#(.+?);', re.DOTALL).findall(str)
        for c in xmlc:
            str = str.replace("&#"+c+";", unichr(int(c)))
    
    p = HTMLParser()
    str = p.unescape(str)
    #str = str.encode("utf-8")
    return str

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
    #title = title.decode('iso-8859-1').encode('iso-8859-1')
    movieFolderName = (''.join(c for c in title if c not in '/\\:?"*|<>')).strip(' .')
    dir = os.path.join(libraryFolderMovies, movieFolderName)
    if not os.path.exists(dir):
        xbmcvfs.mkdir(unicode(dir).encode("iso-8859-1"))
        fh = xbmcvfs.File(unicode(os.path.join(dir, "movie.strm")).encode("iso-8859-1"), 'w')
        fh.write(unicode('plugin://'+addonID+'/?mode=playVideo&url='+movieID).encode("utf-8"))
        fh.close()
    if updateDB:
        xbmc.executebuiltin(unicode('UpdateLibrary(video)').encode("utf-8"))


def addSeasonToLibrary(seriesID, seriesTitle, seasonID):
    seriesFolderName = (''.join(c for c in seriesTitle if c not in '/\\:?"*|<>')).strip(' .')
    seriesDir = os.path.join(libraryFolderTV, seriesFolderName)
    if not os.path.isdir(seriesDir):
        xbmcvfs.mkdir(unicode(seriesDir).encode("iso-8859-1"))
    content = getUnicodePage(urlMain+"/gp/product/"+seasonID)
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
            filename = (''.join(c for c in filename if c not in '/\\:?"*|<>')).strip(' .')
            print type(filename)
            fh = xbmcvfs.File(unicode(os.path.join(seriesDir, filename)).encode('utf-8'), 'w')
            fh.write(unicode('plugin://'+addonID+'/?mode=playVideo&url='+episodeID).encode("utf-8"))
            fh.close()
    if updateDB:
        xbmc.executebuiltin('UpdateLibrary(video)')


def debug(content):
    if (NODEBUG):
        return
    #print unicode(content).encode("utf-8")
    #log(content, xbmc.LOGDEBUG)
    log(unicode(content), xbmc.LOGDEBUG)

def log(msg, level=xbmc.LOGNOTICE):
    # xbmc.log('%s: %s' % (addonID, msg), level)
    log_message = u'{0}: {1}'.format(addonID, msg)
    xbmc.log(log_message.encode("utf-8"), level)
    """
    xbmc.LOGDEBUG = 0
    xbmc.LOGERROR = 4
    xbmc.LOGFATAL = 6
    xbmc.LOGINFO = 1
    xbmc.LOGNONE = 7
    xbmc.LOGNOTICE = 2
    xbmc.LOGSEVERE = 5
    xbmc.LOGWARNING = 3
    """

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
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&videoType="+urllib.quote_plus(videoType.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name})
    liz.setProperty("fanart_image", defaultFanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating="", showAll = False):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    sAll = ""
    if (showAll):
        sAll = "&showAll=true"
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(name.encode("utf8"))+sAll
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDirR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating="", showAll = False):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    coverFile = os.path.join(cacheFolderCoversTMDB, filename)
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    if os.path.exists(coverFile):
        iconimage = coverFile
    sAll = ""
    if (showAll):
        sAll = "&showAll=true"
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(name.encode("utf8"))+sAll
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addLink(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    #entries.append(("PreCache Video", 'RunPlugin(plugin://'+addonID+'/?mode=precacheVideo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    if videoType != "episode":
        entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
        entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
        entries.append((translation(30052), 'RunPlugin(plugin://'+addonID+'/?mode=addToQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&name='+urllib.quote_plus(titleTemp.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addLinkR(name, url, mode, iconimage, videoType="", desc="", duration="", year="", mpaa="", director="", genre="", rating=""):
    filename = (''.join(c for c in url if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "year": year, "mpaa": mpaa, "director": director, "genre": genre, "rating": rating})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    entries.append((translation(30060), 'Container.Update(plugin://'+addonID+'/?mode=showInfo&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30051), 'RunPlugin(plugin://'+addonID+'/?mode=playTrailer&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30053), 'RunPlugin(plugin://'+addonID+'/?mode=removeFromQueue&url='+urllib.quote_plus(url.encode("utf8"))+'&videoType='+urllib.quote_plus(videoType.encode("utf8"))+')',))
    if videoType == "movie":
        titleTemp = name.strip()
        if year:
            titleTemp += ' ('+year+')'
        entries.append((translation(30055), 'RunPlugin(plugin://'+addonID+'/?mode=addMovieToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&name='+urllib.quote_plus(titleTemp.encode("utf8"))+')',))
    entries.append((translation(30057), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarMovies&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    entries.append((translation(30058), 'Container.Update(plugin://'+addonID+'/?mode=listSimilarShows&url='+urllib.quote_plus(url.encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addSeasonDir(name, url, mode, iconimage, seriesName, seriesID):
    filename = (''.join(c for c in seriesID if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)+"&seriesID="+urllib.quote_plus(seriesID.encode("utf8"))+"&thumb="+urllib.quote_plus(iconimage.encode("utf8"))+"&name="+urllib.quote_plus(seriesName.encode("utf8"))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "TVShowTitle": seriesName})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30056), 'RunPlugin(plugin://'+addonID+'/?mode=addSeasonToLibrary&url='+urllib.quote_plus(url.encode("utf8"))+'&seriesID='+urllib.quote_plus(seriesID.encode("utf8"))+'&name='+urllib.quote_plus(seriesName.strip().encode("utf8"))+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addEpisodeLink(name, url, mode, iconimage, desc="", duration="", season="", episodeNr="", seriesID="", playcount="", aired="", seriesName=""):
    filename = (''.join(c for c in seriesID if c not in '/\\:?"*|<>')).strip()+".jpg"
    fanartFile = os.path.join(cacheFolderFanartTMDB, filename)
    u = sys.argv[0]+"?url="+urllib.quote_plus(url.encode("utf8"))+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultTVShows.png", thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels={"title": name, "plot": desc, "duration": duration, "season": season, "episode": episodeNr, "aired": aired, "playcount": playcount, "TVShowTitle": seriesName})
    liz.setProperty("fanart_image", fanartFile)
    entries = []
    entries.append((translation(30054), 'RunPlugin(plugin://'+addonID+'/?mode=playVideo&url='+urllib.quote_plus(url.encode("utf8"))+'&selectQuality=true)',))
    liz.addContextMenuItems(entries)
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def checkEpisodeStatus(entry):
    statusList = []
    statusList.append("prime-logo-small")
    statusList.append("episode-status cell-free")
    statusList.append("episode-status cell-owned")
    statusList.append("episode-status cell-unavailable")
    if showPaidVideos:
        statusList.append("episode-status ")
    for status in statusList:
        statusString = 'class="' + status + '"'
        if statusString in entry:
            return True
    return False

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
name = urllib.unquote_plus(params.get('name', ''))
season = urllib.unquote_plus(params.get('season', ''))
showAllSeasons = urllib.unquote_plus(params.get('showAll', '')) == "true"
seriesID = urllib.unquote_plus(params.get('seriesID', ''))
videoType = urllib.unquote_plus(params.get('videoType', ''))
selectQuality = urllib.unquote_plus(params.get('selectQuality', ''))

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

if os.path.exists(os.path.join(addonUserDataFolder, "cookies")):
    os.rename(os.path.join(addonUserDataFolder, "cookies"), cookieFile)



if os.path.exists(cookieFile):
    cj.load(cookieFile)
else:
    login()

if mode == 'changeStream':
    changeStream(url)
elif mode == 'listMovies':
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
    listSeasons(name, url, thumb, showAll=showAllSeasons)
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