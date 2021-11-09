import json 
import os
import time
import requests
import random
import urllib.request
 
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
header = {
    "content-type": "application/json",
    'User-Agent': user_agent
}
 
url = "https://tdhr.jp/zen-i/"
debug = True

def dprint(text):
    if debug:
        print(text)


def send_ohana(data):
    header = {"content-type": "application/json"}
    time.sleep(2)
    dprint(data)
    result = requests.post(url, data=data, headers= header)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(result.content)
        print("Payload delivered successfully, code {}.".format(result.status_code))


if __name__ == "__main__":
    # init
    while True:
        data = {}
        data["x"] = random.randint(0, 1400)
        data["y"] = random.randint(0, 1400)
        data["id"] = random.randint(20000, 254000000)
        send_ohana(json.dumps(data))
        time.sleep(1)
