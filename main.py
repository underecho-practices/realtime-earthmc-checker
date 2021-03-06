import json 
import os
import time
import requests
import math
import sys
from datetime import datetime, timezone
 
# Fake user agant
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
header = {
    "content-type": "application/json",
    'User-Agent': user_agent
}
 
url = "https://earthmc.net/map/tiles/_markers_/marker_earth.json"
user_url = "https://earthmc.net/map/up/world/earth/"
discord_url = ""

focus_mode = False
oniya = False

def ascii_init():
    a = """
   ('-.    _   .-')                
 _(  OO)  ( '.( OO )_              
(,------.  ,--.   ,--.)   .-----.  
 |  .---'  |   `.'   |   '  .--./  
 |  |      |         |   |  |('-.  
(|  '--.   |  |'.'|  |  /_) |OO  ) 
 |  .--'   |  |   |  |  ||  |`-'|  
 |  `---.  |  |   |  | (_'  '--'\  
 `------'  `--'   `--'    `-----'  
"""
    print(a)
    print("        Presented by GunmaSamurais")
    print("              Coded by under.#2547\n\n\n\n\n")

    print(f"Map marker url: {url}")
    print(f"User data url: {user_url}")
    print(f"WebHook url: {discord_url}")
    
    

def get_latest_marker_data() -> dict:
    response = requests.get(url, headers=header)
    body:dict = response.json()
    return body

def get_latest_user_data() -> dict:
    response = requests.get(user_url, headers=header)
    body:dict = response.json()
    return body

def split_list(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

def area_parse(file_name):
    with open(file_name, encoding='utf-8') as f:
        data = json.load(f)
        with open("area_parsed.json", mode='w', encoding='utf-8') as fs:
            data = data["sets"]["townyPlugin.markerset"]["areas"]
            fs.write(json.dumps(data, ensure_ascii=False, indent=4))

def send_discord(data):
    header = {"content-type": "application/json"}
    time.sleep(1)
    result = requests.post(discord_url, data=data, headers= header)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))

def send_deleted_notify(deleted_towny:list) -> None:
    all_data: list = []
    with open("area_parsed_old.json", mode='r', encoding='utf-8') as fs:
        temp = json.load(fs)
        all_data = [temp[i] for i in deleted_towny]

    content = {"content": None}
    content["embeds"] = []
    for data in all_data:
        content["embeds"].append({
        "title": "DELETED Towny",
        "url": f"https://earthmc.net/map/?worldname=earth&mapname=flat&zoom=8&x={str(data['x'][0])}&y=64&z={str(data['z'][0])}",
        "description": "Town name: " + data["label"],
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
        })

    
    send_discord(json.dumps(content))

def send_added_notify(added_towny:list) -> None:
    all_data: list = []
    with open("area_parsed.json", mode='r', encoding='utf-8') as fs:
        temp = json.load(fs)
        all_data = [temp[i] for i in added_towny]

    content = {"content": None}
    content["embeds"] = []
    for data in all_data:
        content["embeds"].append({
        "title": "ADDED Towny",
        "url": f"https://earthmc.net/map/?worldname=earth&mapname=flat&zoom=8&x={str(data['x'][0])}&y=64&z={str(data['z'][0])}",
        "description": "Town name: " + data["label"],
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
        })
    
    send_discord(json.dumps(content))

def check_area():
    olddata = 0
    data = 0
    deleted_data = []
    added_data = []

    with open("area_parsed_old.json",mode='r', encoding='utf-8') as f:
        olddata = json.load(f)
    with open("area_parsed.json",mode='r', encoding='utf-8') as f:
        data = json.load(f)

    for i in olddata.keys():
        if not i in data.keys():
            if i[-5:]!="_Shop":
                deleted_data.append(i)
                focus_mode = True
        
    for i in data.keys():
        if not i in olddata.keys():
            if i[-5:]!="_Shop":
                added_data.append(i)

    result = list(split_list(added_data, 10))
    for i in result:
        send_added_notify(i)

    result = list(split_list(deleted_data, 10))
    for i in result:
        send_deleted_notify(i)

def check():
    try:
        data = get_latest_marker_data()
    except:
        pass
    else:
        dt_local_aware = datetime.now().astimezone()
        print(f"[{dt_local_aware.isoformat()}]" + "Checking latest data.")
        with open('latest.json', 'w') as f:
            json.dump(data, f, indent=4)

        area_parse("latest.json")
        if not os.path.exists("area_parsed_old.json"):
            print(f"[{dt_local_aware.isoformat()}]" + "Historical data does not exist. aborted.")
            os.rename("area_parsed.json", "area_parsed_old.json")
            return
        else:
            check_area()
            check_oniya()
            done = False
            while not done:
                try:
                    if os.path.exists("area_parsed_old.json"):
                        os.remove("area_parsed_old.json")
                    os.rename("area_parsed.json", "area_parsed_old.json")
                    done = True
                except:
                    print("unexpected error. retrying....")

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
    if not os.path.exists("webhook"):
        print("webhook file doesn't exist. Check that you have created the file before launching it.")
        time.sleep(15)
        sys.exit(0)

    with open("webhook",mode='r', encoding='utf-8') as f:
        discord_url = f.read()

    
        
    ascii_init()
    
    while True:
        try:
            check()
        except:
            print("unexpected error. check github or DM me.")
            sys.exit(0)
            
        if focus_mode:
            time.sleep(30)
        else:
            time.sleep(120)
