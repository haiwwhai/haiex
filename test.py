# -*- coding: utf-8 -*-
#binance bitmax hoo gateIO Poloneix huobi
import requests
import time
import random
import sys
import hmac
import hashlib
import json
import smtplib
from email.mime.text import MIMEText
import http.client
def getSign(params, secretKey):
    bSecretKey = bytes(secretKey, encoding='utf8')

    sign = ''
    for key in params.keys():
        value = str(params[key])
        sign += key + '=' + value + '&'
    bSign = bytes(sign[:-1], encoding='utf8')

    mySign = hmac.new(bSecretKey, bSign, hashlib.sha512).hexdigest()
    return mySign

def httpPost(url, resource, params, apiKey, secretKey):
     headers = {
            "Content-type" : "application/x-www-form-urlencoded",
            "KEY":apiKey,
            "SIGN":getSign(params, secretKey)
     }

     conn = http.client.HTTPSConnection(url, timeout=10)

     tempParams = urllib.parse.urlencode(params) if params else ''
     conn.request("POST", resource, tempParams, headers)
     response = conn.getresponse()
     data = response.read().decode('utf-8')
     params.clear()
     conn.close()
     return data

def get_gate_fee():
    url= 'data.gateapi.io'
    URL = "/api2/1/private/feelist"
    apiKey = 'EDF07FEF-02E9-4E5A-B171-B2A9A7E48207'
    secretKey = '059e9f6cfad083e092446325377b02570fb92d59e33006719c57d6d43b4f1572'
    params = {}
    fee = httpPost(url, URL, params, apiKey, secretKey)
    return eval(fee)
    
s = get_gate_fee()
print(s['HIT']['withdraw_fix'])