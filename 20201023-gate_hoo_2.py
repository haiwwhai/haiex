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

min_req = 10  #dollor

def gen_sign(client_id, client_key):
    ts = int(time.time())
    nonce = "abcdefg"
    obj = {"ts": ts, "nonce": nonce, "sign": "", "client_id": client_id}
    s = "client_id=%s&nonce=%s&ts=%s" % (client_id, nonce, ts) 
    v = hmac.new(client_key.encode(), s.encode(), digestmod=hashlib.sha256)
    obj["sign"] = v.hexdigest()
    return obj 
#得到gate深度
def get_gatecoin(symbol1):
    url = 'https://data.gateapi.io/api2/1/orderBook/'+symbol1
    try:
        data = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        print('获取',symbol1,'币深度正常')
    except:
        data={}
        #time.sleep(random.uniform(1, 3))
        print('无法获取获取',symbol1,'深度')
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
        print('获取HOO币状态正常')
    except:
        pass#time.sleep(random.uniform(1, 3))
        print('HOO无法获取',symbol1,'币状态') 
    
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
        print('获取HOO交易对正常！')
    except:
        time.sleep(random.uniform(1, 3))
        pairs=[]
        print('HOO无法获取交易对！') 
    return pairs




#man=================================================================================================
min_profit =5 # dollar
del_coin = ['ETC','MTR','ULU','TAI','RVC','STX','DILI']

while True:
    try:
        pairs = get_gatepairs()
        pairs2 =[]
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

        hoo_pairs = get_hoopairs()
        pairs_new2 = [i.replace('_','-') for i in pairs2]# if '_USDT' in i]
        pairs_new = set(hoo_pairs) & set(pairs_new2)
        #pairs_new = ['AKRO-USDT','FOR-USDT']
        #print(pairs_new)
        for i in pairs_new:
            hoo_bid_price = []
            hoo_bid_vol = []
            hoo_ask_price =[]
            hoo_ask_vol =[]
            gate_bid_price = []
            gate_bid_vol = []
            gate_ask_price =[]
            gate_ask_vol =[]
            gate_hoo_vol = []
            hoo_gate_vol =[]
            
            hoo_depth = get_hoodepth(i)
            temp_pair = i.replace('-','_').lower()
            gate_date = get_gatecoin(temp_pair)
            #print(hoo_depth)
            #print(i)
            #print(gate_date)

            for t in range(0,5):  
                try:
                    if hoo_depth != {}:
                        hoo_bid_price.append(float(hoo_depth['bids'][t]['price']))
                        hoo_bid_vol.append(float(hoo_depth['bids'][t]['quantity']))
                        hoo_ask_price.append(float(hoo_depth['asks'][t]['price']))
                        hoo_ask_vol.append(float(hoo_depth['asks'][t]['quantity'])) 
                        #print('yes hoo')           
                    else:
                        break
                    #print(gate_date)
                    if gate_date != {}:                        
                        gate_bid_price.append(float(gate_date['bids'][t][0]))
                        gate_bid_vol.append(float(gate_date['bids'][t][1]))
                        gate_ask_price.append(float(gate_date['asks'][-t-1][0]))
                        gate_ask_vol.append(float(gate_date['asks'][-t-1][1]))
                        #print('yes gate') 
                    else:
                        break    
                    if gate_bid_price[0]/hoo_ask_price[0] > 1.01 :
                        if sum(hoo_ask_vol) > sum(gate_bid_vol):
                            min_gate_hoo_vol = sum(gate_bid_vol)
                            if len(hoo_ask_vol)>1:
                                hoo_ask_vol[-1] = min_gate_hoo_vol-hoo_ask_vol[0:-2]
                            else:
                                hoo_ask_vol[0] = min_gate_hoo_vol                                    
                        elif  sum(hoo_ask_vol) < sum(gate_bid_vol):
                            min_gate_hoo_vol =  sum(hoo_ask_vol)
                            if len(gate_bid_vol)>1:
                                gate_bid_vol[-1] = min_gate_hoo_vol-gate_bid_vol[0:-2]
                            else:
                                gate_bid_vol[0] = min_gate_hoo_vol

                        gate_bid_real = sum(map(lambda x,y: x * y, gate_bid_price,gate_bid_vol))
                        hoo_ask_real = sum(map(lambda x,y: x * y, hoo_ask_price,hoo_ask_vol))

                        if gate_bid_real-hoo_ask_real > min_profit :
                            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((gate_bid_price[0]/hoo_ask_price[0]-1)*100,'.3f'),'%','|GATE->HOO |',i,'|',format(gate_bid_real-hoo_ask_real,'.1f','$'),'|',gate_bid_price,hoo_ask_price,'|',gate_bid_vol,hoo_ask_vol)
                            break
                        else:
                            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((gate_bid_price[0]/hoo_ask_price[0]-1)*100,'.3f'),'%','|GATE->HOO |',i,'|',format(gate_bid_real-hoo_ask_real,'.1f','$'),'|','No depth!')
                            print(gate_bid_price,gate_bid_vol,'|',hoo_ask_price,hoo_ask_vol)
                    elif hoo_bid_price[0]/gate_ask_price[0] > 1.01 :
                        if sum(gate_ask_vol) > sum(hoo_bid_vol):
                            min_hoo_gate_vol = sum(hoo_bid_vol)
                            if len(gate_ask_vol)>1:
                                gate_ask_vol[-1] = min_hoo_gate_vol-gate_ask_vol[0:-2]
                            else:
                                gate_ask_vol[0] = min_hoo_gate_vol                                    
                        elif  sum(gate_ask_vol) < sum(hoo_bid_vol):
                            min_hoo_gate_vol =  sum(gate_ask_vol)
                            if len(hoo_bid_vol)>1:
                                hoo_bid_vol[-1] = min_hoo_gate_vol-hoo_bid_vol[0:-2]
                            else:
                                hoo_bid_vol[0] = min_hoo_gate_vol                        
                        gate_ask_real = sum(map(lambda x,y: x * y, gate_ask_price,gate_ask_vol))
                        hoo_bid_real = sum(map(lambda x,y: x * y, hoo_bid_price,hoo_bid_vol))                  
                         
                        if hoo_bid_real- gate_ask_real > min_profit:
                            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((hoo_bid_price[0]/gate_ask_price[0]-1)*100,'.3f'),'%','|HOO ->GATE|',i,'|',format(hoo_bid_real-gate_ask_real,'.1f'),'$','|',hoo_bid_price,gate_ask_price,'|',hoo_bid_vol,gate_ask_vol)
                            break 
                        else:
                            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((hoo_bid_price[0]/gate_ask_price[0]-1)*100,'.3f'),'%','|HOO ->GATE|',i,'|',format(hoo_bid_real-gate_ask_real,'.1f'),'$','|','No depth!' ) 
                            print(hoo_bid_price,hoo_bid_vol,'|',gate_ask_price,gate_ask_vol) 
                    else:
                        pass#print(i,'checked!')
                except:
                    continue
            time.sleep(random.uniform(1, 2))
    except:
        continue
    time.sleep(5)    
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),"Running, next round starting!",'-'*15)    
    
