# -*- coding:utf-8 -*-

import requests
import time
import hmac
import hashlib
import json
import random


host = "https://api.hoolgd.com"
client_id = "7q4tSQgcrJbELFm96K2No2bRwtT9Ya"
client_key = "esCXQSRJK4q5dwyjUaPiSHEJpxZrTpe31LvwD5tRmy67MqfCXv"

def gen_sign(client_id, client_key):
    ts = int(time.time())
    nonce = "abcdefg"
    obj = {"ts": ts, "nonce": nonce, "sign": "", "client_id": client_id}
    s = "client_id=%s&nonce=%s&ts=%s" % (client_id, nonce, ts) 
    v = hmac.new(client_key.encode(), s.encode(), digestmod=hashlib.sha256)
    obj["sign"] = v.hexdigest()
    return obj 
#得到gate深度
def get_gatecoin():
    url = 'https://data.gateapi.io/api2/1/orderBooks'
    try:
        data = {}
        data = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        print('获取GATE币深度正常')
    except:
        #time.sleep(random.uniform(1, 3))
        data = {}
        print("无法获取GATE币深度状态")
    return data
#得到gate pair
def get_gatepairs():
    url = 'https://data.gateapi.io/api2/1/pairs'
    try:
        data = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        print('获取GATE币交易对正常')

    except:
        #time.sleep(random.uniform(1, 3))
        print("无法获取GATE交易对")
    return data

def get_hoodepth(symbol1):
    try:
        h_depth={}
        path = "/open/v1/depth"
        obj = gen_sign(client_id, client_key)
        obj.update({"symbol": symbol1})
        res = requests.get(host + path, params=obj)
        h_depth = json.loads(res.content)['data']
        #print('获取HOO币状态正常')
    except:
        time.sleep(random.uniform(1, 3))
        #print('HOO无法获取',symbol1,'币状态') 
    
    return h_depth

def get_hoopairs():
    try:
        pairs=[]
        path = "/open/v1/tickers"
        obj = gen_sign(client_id, client_key)
        res = requests.get(host + path, params=obj)
        temp = json.loads(res.content)['data']
        for i in temp:
            pairs.append(i['symbol'])
        print('获取HOO币状态正常')
    except:
        time.sleep(random.uniform(1, 3))
        pairs=[]
        print('HOO无法获取',symbol1,'币状态') 
    return pairs


#main-------------------------------------------------------
del_coin = ['ETC','MTR','ULU','TAI','RVC','DILI','STX','DEGO']


while True:
    pairs=[]
    gate_date= []
    pairs2 =[]
    hoo_pairs=[]
    hoo_depth={}
    gate_bid_price = 9999999
    gate_bid_vlo = 0
    gate_ask_price = 9999999
    gate_ask_vlo = 0
    try:
        pairs = get_gatepairs()

        for par in pairs:
            del_status = False
            for s in del_coin:
                #print(s)
                if s in par:
                    del_status = True
                    break

            if del_status:
                pass
            else:
                pairs2.append(par) 

        #print(pairs2)
        gate_date = get_gatecoin()
        #print(gate_date)
        hoo_pairs = get_hoopairs()
        pairs_new2 = [i.replace('_','-') for i in pairs2]# if '_USDT' in i]
        pairs_new = set(hoo_pairs) & set(pairs_new2)
        #print(pairs_new2)
        #print(hoo_pairs)
        #print(pairs_new)
        for i in pairs_new:
            try:
                hoo_depth = get_hoodepth(i)
                #print(hoo_depth)
                if hoo_depth == {} or hoo_depth['bids'] ==[] or gate_date == {} :
                    hoo_bid_price =99999999999999
                    hoo_bid_vol =0
                    hoo_ask_price =99999999999999
                    hoo_ask_vol =0 
                else:  
                    hoo_bid_price =hoo_depth['bids'][0]['price']
                    hoo_bid_vol =hoo_depth['bids'][0]['quantity']
                    hoo_ask_price =hoo_depth['asks'][0]['price']
                    hoo_ask_vol =hoo_depth['asks'][0]['quantity'] 

                temp_pair = i.replace('-','_').lower()
                #print(temp_pair)
                gate_bid_price = gate_date[temp_pair]['bids'][0][0]
                gate_bid_vlo = gate_date[temp_pair]['bids'][0][1]
                gate_ask_price = gate_date[temp_pair]['asks'][-1][0]
                gate_ask_vlo = gate_date[temp_pair]['asks'][-1][1]
                
                if float(gate_bid_price)/float(hoo_ask_price) > 1.01 and float(gate_bid_price)/float(hoo_ask_price) <2:
                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((float(gate_bid_price)/float(hoo_ask_price)-1)*100,'.3f'),'%','|',i, '|GATE---> HOO|',  gate_bid_price, hoo_ask_price,'|',gate_bid_vlo,hoo_ask_vol)
                elif float(hoo_bid_price)/float(gate_ask_price) > 1.01 and float(hoo_bid_price)/float(gate_ask_price) <2:
                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((float(hoo_bid_price)/float(gate_ask_price)-1)*100,'.3f'),'%','|',i, '|HOO---> GATE|',  hoo_bid_price, gate_ask_price,'|',hoo_bid_vol,gate_ask_vlo)    
                else:
                    pass#print(i,'checked!')
                time.sleep(random.uniform(1, 2))
            except:
                #print(i,'Error!')   
                continue 
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"Running, next round starting!",'-'*15)    
        time.sleep(10)
    except:
        
        continue
