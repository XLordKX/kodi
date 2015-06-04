from __future__ import unicode_literals
import asyncore, socket
import xbmc
import xbmcaddon
import time
import base64
import json
import sys
import os

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level)

class AmazonHTTPClient(asyncore.dispatcher):

    def __init__(self, conf, ahost, buffers):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (ahost, 80) )
        self.maxsize = 1024 * 1024 * 1
        self.amazonbuffer = buffers
        self.streaming = False
        self.conf = conf
        self.t = int(time.time())
        self.readbytes = 0
        self.bflow = 0
        self.isRealTimeSet = False
        self.bpsrequired = 0
        self.reduceBitrate = None
        self.streamtime = 0
        self.cl = False
        self.avgbr = []
        debug("AmazonHTTPClient __init__")
    
    def handle_connect(self):
        debug("AmazonHTTPClient handle_connect")
    
    def handle_close(self):
        debug("AmazonHTTPClient handle_close")
        self.cl = True

    def readable(self):
        return (not self.cl and len(self.amazonbuffer[0]) < self.maxsize)
    
    def handle_read(self):
        hread = self.recv(1024 * 1024 * 6)
        if not hread: return
        self.amazonbuffer[0] += hread
        if self.streaming:
            self.readbytes += len(hread)
            tnow = int(time.time())
            if tnow > self.t:
                self.streamtime += 1
                bpsnow = self.readbytes / 1024
                self.avgbr.append(bpsnow)
                self.readbytes = 0
                
                if len(self.avgbr) > 30:
                    del self.avgbr[0]

                if bpsnow < self.bpsrequired:
                    self.bflow -= self.bpsrequired - bpsnow
                
                elif bpsnow > self.bpsrequired:
                    self.bflow += bpsnow - self.bpsrequired
                
                if self.isRealTimeSet:
                    if self.bflow < 0: # or self.streamtime > 30: #################################################################
                        debug("AmazonHTTPClient Buffer low: " + str(self.bflow) + "kb")
                        self.reduceBitrate((sum(self.avgbr)/self.streamtime))
                        self.conf.asinrealruntime = -99 # avoid player gettime, stream gets closed in a moment
                else:
                    if self.conf.asinrealruntime > 0:
                        debug("AmazonHTTPClient isRealTimeSet is true, asinrealruntime: " + str(self.conf.asinrealruntime))
                        self.conf.asinruntime = self.conf.asinrealruntime * 1000
                        newreqstreamrate = (self.conf.streamlength / (self.conf.asinruntime/1000)) / 1024
                        self.bflow += ((self.bpsrequired - newreqstreamrate) * self.streamtime)
                        debug("AmazonHTTPClient recalculated stream bitrate (kbyte) " + str(self.bpsrequired) + " to " + str(newreqstreamrate))
                        self.bpsrequired = newreqstreamrate
                        self.isRealTimeSet = True
                        self.bflow = 0
                    else:
                        if self.conf.asinrealruntime == 0 and self.streamtime > 5:
                            self.conf.asinrealruntime = -99 # deactivate check until external script changes real time
                            addon = xbmcaddon.Addon()
                            addonPath = addon.getAddonInfo('path')
                            apivplayer = os.path.join(addonPath, "PlayerProc.py")
                            xbmc.executebuiltin('XBMC.RunScript('+apivplayer+',gettime,asin=' + self.conf.asin + ')')
                        else:
                            if self.conf.asinrealruntime > -10 and self.conf.asinrealruntime < 0:
                                if self.streamtime > 6 and (sum(self.avgbr)/self.streamtime) < self.bpsrequired:
                                    self.reduceBitrate((sum(self.avgbr)/self.streamtime))
                                    self.conf.asinrealruntime = -99 # avoid player gettime, stream gets closed in a moment
                                else:
                                    self.conf.asinrealruntime = 0
                            elif self.conf.asinrealruntime == -22:
                                debug("AmazonHTTPClient requesting player total time again")
                                self.conf.asinrealruntime = 0
                                
                debug("AmazonHTTPClient Stream kbyte per second: " + str(bpsnow) + " (" + str(self.bpsrequired) + " required), Buffer: " + str(self.bflow))
                self.t = tnow
        else:
            if self.amazonbuffer[0].startswith(b"HTTP/1.1 206"):
                h = self.amazonbuffer[0][:self.amazonbuffer[0].find(b"\r\n\r\n")]
                sfor = b"Content-Range: bytes"
                p = h.find(sfor)
                h = h[p + len(sfor):h.find(b"\r\n",p)].strip() #Content-Range: bytes 0-7444812466/7444812467
                p0 = h[:h.find(b"-")]
                h = h[len(p0)+1:]
                p1 = h[:h.find(b"/")]
                p2 = h[len(p1)+1:]
                self.conf.streamlength = int(p2)
                self.maxsize = (self.conf.streamlength / (self.conf.asinruntime/1000)) * self.conf.maxbuffer
                self.bpsrequired = (self.conf.streamlength / (self.conf.asinruntime/1000)) / 1024
                if not (int(p1) - int(p0)) < self.maxsize:
                    self.streaming = True
                else:
                    debug("AmazonHTTPClient header requested byte range too short, not activating extended stream handling " + str(int(p1) - int(p0)))
                debug("AmazonHTTPClient streamlength: " + str(self.conf.streamlength) + ", asinruntime: " + str(self.conf.asinruntime/1000))

    def writable(self):
        return (len(self.amazonbuffer[1]) > 0)

    def handle_write(self):
        sent = self.send(self.amazonbuffer[1])
        self.amazonbuffer[1] = self.amazonbuffer[1][sent:]
        

