import json 
import os
import time
import requests
import math
import urllib.request
from datetime import datetime, timezone
 
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
header = {
    "content-type": "application/json",
    'User-Agent': user_agent
}
 
url = "https://earthmc.net/map/tiles/_markers_/marker_earth.json"
user_url = "https://earthmc.net/map/up/world/earth/"
# discord_url = "https://discord.com/api/webhooks/897874529815257118/EVwrOak-rUUPHUpboapsjv5q7gxx-5MMF6HaYIlSyefBK6yvhfE_pqVJjd5h5kdZPf8P"
discord_url = "https://canary.discord.com/api/webhooks/898020112983011348/opcxOPRFTPI2yRA1_YYwVu2qHcIuCSpXZRLVy19fvT41HHmP8sqbJcZGWcSbd7A8aSU_"
debug = True

focus_mode = False
oniya = False

def dprint(text):
    if debug:
        print(text)


def get_latest_marker_data() -> dict:
    response = requests.get(url, headers=header)
    body:dict = response.json()
    return body

def get_latest_user_data() -> dict:
    response = requests.get(user_url, headers=header)
    body:dict = response.json()
    return body

def is_latest(timestamp) -> bool:
    cache = 0
    with open('timestamp', mode='r') as f:
        cache = f.read()
    if timestamp == cache:
        return True
    else:
        with open('timestamp', mode='w') as f:
            f.write(str(timestamp))
            return False


def area_parse(file_name):
    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
        with open("area_parsed.json", mode='w', encoding='utf-8') as fs:
            data = data["sets"]["townyPlugin.markerset"]["areas"]
            fs.write(json.dumps(data, ensure_ascii=False, indent=4))

def send_discord(data):
    header = {"content-type": "application/json"}
    time.sleep(1)
    dprint(data)
    result = requests.post(discord_url, data=data, headers= header)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))

def send_deleted_notify(deleted_towny:str) -> None:
    data = 0
    with open("area_parsed_old.json", mode='r', encoding='utf-8') as fs:
        temp = json.load(fs)
        data = temp[deleted_towny]

    content = {"content": None}
    content["embeds"] = [{
      "title": "DELETED Towny",
      "url": f"https://earthmc.net/map/?worldname=earth&mapname=flat&zoom=8&x={str(data['x'][0])}&y=64&z={str(data['z'][0])}",
      "description": "Town name: " + deleted_towny,
      "color": 16711680,
      "fields": [
        {
          "name": "X-pos",
          "value": str(data['x'][0]),
          "inline": True
        },
        {
          "name": "Z-pos",
          "value": str(data['z'][0]),
          "inline": True
        },
        {
          "name": "Nether X-pos(unconfirmed)",
          "value": str(math.floor(data['x'][0] / 8)),
          "inline": True
        },
        {
          "name": "Nether Z-pos(unconfirmed)",
          "value": str(math.floor(data['z'][0] / 8)),
          "inline": True
        }
      ]
    }]
    
    send_discord(json.dumps(content))

def send_added_notify(added_towny:str) -> None:
    data = 0
    with open("area_parsed.json", mode='r', encoding='utf-8') as fs:
        temp = json.load(fs)
        data = temp[added_towny]

    content = {"content": None}
    content["embeds"] = [{
      "title": "ADDED Towny",
      "url": f"https://earthmc.net/map/?worldname=earth&mapname=flat&zoom=8&x={str(data['x'][0])}&y=64&z={str(data['z'][0])}",
      "description": "Town name: " + added_towny,
      "color": 65280,
      "fields": [
        {
          "name": "X-pos",
          "value": str(data['x'][0]),
          "inline": True
        },
        {
          "name": "Z-pos",
          "value": str(data['z'][0]),
          "inline": True
        },
        {
          "name": "Nether X-pos(unconfirmed)",
          "value": str(math.floor(data['x'][0] / 8)),
          "inline": True
        },
        {
          "name": "Nether Z-pos(unconfirmed)",
          "value": str(math.floor(data['z'][0] / 8)),
          "inline": True
        }
      ]
    }]
    
    send_discord(json.dumps(content))

def check_area():
    olddata = 0
    data = 0

    with open("area_parsed_old.json",mode='r', encoding='utf-8') as f:
        olddata = json.load(f)
    with open("area_parsed.json",mode='r', encoding='utf-8') as f:
        data = json.load(f)

    for i in olddata.keys():
        if not i in data.keys():
            if i[-5:]!="_Shop":
                send_deleted_notify(i)
                focus_mode = True
        
    for i in data.keys():
        if not i in olddata.keys():
            if i[-5:]!="_Shop":
                send_added_notify(i)

def check():
    try:
        data = get_latest_marker_data()
    except:
        pass
    else:
        if not (is_latest(data["timestamp"])):
            dt_local_aware = datetime.now().astimezone()
            dprint(f"[{dt_local_aware.isoformat()}]" + "Cache miss. get latest data.")
            with open('latest.json', 'w') as f:
                json.dump(data, f, indent=4)
            area_parse("latest.json")
            check_area()

            if os.path.exists("area_parsed_old.json"):
                os.remove("area_parsed_old.json")
            os.rename("area_parsed.json", "area_parsed_old.json")

def check_oniya():
    global oniya
    try:
        data = get_latest_user_data()
    except:
        pass
    else:
        for i in data["players"]:
            if i["account"] == "oniyao228":
                if not oniya:
                    oniya = True
                    content = {"content": None}
                    content["embeds"] = [{
                    "title": "Logged in oniya",
                    "description": "",
                    "color": 65280}]
                    send_discord(json.dumps(content))
                break
        else:
            if oniya:
                oniya = False
                content = {"content": None}
                content["embeds"] = [{
                "title": "Logged out oniya",
                "description": "",
                "color": 16711680}]
                send_discord(json.dumps(content))

if __name__ == "__main__":
    # init
    while True:
        check()
        check_oniya()
        if focus_mode:
            time.sleep(30)
        else:
            time.sleep(120)
