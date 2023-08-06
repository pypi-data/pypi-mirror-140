#!/home/ai-046/anaconda3/bin/python3
# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# @File Name:        utils.py
# @Author:           wen
# @Version:          ver0_1
# @Created:          2022/2/10 上午10:56
# @Description:      Main Function:    xxx
# @Note:             xxx
# Function List:     hello() -- print helloworld
# History:
#       <author>    <version>   <time>      <desc>
#       wen         ver0_1      2020/12/15  xxx
# ------------------------------------------------------------------

import requests
import time

def translate(s: str, sleeptime=None):
    url = "http://fanyi.youdao.com/translate"
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': s
    }
    r = requests.get(url, params=data)
    result = r.json()
    if sleeptime: time.sleep(sleeptime)
    return result['translateResult'][0][0]['tgt']