class PrimeProxyHandler(asyncore.dispatcher):
    
    def __init__(self, sock, getAsinInfo):
        asyncore.dispatcher.__init__(self, sock)
        debug("PrimeProxyHandler __init__")
        self.getAsinInfo = getAsinInfo
        self.amazon = None
        self.clientrequest = str()
        self.amazonrequest = str()
        self.amazonreceive = str()
        self.amazonbuffer = [self.amazonreceive, self.amazonrequest]
        self.amazonsocket = None
        self.conf = None
        self.isreducing = False
        self.myhandlerid = 0
        self.cl = False

    def handle_connect(self):
        self.amazonbuffer[0] = str()
        self.amazonbuffer[1] = str()
        debug("PrimeProxyHandler handle_connect")
        
    def handle_close(self):
        self.cl = True
        self.amazonbuffer[0] = str()
        self.clientrequest = str()
        debug("PrimeProxyHandler handle_close")
        if self.amazonsocket:
            if self.amazonsocket.connected:
                self.amazonsocket.close()
            self.amazonsocket = None
        
    def readAsinFromUri(self, s):
        s = s[:s.find("\r\n")].strip()
        s = s[s.find(" ")+2:s.find(" ",s.find(" ")+1)]
        s = s[:s.find(".mp4")]
        self.conf = self.getAsinInfo(s)
        if self.conf.asinrealruntime < 0: self.conf.asinrealruntime = 0
    
    def readable(self):
        return not self.cl

    def handle_read(self): # read client
        hread = self.recv(8192)
        if not hread: return
        self.clientrequest += hread
        if len(self.clientrequest) > 0:
            if self.clientrequest.startswith(b"HEAD ") and b"\r\n\r\n" in self.clientrequest: #headers :)  or self.buf.request.startswith("GET ")
                reqheader = self.clientrequest[:self.clientrequest.find(b"\r\n\r\n")+len(b"\r\n\r\n")]
                self.clientrequest = self.clientrequest[len(reqheader):]
                self.readAsinFromUri(reqheader)
                self.amazon = self.conf.getUrlParams(self.conf.streamindex)
                reqheader = reqheader.replace(b"HEAD /" + self.conf.asin + b".mp4 HTTP", b"HEAD "+ self.amazon["uri"] + b" HTTP") #Host: 127.0.0.1:59950
                reqheader = reqheader.replace(b"Host: 127.0.0.1:59950", b"Host: "+ self.amazon["host"]) #Host: 127.0.0.1:59950
                self.amazonbuffer[1] = reqheader
                pass
            elif self.clientrequest.startswith(b"GET ") and b"\r\n\r\n" in self.clientrequest: #headers :)  or self.buf.request.startswith("GET ")
                reqheader = self.clientrequest[:self.clientrequest.find(b"\r\n\r\n")+len(b"\r\n\r\n")]
                self.clientrequest = self.clientrequest[len(reqheader):]
                self.readAsinFromUri(reqheader)
                self.amazon = self.conf.getUrlParams(self.conf.streamindex)
                reqheader = reqheader.replace(b"GET /" + self.conf.asin + b".mp4 HTTP", b"GET "+ self.amazon["uri"] + b" HTTP") #Host: 127.0.0.1:59950
                reqheader = reqheader.replace(b"Host: 127.0.0.1:59950", b"Host: "+ self.amazon["host"]) #Host: 127.0.0.1:59950
                self.amazonbuffer[1] = reqheader
            
            if self.amazonsocket is None:
                try:
                    self.amazonsocket = AmazonHTTPClient(self.conf, self.amazon["host"], self.amazonbuffer)
                    self.amazonsocket.reduceBitrate = self.reduceBitrate
                except:
                    debug("NO AMAZON SOCKET, CREATING ONE FAILED")
            


    def writable(self):
        return (len(self.amazonbuffer[0]) > 0 and self.amazonsocket)

    def handle_write(self):
        sent = self.send(self.amazonbuffer[0])
        self.amazonbuffer[0] = self.amazonbuffer[0][sent:]
            
    def reduceBitrate(self, avgBitrate = None):
        if not self.isreducing:
            usebitrateindex = -1
            if avgBitrate is not None:
                avgBitrate -= (avgBitrate / 10)
                for c, k in enumerate(self.conf.slist):
                    if (k['bitrate']/8) < avgBitrate:
                        usebitrateindex = c
            
            if usebitrateindex > -1:
                self.conf.streamindex = usebitrateindex
                debug("PrimeProxyHandler Using new bitrate: " + str(self.conf.slist[self.conf.streamindex]['bitrate']) + "; avg: " + str(avgBitrate * 8))
                self.isreducing = True
                self.execPlayer()
            else:
                if self.conf.tryLower():
                    self.isreducing = True
                    self.execPlayer()
            return True
        debug("PrimeProxyHandler ignoring reduce bitrate request, already reducing")
        return False
    
    def execPlayer(self):
        addon = xbmcaddon.Addon()
        addonPath = addon.getAddonInfo('path').decode('utf-8')
        apivplayer = os.path.join(addonPath, "PlayerProc.py")
        runscript = unicode('XBMC.RunScript('+ apivplayer + ',play,asin=' + self.conf.asin + ',title=' + self.conf.asintitle + ',thumbnailimage=' + self.conf.asinthumbnailimage + ')')
        xbmc.executebuiltin(runscript.encode("utf-8"))


