import json
import time
import asyncio
import aiohttp
import urllib3
import requests
import multiprocessing

async def GetArtistTotal(ArtistID,session):
    with open("config.json","r",encoding="utf_8") as configFiles:
        config = json.load(configFiles)
        configFiles.close()
    user_agent = config["user_agent"]
    cookie = config["cookie"]
    referer = f"https://www.pixiv.net/users/{ArtistID}"
    headers = {"user-agent":f"{user_agent}","cookie":f"{cookie}","referer":f"{referer}"}
    url = f"https://www.pixiv.net/ajax/user/{ArtistID}/profile/all?lang=zh_tw"
    while True:
        try:
            async with await session.get(url=url,headers=headers) as Req:
                ReqData = await Req.json()
                IDS = ReqData["body"]["illusts"]
                if Req.status == 200:
                    break
                else:
                    time.sleep(200)
                    continue
        except:
            continue
    IDList = []
    for i in IDS.keys():
        IDList.append(int(i))
    return IDList

async def GetDownloadLink(ID,session):
    with open("config.json","r",encoding="utf_8") as configFiles:
        config = json.load(configFiles)
        configFiles.close()
    user_agent = config["user_agent"]
    cookie = config["cookie"]
    referer = f"https://www.pixiv.net/artworks/{ID}"
    headers = {"user-agent":f"{user_agent}","cookie":f"{cookie}","referer":f"{referer}"}
    url = f"https://www.pixiv.net/ajax/illust/{ID}/pages?lang=zh"
    while True:
        try:
            async with await session.get(url=url,headers=headers) as Req:
                if Req.status == 200:
                    ReqData = await Req.json()
                    DownloadUrls = ReqData["body"]
                    break
                else:
                    time.sleep(200)
                    continue
        except:
            continue
    Result = {}
    Result[f"{ID}"] = [i["urls"]["original"] for i in DownloadUrls]
    return Result

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
        try:
            Req = requests.get(f"{Url}",headers=headers,verify=False)
            if Req.status_code == 200:
                with open(f"IMG\{ArtistName}\{ID}-{Number}.jpg","wb") as IMG:
                    IMG.write(Req.content)
                break
            else:
                time.sleep(240)
                continue
        except:
            continue

async def ArtistDownloader(ArtistName,ArtistID):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(GetArtistTotal(ArtistID,session))]
        IDList = await asyncio.gather(*tasks)
        IDList = IDList[0]
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(GetDownloadLink(ID,session)) for ID in IDList]
        DownloadLink = await asyncio.gather(*tasks)
    Program = multiprocessing.Pool()
    for Dict in DownloadLink:
        ID = list(Dict.keys())[0]
        for Number in range(0,len(Dict[f"{ID}"]),1):
            Program.apply_async(Download,args=(ArtistName,ID,Number,Dict[f"{ID}"][Number]))
    Program.close()
    Program.join()