from __future__ import unicode_literals
from urlparse import urlparse
import xbmc
import xbmcaddon
import os

class Movies():
    def __init__(self):
        pass

class AmazonWebContent():
    def __init__(self):
        pass

class VideoImage():
    
    def __init__(self):
        addonID = 'plugin.video.prime_instant'
        addon = xbmcaddon.Addon(id=addonID)
        addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
        self.cacheFolder = os.path.join(addonUserDataFolder, "cache", "covers")
        pass
    
    def ImageFile(self, imgsrc):
        urlinfo = urlparse(imgsrc)
        path = urlinfo[2]
        imgbasename = path[path.rfind("/")+1:]
        imgfile = imgbasename[:imgbasename.find(".")] + ".jpg"
        imgsrc = imgsrc[:imgsrc.rfind("/")+1] + imgfile
        return imgsrc

    """
    def ImageDownload(self, asin, imgsrc):
        f = open(os.path.join(self.cacheFolder, asin + ".jpg"), "wb")
        f.write(WebContent().DownloadFile(self.ImageFile(imgsrc)))
        f.close()

    
    def HasCachedImage(self, asin):
        imgfile = os.path.join(self.cacheFolder, asin + ".jpg")
        if (os.path.exists(imgfile)):
            return True
        return False

    
    def GetImage(self, asin, imgsrc):
        if not self.HasCachedImage(asin):
            self.ImageDownload(asin, imgsrc)
        return os.path.join(self.cacheFolder, asin + ".jpg")
    """