class PrimeProxy(asyncore.dispatcher):

    def __init__(self, host, port, pcontrol):
        asyncore.dispatcher.__init__(self)
        debug("PrimeProxy __init__")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(10)
        self.pcontrol = pcontrol

    def handle_accept(self):
        debug("PrimeProxy handle_accept")
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            debug('PrimeProxy incoming connection from ' + repr(addr))
            PrimeProxyHandler(sock, self.getAsinConfig)
            
            
    def getAsinConfig(self, asin):
        return self.pcontrol.streamConfiguration[asin]


class streamConfig():

    def __init__(self):
        self.maxbuffer = 10
        self.streamindex = 0
        self.slist = None
        self.asin = None
        self.asinruntime = 0
        self.asinrealruntime = 0
        self.asintitle = None
        self.asinthumbnailimage = ""
    
    def tryHigher(self):
        if (len(self.slist)-1) > self.streamindex:
            self.streamindex += 1
            return True
        return False
    
    def tryLower(self):
        if self.streamindex > 0:
            self.streamindex -= 1
            return True
        return False
    
    def setHighest(self):
        self.streamindex = len(self.slist)-1
        
    def getUrlParams(self, i):
        self.streamindex = i
        u = self.slist[i]['url']
        proto = u[:u.find("://")]
        host = u[len(proto)+3:u.find("/", len(proto) + 3)]
        uri = u[len(proto) + 3 + len(host):]
        return {"proto": proto, "host": host, "uri": uri}

