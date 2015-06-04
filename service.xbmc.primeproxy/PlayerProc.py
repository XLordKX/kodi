import xbmc
import xbmcgui
import xbmcplugin
import sys
import time
import json
import base64
import socket
import time
import urllib

def build_url(query):
    return '?' + urllib.urlencode(query)

def sendRealTime(t):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 59910))
    s.sendall(base64.b64encode(json.dumps({"asin": asin, "setProperties": {"RealRuntime" : t}})) + "\r\n")
    pcdata = ""
    while not "\r\n" in pcdata:
        pcdata += s.recv(1024)
        pass
    s.close()

if __name__ == '__main__':
    if "play" in str(sys.argv) and "asin=" in str(sys.argv):
        asin = ""
        title = asin
        thumbnailimage = ""
        for i in sys.argv:
            if i.startswith("asin="):
                asin = i[len("asin="):]
            if i.startswith("title="):
                title = i[len("title="):]
            if i.startswith("thumbnailimage="):
                thumbnailimage = i[len("thumbnailimage="):]
        params = build_url({"mode": "changeStream", "url": asin, "thumbnailimage": thumbnailimage, "title": title})
        xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":"1","method":"Player.Open","params":{ "item": {"file":"plugin://plugin.video.prime_instant/'+params+'"} }}')
        
    if "gettime" in str(sys.argv) and "asin=" in str(sys.argv):
        if xbmc.Player().isPlaying():
            for i in sys.argv:
                if i.startswith("asin="):
                    asin = i[len("asin="):]
            tstart = time.time()
            if xbmc.Player().isPlaying():# and int(xbmc.Player().getTime()) > 0:
                xt = xbmc.Player().getTotalTime()
                if int(xt) > 0:
                    sendRealTime(xt)
                else:
                    sendRealTime(-22)
            else:
                sendRealTime(-2)
        else:
            sendRealTime(-1)