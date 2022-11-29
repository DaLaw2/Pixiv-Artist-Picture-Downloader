import json
import time
import urllib3
import requests
import multiprocessing

def GetArtistTotal(ArtistID):
    with open("config.json","r",encoding="utf_8") as configFiles:
        config = json.load(configFiles)
        configFiles.close()
    user_agent = config["user_agent"]
    cookie = config["cookie"]
    referer = f"https://www.pixiv.net/users/{ArtistID}"
    headers = {"user-agent":f"{user_agent}","cookie":f"{cookie}","referer":f"{referer}"}
    url = f"https://www.pixiv.net/ajax/user/{ArtistID}/profile/all?lang=zh_tw"
    while True:
        Req = requests.get(f"{url}",headers=headers)
        if Req.status_code == 200:
            IDS = json.loads(Req.content)["body"]["illusts"]
            break
        else:
            time.sleep(200)
            continue
    IDList = []
    for i in IDS.keys():
        IDList.append(int(i))
    return IDS

def GetDownloadLink(ID,LOCK,Dict):
    with open("config.json","r",encoding="utf_8") as configFiles:
        config = json.load(configFiles)
        configFiles.close()
    user_agent = config["user_agent"]
    cookie = config["cookie"]
    referer = f"https://www.pixiv.net/artworks/{ID}"
    headers = {"user-agent":f"{user_agent}","cookie":f"{cookie}","referer":f"{referer}"}
    url = f"https://www.pixiv.net/ajax/illust/{ID}/pages?lang=zh"
    while True:
        Req = requests.get(f"{url}",headers=headers)
        if Req.status_code == 200:
            DownloadUrls = json.loads(Req.content)["body"]
            break
        else:
            time.sleep(200)
            continue
    Result = []
    for i in DownloadUrls:
        Result.append(i["urls"]["original"])
    LOCK.acquire()
    Dict[f"{ID}"] = Result
    LOCK.release()

def Download(ArtistName,ID,Number,Url):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    with open("config.json","r",encoding="utf_8") as configFiles:
        config = json.load(configFiles)
        configFiles.close()
    user_agent = config["user_agent"]
    cookie = config["cookie"]
    referer = f"https://www.pixiv.net/"
    headers = {"user-agent":f"{user_agent}","cookie":f"{cookie}","referer":f"{referer}"}
    while True:
        Req = requests.get(f"{Url}",headers=headers,verify=False)
        if Req.status_code == 200:
            with open(f"IMG\{ArtistName}\{ID}-{Number}.jpg","wb") as IMG:
                IMG.write(Req.content)
            break
        else:
            time.sleep(200)
            continue

def ArtistDownloader(ArtistName,ArtistID):
    IDList = GetArtistTotal(ArtistID)
    M = multiprocessing.Manager()
    Program = multiprocessing.Pool()
    Dict=M.dict()
    LOCK=M.Lock()
    for ID in IDList:
        Program.apply_async(GetDownloadLink,args=(ID,LOCK,Dict))
    Program.close()
    Program.join()
    Program2 = multiprocessing.Pool()
    for i in Dict.keys():
        for j in range(0,len(Dict[f"{i}"]),1):
            Program2.apply_async(Download,args=(ArtistName,i,j,Dict[f"{i}"][j]))
    Program2.close()
    Program2.join()