class PrimeControlHandler(asyncore.dispatcher):
    
    def __init__(self, sock, setConfig, getConfig):
        asyncore.dispatcher.__init__(self, sock)
        self.conf = None
        self.setConfig = setConfig
        self.getConfig = getConfig
        self.buffer = ""
        self.bufferout = ""
    
    def handle_connect(self):
        debug("PrimeControlHandler handle_connect")
    
    def handle_read(self): # read client
        self.buffer += self.recv(8192)
        while "\r\n" in self.buffer:
            pos = self.buffer.find("\r\n")
            cmd = self.buffer[:pos+2].strip()
            self.buffer = self.buffer[pos+2:]
            self.parsecmd(cmd)

    
    def writable(self):
        return (len(self.bufferout) > 0)

    def handle_write(self):
        sent = self.send(self.bufferout)
        self.bufferout = self.bufferout[sent:]
        
    def sendAnswer(self, isSuccess = True, message = "OK"):
        jsonstring = ""
        if isSuccess:
            jsonstring = {"status": "success", "message": str(message)}
        else:
            jsonstring = {"status": "error", "message": str(message)}
        self.send(base64.b64encode(json.dumps(jsonstring)) + "\r\n")
    
    def parsecmd(self, cmd):
        request = json.loads(base64.b64decode(cmd))
        if "asin" in request and request["asin"]:
            self.conf = self.getConfig(request["asin"])
            for prop, value in request["setProperties"].iteritems():
                prop = "setAsin" + prop
                self.setProp(prop, value)
            self.setConfig(self.conf)
            self.sendAnswer()
        else:
            if "hello" in request and request["hello"]:
                self.justAnswer()
            else:
                self.sendAnswer(False, "error while setting properties")
    
    def setProp(self, prop, value):
        if prop == "setAsinStreamingIndex": self.setAsinStreamingIndex(value)
        if prop == "setAsinRuntime": self.setAsinRuntime(value)
        if prop == "setAsinRealRuntime": self.setAsinRealRuntime(value)
        if prop == "setAsinStreamingList": self.setAsinStreamingList(value)
        if prop == "setAsinThumbnailImage": self.setAsinThumbnailImage(value)
        if prop == "setAsinTitle": self.setAsinTitle(value)
            
    def setAsinStreamingIndex(self, value):
        self.conf.streamindex = value
        pass

    def setAsinRuntime(self, value):
        self.conf.asinruntime = int(value)
        pass
    
    def setAsinRealRuntime(self, value):
        self.conf.asinrealruntime = value
        pass
    
    def setAsinStreamingList(self, value):
        self.conf.slist = value
        pass
    
    def setAsinThumbnailImage(self, value):
        self.conf.asinthumbnailimage = value
        pass
    
    def setAsinTitle(self, value):
        self.conf.asintitle = value
        pass
    
    def justAnswer(self):
        self.sendAnswer()
        pass
    
class PrimeControlServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        debug("PrimeControlServer __init__")
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.streamConfiguration = {}
        
    def handle_accept(self):
        debug("PrimeControlServer handle_accept")
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            debug('PrimeControlServer incoming connection from ' + repr(addr))
            handler = PrimeControlHandler(sock, self.setConfig, self.getConfig)
    
    def setConfig(self, sc):
        self.streamConfiguration[sc.asin] = sc
        
    def getConfig(self, asin):
        if asin in self.streamConfiguration:
            return self.streamConfiguration[asin]
        else:
            sc = streamConfig()
            sc.asin = asin
            return sc


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    debug("startup vbs")
    primecontrol = PrimeControlServer('127.0.0.1', 59910)
    primeproxy = PrimeProxy('127.0.0.1', 59950, primecontrol)
    while asyncore.socket_map and not monitor.abortRequested():
        asyncore.loop(1, count=1)
        time.sleep(0.1)
    log("exited")

