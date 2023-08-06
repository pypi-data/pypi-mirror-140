import json
import time

import requests

SERVER_URL = 'http://uif01.xyz/client'
API_KEY = '172574895'
DELAY_SECOND = 120


def HeartBeat():
    res = requests.get('http://ip-api.com/json/?lang=zh-CN').text
    res = json.loads(res)
    res['api_key'] = API_KEY
    res['fuc'] = 'HeartBeat'
    while True:
        try:
            requests.get(SERVER_URL, params=res)
        except:
            pass
        time.sleep(DELAY_SECOND)


HeartBeat()
