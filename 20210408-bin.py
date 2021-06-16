# -*- coding: utf-8 -*-
#20210106-update the gateio withdraw fee
#20210124-update the hoo ethersum wallet coins to check whether can withdraw or not
#20210206-update the condition with price gas small than 10
#20210209-updaate hoo withdraw fee
#20210214-update gateio, to delete key
import requests
import time
import random
import sys
import hmac
import hashlib
import json
import http.client
import urllib
from bs4 import BeautifulSoup
#import smtplib
#from email.mime.text import MIMEText


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
# 获取币圈行情，数据来源：非小号网站
'''
def getcurrentprice():
    n=0
    while True:
        try:
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
            url = 'https://dncapi.bqiapp.com/api/coin/web-coinrank?page=1&type=0&pagesize=100&webp=1'
            data = requests.get(url, headers=header).json()
            data1=data['data']
            bene={}
            bene['BTC']=[val for val in data1 if val['code']=='bitcoin'][0]['current_price']
            bene['ETH']=[val for val in data1 if val['code']=='ethereum'][0]['current_price']
            #bene['USDT'] = [val for val in data1 if val['code'] == 'tether'][0]['current_price']
            print('成功获取BTC，ETH价格')
            break
        except:
            if n<3:
                time.sleep(random.uniform(1, 3))
                n=n+1
                continue
            else:
                print('无法获取BTC，ETH，USDT价格。按BTC=80500，ETH=1614,USDT=6.94计算')
                bene={'BTC': 117800, 'ETH': 3275, 'USDT': 6.5}
                break
    return bene
'''
#得到币安api的整个数据
def get_binance_data(symbol):
    data=[]
    token=symbol.replace('/','')
    url='https://api.binance.com/api/v3/depth?symbol='+token
 
    try:
        temp=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data.append(temp['bids'])
        data.append(temp['asks']) 
        #print(temp)
    except:
        data=[]
        print("Binance "+symbol+" not response!")            
    return data   #'bidPrice': 'bidQty' 'askPrice':  'askQty': 

#得到gate深度
def get_bitmax_data(symbol):
    url = 'https://bitmax.io/api/pro/v1/depth?symbol='+symbol
    data=[]
    try:
        depth = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('获取',symbol1,'币深度正常')
        data.append(depth['data']['data']['bids'])
        data.append(depth['data']['data']['asks'])
        #data.append(depth)
        #print(data)     
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print('Bitmax '+symbol+' not response!')
    return data
#得到gate深度
def get_gate_data(symbol):
    i=symbol.replace('/','_')
    url = 'https://data.gateapi.io/api2/1/orderBook/'+i
    data=[]
    try:
        depth = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(depth['bids'])
        data.append(depth['bids'])
        #data.append(float(depth['bids'][0][1]))
        depth['asks'].reverse()
        data.append(depth['asks'])
        #print(data)
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print('Gate '+symbol+' not response!')
    return data
def get_huobi_data(symbol):
    i=symbol.replace('/','').lower()
    url = 'https://api.huobi.pro/market/depth?symbol='+i+'&type=step0&depth=20'
    data=[]
    try:
        depth = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(depth['bids'])
        depth['tick']['bids'].reverse()
        data.append(depth['tick']['bids'])  
        #data.append(float(depth['tick']['bids'][-1][1]))
        data.append(depth['tick']['asks'])
        #data.append(float(depth['tick']['asks'][0][1]))
        #print(data)
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print('Huobi '+symbol+' not response!')
    return data
def get_hoo_data(symbol):
    symbol1 = symbol.replace('/','-')
    data=[]
    try:        
        path = "/open/v1/depth"
        obj = gen_sign(client_id, client_key)
        obj.update({"symbol": symbol1})
        res = requests.get(host + path, params=obj)
        h_depth = json.loads(res.content)['data']
        data.append([[i['price'],i['quantity']] for i in h_depth['bids']])   #[{'price': '19287.17', 'quantity': '3.750289'},{}]
        #data.append(float(h_depth['bids'][0]['quantity']))
        data.append([[i['price'],i['quantity']] for i in h_depth['asks']])
        #data.append(float(h_depth['asks'][0]['quantity']))
        #print('获取HOO币状态正常')
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print('HOO '+symbol+' not response!') 
    
    return data
def get_pol_data(symbol):
    a=symbol.split('/')[0]
    b=symbol.split('/')[1]
    c=b+'_'+a 
    url="https://poloniex.com/public?command=returnOrderBook&currencyPair="+c+"&depth=20"  #depth 10  
    data=[]
    try:
        data1=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('P网正常')
        data.append(data1['bids'])  #[[price amount],[price amount]]
        data.append(data1['asks'])
    except:
        data = []
        print("Pwang "+symbol+" not response!")
    return data

#得到gate pair
def get_gate_pairs():
    url = 'https://data.gateapi.io/api2/1/pairs'
    url2 = 'https://data.gateapi.io/api2/1/coininfo'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data2 = [i.replace('_','/') for i in data1 if 'USDT' in i]
        data3 = requests.get(url2, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        status = data3['coins']
        data=[]
        for i in data2:
            for j in status:
                if i.split('/')[0] == list(j.keys())[0]:
                    temp=j[list(j.keys())[0]]
                    if temp['withdraw_disabled']== 1 or temp['deposit_disabled'] ==1:
                        break
                    else:
                        data.append(i)
                        break
        print('Get GATE    pairs sucessfully!')
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print("Can not Get GATE pairs!")
    return data
def get_hoo_pairs():
    try:
        pairs=[]
        get_hoo_fee = {'EOS': 0.1, 'BTC': 0.0005, 'ETH': 0.007, 'HC': 0.5, 'DASH': 0.02, 'NEO': 0.0, 'QTUM': 0.1, 'VET': 100.0, 'XRP': 0.1, 'DOGE':50.0, 'XMR': 0.01, 'BTM': 10.0, 'DCR': 0.01, 'HT': 0.8, 'PUB': 0.0, 'TPT': 100.0, 'RBF': 2.39391625, 'KAN': 900.0, 'BNB': 0.001, 'OMG': 1.5, 'ZRX': 10.0, 'ZIL': 0.1, 'DLB': 20.0, 'AE': 10.0, 'AION': 94.0, 'AMB': 499.0, 'AOA': 700.0, 'ATX': 4031.20482777, 'AUTO': 3625.30649559, 'BAT': 5.0, 'BIX': 11.53565654, 'BLZ': 50.0, 'BNT': 5.0, 'BRD': 13.7355291, 'CENNZ': 50.0, 'CMT': 122.73254237, 'CTXC': 12.93088277, 'CVC': 70.0, 'CVT': 40.0, 'DRGN': 68.52871512, 'FSN': 1.0, 'FUN': 1000.0, 'FXT': 1958.87870481, 'GNO': 0.06, 'GNT': 25.26006977, 'HOT': 2000.0, 'IOST': 5.0, 'KNC': 4.0, 'LINK': 0.5, 'LRC': 20.0, 'MANA': 24.01449913, 'MCO': 0.3, 'MKR': 0.008, 'NAS': 2.0, 'NEC': 7.0, 'NEXO': 20.0, 'PAY': 21.38080805, 'QKC': 1.0, 'SNT': 200.0, 'SOC': 311.67374462, 'STORJ': 13.0, 'AISA': 100.0, 'DCC': 1000.0, 'EOSRAM': 100.0, 'HVT': 0.0, 'EBTC': 0.0, 'EETH': 0.0, 'IHT': 937.03953101, 'VNS': 1000.0, 'DICE': 0.0, 'EKT': 1000.0, 'SPC': 1235.37086057, 'CHAT': 612.88362251, 'HPY': 2.0, 'MAX': 0.0, 'OCT': 0.0, 'RIDL': 0.0, 'BLACK': 0.0, 'ECTT': 0.0, 'TOOK': 0.0, 'SEED': 0.0, 'PGL': 0.0, 'TOS': 817.10132117, 'UGAS': 10.0, 'MXC': 591.90921228, 'ZIP': 8720.90229578, 'PAI': 90.0, 'HX': 0.1, 'PAX': 4.0, 'PIN': 1000.0, 'BOS': 0.1, 'TRX': 1.0, 'BTT': 150.0, 'RVN': 1.0, 'WICC': 100.0, 'UB': 0.0, 'XIN': 0.02, 'ATOM': 0.005, 'OKB': 0.6, 'GT': 5.0, 'DLX': 0.0, 'LEO': 5.0, 'BKBT': 7067.75286918, 'ENTC': 1000.0, 'ONT': 1.0, 'ARN': 0.0, 'ATD': 100.0, 'BEAN': 10.0, 'BETX': 0.0, 'BOID': 10.0, 'BRM': 0.0, 'BUFF': 0.0, 'CET': 0.0, 'CHL': 0.0, 'DRAGON': 0.0, 'EAP': 0.0, 'ECASH': 0.0, 'EMT': 0.0, 'ENB': 0.0, 'EOSABC': 0.0, 'FAST': 0.0, 'GCHIP': 0.0, 'GGS': 0.0, 'HASH': 0.0, 'HIG': 10.0, 'HORUS': 0.0, 'INF': 0.0, 'IQ': 100.0, 'JKR': 0.0, 'JOY': 0.0, 'KING': 0.0, 'LLG': 0.0, 'LUCK': 0.0, 'LYNX': 0.0, 'MEV': 0.0, 'MGT': 0.0, 'MUR': 0.0, 'NEWS': 1400.0, 'OGM': 0.0, 'OKT': 0.0, 'ONE': 0.0, 'POKER': 0.0, 'POOR': 0.0, 'PTI': 0.0, 'SENSE': 0.0, 'SKY': 0.0, 'SLAM': 10.0, 'TKC': 10.0, 'TOB': 0.0, 'TRYBE': 0.0, 'TXT': 10.0, 'UCTT': 0.0, 'VIP': 0.0, 'VOID': 0.0, 'XPC': 0.0, 'ZKS': 0.0, 'CUSE': 1000.0, 'SCEC': 1000.0, 'USE': 1000.0, 'UNC': 1000.0, 'FREC': 29355.5198973, 'FCC': 1000.0, 'EVS': 8.42585785, 'SGN': 5508.13729426, 'PIZZA': 0.0, 'KEY': 0.0, 'ARP': 1000.0, 'ALGO': 0.2, 'DNAT': 20.0, 'YEC': 0.5, 'AXE': 1.0, 'RRB': 50.0, 'GLO': 18000.0, 'CKB': 20.0, 'GDP': 1000.0, 'DILIO': 800.0, 'TC': 8700.0, 'NST':100.0, 'WICM': 0.1, 'KOC': 7.0, 'MX': 15.0, '5TH': 20.0, 'TZS': 1000.0, 'MOF': 2.5, 'SKR': 3000.0, 'ZVC': 10.5, 'GLOS': 300.0, 'TZVC': 25.0, 'STX': 50.0, 'CLC': 10.0, 'FCT': 50.0, 'PGS': 8000.0, 'FBT': 20000.0, 'KAVA': 0.2, 'RNDR': 12.0, 'HZT': 20.0, 'PROPS': 15.0, 'EIDOS': 400.0, 'KSM': 0.1, 'AIX': 10000.0, 'OGN': 20.0, 'RUTM': 0.0001, 'SIN': 5.0, 'TRB': 0.1, 'BWT': 0.0, 'OXT': 15.0, 'PYP': 0.0, 'BPT': 20.0, 'FO': 50.0, 'TFO': 100.0, 'MDU': 1.0, 'UA': 1.0, 'UCT': 0.1, 'HDAO': 50.0, 'YAS': 5.0, 'FCH': 5.0, 'TKM': 0.1, 'SVVC': 500.0, 'EXN': 5.0, 'SBC': 100.0, 'HNEO': 0.1, 'HQTUM': 10.0, 'TROY': 2000.0, 'ETF': 0.0, 'BKCM': 500.0, 'JMC': 100.0, 'KLAY': 0.5, 'TRT': 1000.0, 'SOL': 0.2, 'MASS': 1.0, 'COMP': 0.03, 'GXC': 0.5, 'HNT': 0.05, 'TWT': 10.0, 'UMA': 0.4, 'JST': 25.0, 'CELO': 0.1, 'DSG': 20.0, 'ZDN': 10.0, 'KEEP': 5.0, '2KEY': 20.0, 'MSC': 20.0, 'ANJ': 25.0, 'XIO': 10.0, 'RING': 70.0, 'ESH': 10.0, 'GTG': 1.5, 'NEST': 100.0, 'JRT': 1.0, 'RVC': 20.0, 'CDS': 2.0, 'SNX': 1.0, 'CLX': 20.0, 'ONG':1.0, 'ROR': 10.0, 'IDK': 10.0, 'TCAD': 10.0, 'TAUD': 10.0, 'RSV': 10.0, 'AR': 1.0, 'KAI': 300.0, 'LYXE': 4.0, 'OKS': 5.0, 'BHD': 0.05, 'DASV': 100.0, 'FOR': 100.0, 'DAPP': 1.0, 'REN': 20.0, 'FIL': 0.05, 'IDEX': 64.0, 'WGRT': 10.0, 'MLN': 0.15, 'CNYT':0.0, 'CDT': 166.0, 'SCS': 16.0, 'CRING': 650.0, 'STAKE': 0.2, 'DMG': 12.0, 'CEL': 1.0, 'NMR': 0.1, 'CHZ': 150.0, 'BAL': 0.3, 'JT': 30.0, 'RSR': 400.0, 'REL': 1.0, 'PNK': 64.0, 'SWTH': 15.0, 'DEXT': 90.0, 'ALEPH': 30.0, 'CAN': 10.0, 'GBT': 10.0, 'LPT':0.2, 'AUC': 5.0, 'DSF': 100.0, 'AKRO': 400.0, 'XOR': 0.025, 'AMPL': 4.0, 'STA': 10.0, 'COT': 10000.0, 'ASKO': 600.0, 'UTO': 1.2, 'MCX': 120.0, 'DAM': 5.0, 'ATTN': 30.0, 'AVA': 1.0, 'FLUX': 0.28, 'VRA': 5555.0, 'AST': 28.0, 'UCA': 10.0, 'IDRT': 15000.0, 'BIDR': 600.0, 'BKRW': 100.0, 'BZRX': 22.0, 'PLR': 70.0, 'NDX': 2565.0, 'DEC': 50.0, 'ORN': 2.0, 'MCB': 0.35, 'MTA': 2.0, 'UTK': 40.0, 'OWL': 0.01, 'WNXM': 0.28, 'RARI': 1.0, 'DFS': 0.2, 'USDD': 10.0, 'PLT': 60.0, 'MW': 2.5, 'YFI': 0.0002, 'QXGS': 1.0, 'CTAFY': 1.0, 'DXD': 0.02, 'SWINGBY': 6.0, 'MTR': 1.0, 'MTRG': 1.0, 'RPL': 3.0, 'FIO': 5.0, 'KTON': 0.03, 'DMST': 66.0, 'DEV': 0.6, 'GEN': 12.0, 'DOT': 0.1, 'DAD': 7.0, 'YFII': 0.001, 'IFT': 2000.0, 'TIFT': 10.0, 'BUIDL': 1.0, 'PUX': 285.0, 'DIA': 0.8, 'BOT': 0.01, 'FNX': 6.0, 'XFT': 2.0, 'STRONG': 0.02, 'YAM': 0.4, 'ETHV': 4.0, 'CRV': 4.0, 'TLOS': 1.0, 'BART': 100.0, 'XRT': 0.25, 'OM': 6.0, 'OGX': 2.0, 'HU': 0.01, 'CREDIT': 60.0, 'HAKKA': 6.0, 'DIP': 3.0, 'LIEN': 0.1, 'BOX': 0.25, 'DF': 26.0, 'CVP': 2.0, 'SUSHI': 3.0, 'PEARL': 0.0003, 'TAI': 0.06, 'OIN': 10.0, 'ADEL': 8.0, 'CRT': 1.0, 'SAL': 0.07, 'SWRV': 3.0, 'CREAM':0.04, 'FARM': 0.005, 'FSW': 20.0, 'ULU': 0.0125, 'DMD': 0.0025, 'ZILD': 0.04, 'UP': 5.0, 'SUN': 0.05, 'PERP': 4.0, 'GOF': 3.0, 'GTF': 5.0, 'WING': 0.01, 'ONES': 5.0, 'PICKLE': 0.2, 'HGET': 0.8, 'GHST': 20.0, 'SAFE': 0.02, 'MEME': 0.03, 'SLM': 0.01, 'HEGIC': 20.0, 'UNI': 1.0, 'FRONT': 10.0, 'LINA': 200.0, 'DHT': 5.0, 'DEGO': 20.0, 'BAND': 1000.01, 'OBEE': 2000.0, 'WHALE': 0.5, 'CRU': 1.0, 'AVAX': 0.01, 'UNII': 250.0, 'COVAL': 800.0, 'BONK': 10.0, 'ASTRO': 6.0, 'ZOM': 0.1, 'SHROOM': 20.0, 'HOO': 70.0, 'SLP': 100.0, 'ARTE': 1.0, 'SKL': 120.0, 'LAYER': 20.0, 'NFT': 30.0, 'BID': 150.0, 'RFUEL': 30.0, 'DANDY': 0.015, 'BUILD': 0.15, 'FIN': 1.0, 'YELD': 0.05, 'PGT': 0.03, 'GTH': 80.0, 'AAVE': 0.1, 'DAOFI': 40.0, 'PLOT': 20.0, 'UFT': 8.0, 'NU': 30.0, 'HEZ': 1.0, 'RAMP': 100.0, 'REVV': 160.0, 'CFS': 25.0, 'BIW': 25.0, 'RGT': 4.0, 'RAK': 0.05, 'BOND': 0.02, 'WOO': 45.0, 'KP3R': 0.02, 'BVB': 40.0, 'YF': 0.01, 'DOUGH': 5.0, 'NSURE': 10.0, 'PTERIA': 0.7, 'ROOK': 0.03, 'LTX': 10.0, 'SPKL': 5000.0, 'BCHA': 0.001, 'CFX': 1.0, 'FC': 0.1, 'DVI': 100.0, 'PRQ': 10.0, 'AC': 10.0, 'SFI': 0.0001, 'SYN': 8.0, 'INDEX': 0.5, 'FIS': 0.3, 'EXRD': 25.0, 'FYZ': 10.0, 'ANT': 1.0, 'ATRI': 100.0, 'ORAI': 0.2, 'EPAN': 20.0, 'TRU': 25.0, 'KOMET': 0.05, 'ARCH': 12.0, 'MARK': 1.5, 'AIN': 160.0, 'YFC': 0.05, 'WDP': 0.1, 'KEX': 1.0, 'FWT': 1000.0, 'CFI': 1.0, 'BUND': 1.0, 'MTS': 1.5, 'WON': 500.0, 'YFD': 0.01, 'TME': 0.01, 'GDAO': 2.0, 'CLIQ': 50.0, 'OPEN': 80.0, 'WFIL': 0.1, 'UMEX': 20.0, 'ZIN': 500.0, 'API3': 2.0, 'ZORA': 0.01, 'SWISS': 0.01, 'CRBN': 100.0, 'BIRD': 1.0, 'STV': 500.0, 'DG': 0.2, 'LOAD': 100.0, 'BETC': 0.5, 'EOC': 1.0, 'STPL': 250.0, 'BUP': 15.0, 'PSK': 50.0, 'MIXS': 25.0, 'BADGER': 0.5, 'BSC': 0.015, 'MONA': 0.005, 'ITS': 0.3, 'UCAP': 3.0, 'XCUR': 150.0, 'PPAY': 50.0, 'YFIA': 3.0, 'YLD': 0.15, 'MVEDA': 80.0, 'SKD': 0.01, 'FAR': 10.0, 'SPDR': 80.0, 'DEFO': 0.02, 'DFO': 40.0, 'GRT': 8.0, 'ANRX': 60.0, 'MAHA': 0.5, 'FXS': 0.15, 'POND': 30.0, 'LON': 3.0, 'TWT1': 1.0, 'FRM': 35.0, 'UDT': 0.7, 'DDX': 1.0, '1INCH': 5.0, 'DRIP': 50.0, 'CBK': 20.0, 'DATX': 10000.0, 'REEF': 35.0, 'WHITE': 0.002, 'ORI': 0.05, 'FIRE': 8.0, 'HYPE': 5.0, 'MIS': 0.008, 'KEK': 500.0, 'BAFI': 2.0, '3XT': 0.003}
        path = "/open/v1/tickers"
        obj = gen_sign(client_id, client_key)
        res = requests.get(host + path, params=obj)
        temp = json.loads(res.content)['data']
        for i in temp:
            if i['symbol'].split('-')[0] in get_hoo_fee.keys():
                pairs.append(i['symbol'].replace('-','/'))        
        print('Get HOO     pairs sucessfully!')
    except:
        pairs=[]
        print('Can HOO     Get GATE pairs！') 
    return pairs
def get_bitmax_pairs():
    url = 'https://bitmax.io/api/pro/v1/products'
    url2 = 'https://bitmax.io/api/pro/v1/assets'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(data1['data'])
        data2 = [i['symbol'] for i in data1['data'] if 'USDT' in i['symbol']]
        print('Get BITMAX  pairs sucessfully!')
        data3 = requests.get(url2, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()

        status = data3['data']
        #print(status[0].values()[0].values())
        data=[]
        for i in data2:
            #print(i.split('/')[0])
            for j in status:
                
                if i.split('/')[0] == j['assetCode'] and j['status'] == 'Normal':
                    data.append(i)
                    break
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print("Can not Get BITMAX pairs!")
    return data
def get_binance_pairs():
    url='https://api.binance.com/api/v3/ticker/price'
    data=[]
    try:
        data=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(data)
        for i in data:
            str_list = list(i['symbol'])
            nPos = i['symbol'].find('USDT')
            if nPos >=3:
                str_list.insert(nPos,'/')
                str_2="".join(str_list)
                i['symbol']=str_2
        binance_pairs = [i['symbol'] for i in data]
        print("Get BINANCE pairs sucessfully!")        
    except:
        binance_pairs=[]
        print("Can not Get BINANCE pairs!")
            
    return binance_pairs   #'bidPrice': 'bidQty' 'askPrice':  'askQty':
def get_pol_pairs():
    url = "https://poloniex.com/public?command=returnTicker"
    url2 = "https://poloniex.com/public?command=returnCurrencies"
    temp=[]
    data=[]
    try:
        data1=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data3=data1.keys()
        for i in data3:
            a=i.split('_')[0]
            b=i.split('_')[1]
            c=b+'/'+a        
            temp.append(c)
        
        data2=requests.get(url2,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(status[0].values()[0].values())
        #print(data2)
        for i in temp:        
            if data2[i.split('/')[0]]['disabled'] == 0:
                data.append(i)
        print('Get PWANG   pairs sucessfully!') 
    except:
        data = []
        print("Can not Get PWANG pairs!")
    return data
def get_huobi_pairs():
    url = 'https://api.huobi.pro/v1/common/symbols'
    url2 = 'https://api.huobi.pro/v2/reference/currencies'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        ss = data1['data']
        data2 = [(i['base-currency']+'/'+i['quote-currency']).upper() for i in ss if i['quote-currency']=='usdt']
        print('Get HUOBI   pairs sucessfully!')
        data3 = requests.get(url2, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()

        status = data3['data']
        #print(status[0].values()[0].values())

        data=[]
        for i in data2:
            #print(i.split('/')[0])
            for j in status:
                #print(j)       
                try:
                    if i.split('/')[0] == j['chains'][0]['displayName'] and j['chains'][0]['withdrawStatus'] == 'allowed' and j['chains'][0]['depositStatus'] == 'allowed':
                        data.append(i)
                        break
                except:
                    pass
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print("Can not Get HUOBI pairs!")
    return data

def sendmail(content,title):
    s=''
    msg_from='cpebj-wh@163.com' #发送方邮箱
    passwd='KSMFJMEYWJDBHXTA'   #settbbjsoxlxbihf'   #填入发送方邮箱的授权码
    msg_to='haiwwhai@qq.com'    #收件人邮箱
                                
    subject=title     #主题     
    #content="12323"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.163.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        #print("Send Sucessfully!") 
    except:
        pass
        # print("发送失败") 
    finally:
        s.quit()


def get_bitmax_fee(symbol):
    a=symbol.split('/')[0]
    url = 'https://bitmax.io/api/pro/v1/assets'
    data=0
    try:
        asset = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('获取',symbol1,'币深度正常')
        data1=asset['data']
        for i in data1:
            if i['assetCode']==a:
                data=float(i['withdrawalFee'])
                break
    except:
        data=0
        print('Bitmax '+symbol+' fee not response!')
    return data

def get_huobi_fee(symbol):
    a=symbol.split('/')[0].lower()
    url = 'https://api.huobi.pro/v2/reference/currencies?currency='+a
    data=0
    try:
        depth = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data=float(depth['data'][0]['chains'][0]['transactFeeWithdraw'])
    except:
        data=0
        #time.sleep(random.uniform(1, 3))
        print('Huobi '+symbol+' fee not response!')
    return data

def get_pol_fee(symbol):
    a=symbol.split('/')[0]
    #print(a)
    url="https://poloniex.com/public?command=returnCurrencies"  #depth 10  
    data=0
    try:
        data1=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(data1)
        data = float(data1[a]['txFee'])
    except:
        data=0
        print('Polo '+symbol+' fee not response!')
    return data
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

def get_gate_fee_NOT_USE():
    url= 'data.gateapi.io'
    URL = "/api2/1/private/feelist"
    apiKey = 'XXXX'
    secretKey = 'XXXX'
    params = {}
    fee={}
    try:
        fee = httpPost(url, URL, params, apiKey, secretKey)
        print('Get Gate fee sucessfully!')
    except:
        fee={}    
    return eval(fee)

def get_hoo_wallet(symbol):
    a=0
    b=0
    d=0
    c =0
    try:
        url = 'https://cn.etherscan.com/tokenholdingsHandler.aspx?&a=0x0093e5f2a850268c0ca3093c7ea53731296487eb&q='+symbol+'&p=1&f=0&h=0&sort=total_price_usd&order=desc&pUsd24hrs=1785.6&pBtc24hrs=0.0316&pUsd=1785.63&fav=&langMsg=%E5%85%B1%E6%89%BE%E5%88%B0%E4%BA%86XX%E4%B8%AA%E4%BB%A3%E5%B8%81&langFilter=%E6%8C%89XX%E7%AD%9B%E9%80%89&langFirst=%E6%9C%80%E5%89%8D&langPage=%E7%AC%ACX%E9%A1%B5%EF%BC%8C%E5%85%B1Y%E9%A1%B5&langLast=%E6%9C%80%E5%90%8E&ps=25'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        req = urllib.request.Request(url,headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
        jsonData = json.loads(html)
        Data = jsonData['layout']
        #print(Data)
        start = Data.find(">"+symbol+"<")
        end = Data.find('$',start)
        #print(start,end)
        #print(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        c= float(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        '''
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        #print(data1)
        soup = BeautifulSoup(data1.content,'lxml')
        #print(soup)   
        s=soup.find_all('tr')
        for i in s:
            #print(i)
            w = i.find_all('td')
            for tt in w:
                if tt.text == symbol:
                    c=float(w[3].text.replace(',',''))  
                    break
            if c>0:
                break
        '''     
    except:
        pass
    return c

def get_bitmax_wallet(symbol):
    a=0
    b=0
    d=0
    c =0
    try:
        url = 'https://cn.etherscan.com/tokenholdingsHandler.aspx?&a=0x986a2fCa9eDa0e06fBf7839B89BfC006eE2a23Dd&q='+symbol+'&p=1&f=0&h=0&sort=total_price_usd&order=desc&pUsd24hrs=1785.6&pBtc24hrs=0.0316&pUsd=1785.63&fav=&langMsg=%E5%85%B1%E6%89%BE%E5%88%B0%E4%BA%86XX%E4%B8%AA%E4%BB%A3%E5%B8%81&langFilter=%E6%8C%89XX%E7%AD%9B%E9%80%89&langFirst=%E6%9C%80%E5%89%8D&langPage=%E7%AC%ACX%E9%A1%B5%EF%BC%8C%E5%85%B1Y%E9%A1%B5&langLast=%E6%9C%80%E5%90%8E&ps=25'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        req = urllib.request.Request(url,headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
        jsonData = json.loads(html)
        Data = jsonData['layout']
        #print(Data)
        start = Data.find(">"+symbol+"<")
        end = Data.find('$',start)
        #print(start,end)
        #print(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        c= float(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        '''
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        #print(data1)
        soup = BeautifulSoup(data1.content,'lxml')
        #print(soup)   
        s=soup.find_all('tr')
        for i in s:
            #print(i)
            w = i.find_all('td')
            for tt in w:
                if tt.text == symbol:
                    c=float(w[3].text.replace(',',''))  
                    break
            if c>0:
                break
        '''    
    except:
        pass
    return c

def get_gate_wallet(symbol):
    a=0
    b=0
    d=0
    c =0
    try:
        url = 'https://cn.etherscan.com/tokenholdingsHandler.aspx?&a=0x0D0707963952f2fBA59dD06f2b425ace40b492Fe&q='+symbol+'&p=1&f=0&h=0&sort=total_price_usd&order=desc&pUsd24hrs=1785.6&pBtc24hrs=0.0316&pUsd=1785.63&fav=&langMsg=%E5%85%B1%E6%89%BE%E5%88%B0%E4%BA%86XX%E4%B8%AA%E4%BB%A3%E5%B8%81&langFilter=%E6%8C%89XX%E7%AD%9B%E9%80%89&langFirst=%E6%9C%80%E5%89%8D&langPage=%E7%AC%ACX%E9%A1%B5%EF%BC%8C%E5%85%B1Y%E9%A1%B5&langLast=%E6%9C%80%E5%90%8E&ps=25'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        req = urllib.request.Request(url,headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
        jsonData = json.loads(html)
        Data = jsonData['layout']
        #print(Data)
        start = Data.find(">"+symbol+"<")
        end = Data.find('$',start)
        #print(start,end)
        #print(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        c= float(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        '''
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        #print(data1)
        soup = BeautifulSoup(data1.content,'lxml')
        #print(soup)   
        s=soup.find_all('tr')
        for i in s:
            #print(i)
            w = i.find_all('td')
            for tt in w:
                if tt.text == symbol:
                    c=float(w[3].text.replace(',',''))  
                    break
            if c>0:
                break
        '''
    except:
        pass 
    return c

def get_poloniex_wallet(symbol):
    a=0
    b=0
    d=0
    c =0
    try:
        url = 'https://cn.etherscan.com/tokenholdingsHandler.aspx?&a=0xA910f92ACdAf488fa6eF02174fb86208Ad7722ba&q='+symbol+'&p=1&f=0&h=0&sort=total_price_usd&order=desc&pUsd24hrs=1785.6&pBtc24hrs=0.0316&pUsd=1785.63&fav=&langMsg=%E5%85%B1%E6%89%BE%E5%88%B0%E4%BA%86XX%E4%B8%AA%E4%BB%A3%E5%B8%81&langFilter=%E6%8C%89XX%E7%AD%9B%E9%80%89&langFirst=%E6%9C%80%E5%89%8D&langPage=%E7%AC%ACX%E9%A1%B5%EF%BC%8C%E5%85%B1Y%E9%A1%B5&langLast=%E6%9C%80%E5%90%8E&ps=25'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        req = urllib.request.Request(url,headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
        jsonData = json.loads(html)
        Data = jsonData['layout']
        #print(Data)
        start = Data.find(">"+symbol+"<")
        end = Data.find('$',start)
        #print(start,end)
        #print(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        c= float(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        '''
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        #print(data1)
        soup = BeautifulSoup(data1.content,'lxml')
        #print(soup)   
        s=soup.find_all('tr')
        for i in s:
            #print(i)
            w = i.find_all('td')
            for tt in w:
                if tt.text == symbol:
                    c=float(w[3].text.replace(',',''))  
                    break
            if c>0:
                break
        '''    
    except:
        pass       
    return c

def get_huobi_wallet(symbol):
    a=0
    b=0
    d=0
    c =0
    try:
        url = 'https://cn.etherscan.com/tokenholdingsHandler.aspx?&a=0xE93381fB4c4F14bDa253907b18faD305D799241a&q='+symbol+'&p=1&f=0&h=0&sort=total_price_usd&order=desc&pUsd24hrs=1785.6&pBtc24hrs=0.0316&pUsd=1785.63&fav=&langMsg=%E5%85%B1%E6%89%BE%E5%88%B0%E4%BA%86XX%E4%B8%AA%E4%BB%A3%E5%B8%81&langFilter=%E6%8C%89XX%E7%AD%9B%E9%80%89&langFirst=%E6%9C%80%E5%89%8D&langPage=%E7%AC%ACX%E9%A1%B5%EF%BC%8C%E5%85%B1Y%E9%A1%B5&langLast=%E6%9C%80%E5%90%8E&ps=25'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        req = urllib.request.Request(url,headers = headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        #print(html)
        jsonData = json.loads(html)
        Data = jsonData['layout']
        #print(Data)
        start = Data.find(">"+symbol+"<")
        end = Data.find('$',start)
        #print(start,end)
        #print(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        c= float(Data[int(start)+10+len(symbol):int(end)-9].replace(',',''))
        '''
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        #print(data1)
        soup = BeautifulSoup(data1.content,'lxml')
        #print(soup)   
        s=soup.find_all('tr')
        for i in s:
            #print(i)
            w = i.find_all('td')
            for tt in w:
                if tt.text == symbol:
                    c=float(w[3].text.replace(',',''))  
                    break
            if c>0:
                break
        '''    
    except:
        pass        
    return c   
'''
def read_excel_data():   #read excel to dict
    filename = r'D:\test1.xls'
    data = xlrd.open_workbook(filename)
    table = data.sheet_by_name('Sheet1')
    row_num = table.nrows  # 行数
    # col_num = table.ncols  # 列数
    datas = dict([]) # 这步也要转字典类型
    for i in range(row_num):
        xx = dict([table.row_values(i)]) # 这一步就要给它转字典类型，不然update没法使用
        datas.update(xx)
    print(datas)
    # print("字典中保存的学历：", datas[key])
'''

#==================main================================================================
if __name__ == "__main__":
    exchangeNames=['Binance','Bitmax','Huobi','Pwang','GateIO','Hoo'] 
    pairs_all = []
    data_all = []
    f=0
    deposit=0
    pairs_new =[[] for i in exchangeNames]
    delete_coins=[['ETC','RIF','DOCK'],['BOND'],['HOT','3L','3S','ETC','RAI'],['STR','MPH','ETC','COVER','OM','BCHSV','BCN','BTCST'],['RAMP','COVER','CET','ETC','BCHA','KLAY','BOND'],['COVER','AGS','ATP','CET','ETC','OM','BAS','KLAY','KEY','TRB','MIS']]
    get_gate_fee = {'GT': 4, 'CNYX': 10, 'USDT': 5, 'USDT_ETH': 5, 'BTC': 0.0005, 'BCH': 0.0005, 'BSV': 0.0005, 'ETH': 0.01, 'ETC': 0.01, 'EOS':0.1, 'XRP': 0.1, 'LTC': 0.001, 'ZEC': 0.001, 'DASH': 0.002, 'QTUM': 0.01, 'QTUM_ETH': 0.1, 'DOGE': 20, 'OCN': 17000, 'BTM': 5, 'TRX': 5, 'ONT': 1, 'BTG': 0.002, 'BAT': 25, 'SNT': 130, 'BTM_ETH': 10, 'CVC': 29, 'REQ': 180, 'RDN': 36, 'KNC': 6.7, 'LINK': 0.43, 'CDT': 640, 'AE': 1, 'INK': 10, 'POWR': 71, 'WTC': 0.2, 'VET': 100, 'RCN': 160, 'PPT': 0.1, 'BNT': 4.1, 'VERI': 0.005,'MCO': 25, 'MDA': 13, 'FUN': 370, 'DATA': 120, 'RLC': 7.1, 'ZSC': 29000, 'WINGS': 410, 'GVT': 0.2, 'KICK': 5, 'CTR': 1, 'HSR': 0.05, 'HC': 0.2, 'QBT': 5, 'QSP': 210, 'BCD': 0.02, 'MED': 100, 'QASH': 230, 'DGD': 0.1, 'GNT': 10, 'MDS': 2200, 'SBTC': 0.05, 'MANA': 50, 'GOD': 0.1, 'BCX': 30, 'SMT': 50, 'BTF': 0.1, 'IOTA': 0.1, 'NAS': 0.5, 'NAS_ETH': 0.5, 'TSL': 10, 'ADA': 1, 'LSK': 0.1, 'BIFI': 0.2, 'XTZ': 0.1, 'BNTY': 5200, 'ICX': 0.2, 'LEND': 20, 'LUN': 6.1, 'ELF': 60, 'SALT': 45, 'FUEL': 23000, 'DRGN': 91, 'GTC': 1400, 'MDT': 280, 'QUN': 2, 'GNX': 600, 'DDD': 2700, 'OST': 690, 'BTO': 10, 'TIO': 10, 'THETA': 10, 'SNET': 3400, 'ZIL': 10, 'RUFF': 1000, 'TNC': 10, 'COFI': 6500, 'ZPT': 10, 'JNT': 360, 'GXS': 1, 'MTN': 4100, 'BLZ': 69, 'GEM': 44000, 'DADI': 2, 'ABT': 81, 'LEDU': 470, 'RFR': 2400, 'XLM': 0.01, 'MOBI': 1, 'NEO': 0, 'GAS': 0.02, 'DBC': 10, 'QLC': 10, 'MKR': 0.0058, 'DAI': 15, 'LRC': 19, 'OAX': 57, 'ZRX': 10, 'PST': 530, 'TNT': 3400, 'LLT': 10, 'DNT': 47, 'DPY': 1400, 'BCDN': 8300, 'STORJ': 20, 'OMG': 2, 'PAY': 77, 'EON': 20, 'IQ': 20, 'EOSDAC': 20, 'TIPS': 100, 'CNC': 0.1, 'TIX': 0.1, 'XMR': 0.001, 'BTS': 1, 'XTC': '10', 'USDG': 15, 'POINT': 1, 'ATOM': 0.01, 'ETH2': 0.005, 'HARD': 0.01, 'KAVA': 0.01, 'IRIS': 5, 'ANT': 2.2, 'ANKR': 610, 'STPT': 420, 'RSR': 220, 'RSV': 15, 'KAI': 0.01, 'CTSI': 62, 'COMP': 0.029, 'OCEAN': 14, 'SC': 230, 'KSM': 0.05, 'FIRO': 0.5, 'DOT': 0.1, 'MTR': 1, 'MTRG': 2, 'SOL': 0.01, 'COTI': 120, 'AMPL': 13, 'DIGG': 0.0003, 'GRAP': 94, 'YAMV1': 500, 'WNXM': 0.23, 'LUNA': 5, 'AVAX': 0.1, 'BZRX': 20, 'PCX': 0.2, 'YAMV2': 1.2, 'YAM': 2.8, 'BOX': 0.1, 'CRV': 4.5, 'UNI': 2, 'SUSHI': 1, 'AAVE': 0.03, 'POLS': 4, 'ERG': 2, 'GOF': 6.2, 'PHA': 39, 'SASHIMI': 140, 'FARM': 0.039, 'SWRV': 6.6, 'RAZOR': 26, 'AUCTION': 0.7, 'ULU': 1, 'OIN': 26, 'AGS': 95, 'ADEL': 51, 'TON': 950, 'KIMCHI': 330, 'KTON': 0.11, 'RING': 140, 'MINI': 240, 'CREAM': 0.068, 'JGN': 79, 'DEGO': 5.8, 'RFUEL': 130, 'SFG': 24, 'NEST': 230, 'CORE': 0.0034, 'NEAR': 3, 'NU': 19, 'STAKE': 0.55, 'ARNX':870, 'TRU': 28, 'ROSE': 10, 'BADGER': 0.5, 'COVER': 0.012, 'GLM': 64, 'BASE': 8.5, 'PICKLE': 0.56, 'HEGIC': 27, 'GTH': 55, 'DUSK': 83, '88MPH': 0.08, 'UNFI': 0.56, 'FLM': 10, 'GHST': 13, 'LOON': 180, 'ACH': 1400, 'DUCK': 64, 'GRT': 20, 'ESD': 72, 'ALEPH': 34, 'FRAX': 15, 'FXS': 1.8, 'BOR': 0.024, 'ROOK': 0.03, 'BAC': 31, 'BAS': 0.17, 'LON': 2.1, 'MAHA': 1.2, 'WOZX': 12, 'FAR': 64, 'POND': 95, '1INCH': 2.5, 'DSD': 85, 'OCTO': 0.14, 'SHARE': 43, 'LINA': 200, 'ONC': 22, 'ONS': 0.62, 'ZKS': 25, 'FROG':1, 'MIS': 0.61, 'WHITE': 0.0031, 'ONX': 2.3, 'MATIC': 140, 'RIF': 8, 'CRU': 1.3, 'PROPS': 210, 'BIFIF': 270, 'LAYER': 23, 'YFDAI': 0.0028, 'QNT': 0.36, 'ARMOR': 13, 'YOP': 5.2, 'BFC': 320, 'BONDED': 700, 'STMX': 1400, 'ROOM': 40, 'GDAO': 8.6, 'PAID': 3.9, 'UNISTAKE': 63, 'BOND': 0.21, 'FXF': 40, 'CRBN': 87, 'TORN': 0.037, 'STRONG': 0.19, 'UMB': 40, 'NUX': 3, 'JASMY': 2, 'WOM': 66, 'NFTX': 0.03, 'PERP': 2.1, 'ORAI': 0.23, 'CWS': 0.47, 'LIT': 1.4, 'UNCX': 0.1, 'POOLZ': 0.49, 'SNOW': 0.14, 'DODO': 5.8, 'OPIUM': 0.79, 'KIF': 0.047, 'REEF': 310, 'BIRD': 0.11, 'MAPS': 25, 'MIR': 3, 'SFIL': 1.3, 'ZCN': 19, 'MARS': 71, 'BAO': 8700, 'LPT': 3, 'DIS': 0.12, 'DEXE': 1.7, 'PBTC35A': 0.14, 'ORN': 2.4, 'NORD': 1.3, 'DAO': 5.5, 'FLOW': 0.1, 'ALPHA': 8.5, 'ENJ':26, 'API3': 2.2, 'FIN': 40, 'SKL': 46, 'PRQ': 13, 'FRONT': 12, 'INJ': 1.3, 'ALPA': 130, 'ROOBEE': 3600, 'NSURE': 13, 'KP3R': 0.035, 'WOO': 240, 'HYVE': 270, 'KFC': 2, 'RAMP': 300, 'SYLO': 13000, 'RARI': 0.64, 'DVP': 160, 'MPH': 370, 'DF': 50, 'CVP': 3.8, 'YFV': 0.1, 'VALUE': 1.8, 'UMA': 0.49, 'YFII': 0.0047, 'SWAP': 14, 'SXP': 5.8, 'BAL': 0.31, 'BAND': 0.82, 'AST': 48, 'TROY': 1400, 'OM': 60, 'SPA': 730, 'AKRO': 290, 'FOR': 280, 'CREDIT': 350, 'DIA': 5.1, 'AXIS': 19, 'TRB': 0.27, 'LIEN': 0.23, 'PEARL': 0.001, 'CORN': 0.0071, 'SLM': 0.034, 'SAL': 0.016, 'TAI': 0.1, 'CRT': 0.73, 'JFI': 0.0011, 'MTA': 3.6, 'YFI': 0.00032, 'KIN': 10000, 'DKA': 480, 'REN': 15, 'DOS': 110, 'SUTER': 2100, 'SRM': 3.8, 'JST': 5, 'LBK': 1300, 'BTMX': 54, 'WAVES': 0.1, 'NSBT': 0.3, 'WEST': 1, 'XEM': 5, 'BU': 0.1, 'HNS': 1, 'BTC3L': 1, 'BTC3S': 1, 'BTC5L': 1, 'BTC5S': 1, 'BCH5L': 1, 'BCH5S': 1, 'DOT5L': 1, 'DOT5S': 1, 'XRP5L': 1, 'XRP5S': 1, 'BSV5L': 1, 'BSV5S': 1, 'LTC5L': 1, 'LTC5S': 1, 'EOS5L': 1, 'EOS5S': 1, 'ETH5L':1, 'ETH5S': 1, 'LINK3L': 1, 'LINK3S': 1, 'KAVA3L': 1, 'KAVA3S': 1, 'EGLD3L': 1, 'EGLD3S': 1, 'CHZ3L': 1, 'CHZ3S': 1, 'MKR3L':1, 'MKR3S': 1, 'LRC3L': 1, 'LRC3S': 1, 'BAL3L': 1, 'BAL3S': 1, 'JST3L': 1, 'JST3S': 1, 'SERO3L': 1, 'SERO3S': 1, 'VET3L': 1, 'VET3S': 1, 'THETA3L': 1, 'THETA3S': 1, 'ZIL3L': 1, 'ZIL3S': 1, 'GRIN3L': 1, 'GRIN3S': 1, 'BEAM3L': 1, 'BEAM3S': 1, 'SOL3L': 1, 'SOL3S': 1, 'SKL3L': 1, 'SKL3S': 1, '1INCH3L': 1, '1INCH3S': 1, 'LON3L': 1, 'LON3S': 1, 'DOGE3L': 1, 'DOGE3S': 1, 'GRT3L': 1, 'GRT3S': 1, 'BNB3L': 1, 'BNB3S': 1, 'TRX3L': 1, 'TRX3S': 1, 'ATOM3L': 1, 'ATOM3S': 1, 'AVAX3L': 1, 'AVAX3S': 1, 'NEAR3L': 1,'NEAR3S': 1, 'ROSE3L': 1, 'ROSE3S': 1, 'ZEN3L': 1, 'ZEN3S': 1, 'QTUM3L': 1, 'QTUM3S': 1, 'XLM3L': 1, 'XLM3S': 1, 'XRP3L': 1, 'XRP3S': 1, 'CFX3L': 1, 'CFX3S': 1, 'BCHA3L': 1, 'BCHA3S': 1, 'OMG3L': 1, 'OMG3S': 1, 'ALGO3L': 1, 'ALGO3S': 1, 'WAVES3L': 1, 'WAVES3S': 1, 'NEO3L': 1, 'NEO3S': 1, 'ONT3L': 1, 'ONT3S': 1, 'ETC3L': 1, 'ETC3S': 1, 'CVC3L': 1, 'CVC3S': 1, 'SNX3L': 1, 'SNX3S': 1, 'ADA3L': 1, 'ADA3S': 1, 'DASH3L': 1, 'DASH3S': 1, 'AAVE3L': 1, 'AAVE3S': 1, 'SRM3L': 1, 'SRM3S': 1, 'KSM3L': 1, 'KSM3S': 1, 'BTM3L': 1, 'BTM3S': 1, 'ZEC3L': 1, 'ZEC3S': 1, 'XMR3L': 1, 'XMR3S': 1, 'AMPL3L': 1, 'AMPL3S': 1, 'CRV3L': 1, 'CRV3S': 1, 'COMP3L': 1, 'COMP3S': 1, 'YFII3L': 1, 'YFII3S': 1, 'YFI3L': 1, 'YFI3S': 1, 'HT3L': 1, 'HT3S': 1, 'OKB3L': 1, 'OKB3S': 1, 'UNI3L': 1, 'UNI3S': 1, 'DOT3L': 1, 'DOT3S': 1, 'FIL3L': 1, 'FIL3S': 1, 'SUSHI3L': 1, 'SUSHI3S': 1, 'ETH3L': 1, 'ETH3S': 1, 'EOS3L': 1, 'EOS3S': 1, 'BSV3L': 1, 'BSV3S': 1, 'BCH3L': 1, 'BCH3S': 1, 'LTC3L': 1, 'LTC3S': 1, 'XTZ3L': 1, 'XTZ3S': 1, 'RVN': 5, 'RVC': 5, 'AR': 0.5, 'DCR': 0.02, 'BCN': 10, 'XMC': 0.05, 'PPS': 0.01, 'NBS': 100, 'STEEM': 1, 'HIVE': 1, 'COCOS': 0.1, 'BCHA': 0.01, 'ATP': 0.5, 'NAX': 0.5, 'KLAY': 1, 'NBOT': 410, 'PLY': 10, 'GRIN': 0.1, 'BEAM': 0.1, 'HBAR': 0.1, 'OKB': 1.7, 'REP': 0.46, 'USDTEST': 100000, 'STAR': 0.01, 'ZEN': 0.15, 'ABBC': 10, 'FIL': 0.01, 'FIC': 0.01, 'FIL6': 0.1, 'SUP': 0.01, 'STOX': 1100, 'VTHO': 50, 'VIDYX': 20, 'BTT': 83, 'ARN': 2, 'SMT_ETH': 50, 'TFUEL': 10, 'CELR': 680, 'CS': 10, 'MAN': 10, 'REM': 2900, 'LYM': 1600, 'INSTAR': 10, 'GALA': 10, 'ONG': 0.1, 'WING': 0.1, 'BFT': 390, 'IHT': 7300, 'SENC': 9800, 'TOMO': 1, 'ELEC': 16000,'SHIP': 10, 'TFD': 10, 'SNX': 1, 'HUR': 10, 'LST': 10, 'SWTH': 5, 'NKN': 5, 'SOUL': 5, 'LRN': 5, 'ADD': 20, 'MEETONE': 5, 'DOCK': 20, 'GSE': 380000, 'RATING': 45000, 'HSC': 380000, 'HIT': 140000, 'DX': 10000, 'CNNS': 2600, 'DREP': 1900, 'MBL': 10, 'GMAT': 37000, 'MIX': 5100, 'LAMB': 490, 'LEO': 10, 'BTCBULL': 0.00021, 'BTCBEAR': 6600, 'ETHBEAR': 190000, 'ETHBULL': 0.0019, 'EOSBULL': 8.7, 'EOSBEAR': 430, 'XRPBEAR': 7100, 'XRPBULL': 6.2, 'WICC': 2, 'WGRT': 100, 'SERO': 5, 'CORAL': 2, 'VIDY': 10000, 'KGC': 55000, 'FTM': 85, 'RUNE': 2, 'COS': 1, 'CBK': 4.6, 'CHZ': 420, 'XVS': 0.12, 'TWT': 1, 'AVA': 1, 'CRO': 160, 'ALY': 19000, 'WIN': 360, 'SUN': 0.0051, 'MTV': 31000, 'ONE': 1, 'ARPA': 350, 'DILI': 30000, 'ALGO': 0.1, 'PI': 0.1, 'CKB': 1, 'BKC': 81000, 'BXC': 38000, 'PAX': 15, 'USDC': 15, 'TUSD': 15, 'GARD': 100, 'CELO': 0.5, 'HPB': 25, 'CFX': 10, 'FTI': 10000, 'SOP': 230000, 'LEMO': 15000, 'NPXS': 40, 'QKC': 20, 'IOTX': 20, 'RED': 3300, 'LBA': 3100, 'KAN': 20, 'OPEN': 7100, 'MITH': 650, 'SKM': 2600, 'XVG': 20, 'NANO': 20, 'NBAI': 20, 'UPP': 20, 'ATMI': 20, 'TMT': 20, 'STRAX': 5, 'EDG': 200, 'STX': 5, 'EGLD': 0.052, 'OKT': 0.04, 'FIS': 2, 'HT': 0.1, 'MDX': 0.3, 'BAGS': 0.006, 'CIR': 0.3, 'BNB': 0.001, 'BBK': 20, 'EDR': 20, 'MET': 5.5, 'TCT': 640, 'EXC': 10, 'MXC': 650}
    get_hoo_fee = {'EOS': 0.1, 'ETH': 0.00622866, 'HC': 0.005, 'DASH': 0.002, 'QTUM': 0.1, 'VET': 100.0, 'XRP': 0.1, 'DOGE': 100.0, 'XMR': 0.01, 'BTM': 10.0, 'DCR': 0.01, 'HT': 0.1, 'BCV': 1428.57142857, 'PUB': 0.0, 'TPT': 0.0, 'RBF': 2.39391625, 'KAN': 10000.0, 'BNB':0.001, 'OMG': 2.16497077, 'ZRX': 6.76589986, 'ZIL': 128.2051282, 'DLB': 20.0, 'AE': 102.04081632, 'AION': 94.0, 'AMB': 499.0,'AOA': 700.0, 'ATX': 4031.204828, 'AUTO': 3625.306496, 'BAT': 25.31645569, 'BIX': 119.04761904, 'BLZ': 50.0, 'BNT': 4.10172272, 'BRD': 13.7355291, 'CENNZ': 50.0, 'CMT': 1000.0, 'CTXC': 158.73015873, 'CVC': 500.0, 'CVT': 40.0, 'DRGN': 68.52871512, 'FSN': 1.0, 'FUN': 1000.0, 'FXT': 1958.878705, 'GNO': 0.07457677, 'GNT': 71.94244604, 'HOT': 2000.0, 'IOST': 555.55555555, 'KNC': 5.38502961, 'LINK': 0.40893105, 'LRC': 15.47987616, 'MANA': 294.11764705, 'MCO': 2.48880039, 'MKR': 0.00373341, 'NAS': 2.0, 'NEC': 86.95652173, 'NEXO': 6.51041666, 'PAY': 204.08163265, 'QKC': 1.0, 'SNT': 156.25, 'SOC': 3333.33333333, 'STORJ': 18.93939393, 'TUSD': 10.08064516, 'AISA': 100.0, 'DCC': 1000.0, 'EOSRAM': 100.0, 'HVT': 0.0, 'EBTC': 0.0, 'EETH': 0.0, 'EUSD': 0.0, 'IHT': 937.039531, 'DICE': 0.0, 'EKT': 1000.0, 'SPC': 1235.370861, 'CHAT': 10000.0, 'HPY': 2.0, 'MAX': 0.0, 'OCT': 0.0, 'RIDL': 0.0, 'BLACK': 0.0, 'ECTT': 0.0, 'TOOK': 0.0, 'MEETONE': 0.0, 'ADD': 0.0, 'ET': 0.0, 'SEED': 0.0, 'PGL': 0.0, 'EOSDAC': 0.0, 'EPRA': 0.0, 'TOS': 10000.0, 'UGAS': 10.0, 'MXC': 10000.0, 'ZIP': 8720.902296, 'PAI': 1250.0, 'PAX': 10.01001001, 'PIN': 1000.0, 'RATING': 1000.0, 'BOS': 0.1, 'TRX': 1.0, 'BTT': 100.0, 'USDC': 10.01001001, 'GUSD': 10.09081735, 'DAI': 10.01001001, 'RVN': 1.0, 'WICC': 10.0, 'UB': 0.0, 'XIN': 0.02, 'ATOM': 0.005, 'OKB': 1.65562913, 'GT': 13.98601398, 'DLX': 0.0, 'LEO': 5.0, 'BKBT':7067.752869, 'ENTC': 1000.0, 'ONT': 1.0, 'ARN': 0.0, 'ATD': 100.0, 'BEAN': 10.0, 'BETX': 0.0, 'BG': 0.0, 'BKT': 0.0, 'BOID': 10.0, 'BRM': 0.0, 'BUFF': 0.0, 'CET': 0.0, 'CHL': 0.0, 'CUSD': 0.0, 'DEOS': 0.0, 'DRAGON': 0.0, 'EAP': 0.0, 'ECASH': 0.0, 'EMT': 0.0, 'ENB': 0.0, 'EOX': 0.0, 'FAST': 0.0, 'FOS': 0.0, 'GCHIP': 0.0, 'GGS': 0.0, 'HASH': 0.0, 'HIG': 10.0, 'HORUS': 0.0, 'INF': 0.0, 'IQ': 150.0, 'KING': 0.0, 'LLG': 0.0, 'LUCK': 0.0, 'LYNX': 0.0, 'NEWS': 1400.0, 'OGM': 0.0, 'ONE': 0.0, 'PIXEOS': 0.0, 'PKE': 0.0, 'POKER': 0.0, 'SLAM': 10.0, 'TKC': 10.0, 'TOB': 0.0, 'TRYBE': 0.0, 'TXT': 10.0, 'UCTT': 0.0, 'VIP': 0.0, 'VOID':0.0, 'VS': 0.0, 'WRK': 0.0, 'CUSE': 1000.0, 'SCEC': 1000.0, 'USE': 1000.0, 'UNC': 3333.33333333, 'FREC': 29355.5199, 'FCC': 1000.0, 'EVS': 8.42585785, 'SGN': 5508.137294, 'PIZZA': 0.0, 'KEY': 0.0, 'AAA': 1000.0, 'ARP': 1000.0, 'ALGO': 0.2, 'HXO': 0.0,'FCOCOS': 0.0, 'DILI-EOS': 0.0, 'DNAT': 10000.0, 'YEC': 0.001, 'AXE': 1.0, 'RRB': 50.0, 'GLO': 3333.33333333, 'CKB': 1.0, 'GDP': 1000.0, 'DILIO': 800.0, 'TC': 129.87012987, 'NST': 238.09523809, 'WICM': 0.1, 'KOC': 67.11409395, 'MX': 17.45200698, '5TH': 238.09523809, 'TZS': 1000.0, 'MOF': 58.47953216, 'SKR': 3000.0, 'ZVC': 0.0, 'GLOS': 2000.0, 'RUN-ERC20': 1000.0, 'TZVC': 344.8275862, 'STX': 50000.001, 'CLC': 10.0, 'FCT': 50.0, 'PGS': 8000.0, 'FBT': 20000.0, 'KAVA': 0.2, 'RNDR': 73.52941176, 'HZT': 20.0, 'PROPS': 163.93442622, 'EIDOS': 400.0, 'KSM': 0.1, 'AIX': 10000.0, 'OGN': 38.46153846, 'RUTM': 0.0001, 'SIN': 5.0, 'TRB': 0.26534348, 'BWT': 0.0, 'OXT': 23.64066193, 'PYP': 0.0, 'HTEST': 0.00160521, 'BPT': 19.19385796, 'FO': 50.0, 'TFO': 100.0, 'MDU': 1.0, 'USDA': 2.0, 'UA': 1.0, 'UCT': 2000.0, 'HDAO': 1428.57142857, 'YAS': 1.0, 'FCH': 5.0, 'TKM': 0.1, 'SVVC': 500.0, 'EXN': 1250.0, 'SBC': 100.0, 'HNEO': 0.1, 'HQTUM': 10.0, 'TROY': 2000.0, 'ETF': 0.0, 'BKCM': 500.0, 'TROY-BEP2': 10.0, 'JMC': 100.0, 'KLAY': 0.5, 'TRT': 1000.0, 'SOL': 0.2, 'MASS': 0.1, 'COMP': 0.02129285, 'USDK': 10.03009027, 'GXC': 0.5, 'HNT': 0.05, 'TWT': 5.0, 'UMA': 0.33354457, 'USDJ': 2.0, 'JST': 10.0, 'CELO': 0.1, 'DSG': 10000.0, 'ZDN': 10.0, 'KEEP': 29.32551319, 'AWC': 0.0, '2KEY': 277.77777777, 'MSC': 10.0, 'ANJ': 156.25, 'XIO': 42.01680672, 'RING': 107.52688172, 'ESH': 238.09523809, 'GTG': 1.5, 'NEST': 222.22222222, 'JRT': 95.23809523, 'RVC': 20.0, 'CDS': 2.0, 'SNX': 0.47433829, 'CLX': 20.0, 'ONG': 0.13, 'ROR': 10.0, 'IDK': 10.0, 'TCAD': 10.0, 'TAUD': 10.0, 'THKD': 10.0, 'TGBP': 10.0, 'BGBP': 10.0, 'EBASE': 10.0, 'EURS': 10.0, 'NUSD': 10.0, 'RSV': 10.0, 'USDS': 10.0, 'SUSD': 9.90099009, 'HUSD': 10.04016064, 'BUSD': 10.04016064, 'AR': 0.26, 'LYXE': 3.81533765, 'OKS': 4.0, 'BHD': 0.05, 'FOR': 263.15789473, 'DAPP': 0.0, 'RUNE': 0.5, 'REN': 11.57407407, 'FIL': 0.001, 'IDEX': 153.84615384, 'WGRT': 5.0, 'MLN': 0.23921728, 'CNYT': 71.42857142, 'CDT': 666.66666666, 'SCS': 16.0, 'CRING': 10.0, 'STAKE': 0.45390585, 'DMG': 163.93442622, 'CEL': 1.99481348, 'NMR': 0.27297046, 'CHZ': 400.0, 'BAL': 0.27360529, 'JT': 97.08737864, 'RSR': 263.15789473, 'REL': 12.45330012, 'PNK': 126.58227848, 'DEXT': 35.4609929, 'ALEPH': 30.0, 'CAN': 10.0, 'GBT': 10.0, 'LPT': 3.01023479, 'AUC': 40.48582995, 'DSF': 100.0, 'AKRO': 243.90243902, 'XOR': 0.05600076, 'AMPL': 4.0, 'STA': 102.04081632, 'COT': 10000.0, 'ASKO': 86.20689655, 'UTO': 13.69863013, 'MCX': 120.0, 'DAM': 66.66666666, 'ATTN': 169.49152542, 'AVA': 0.024, 'FLUX': 11.54734411, 'VRA': 10000.0, 'AST': 46.72897196, 'UCA': 10.0, 'IDRT': 15000.0, 'BIDR': 615.0, 'BKRW': 100.0, 'BZRX': 21.41327623, 'PLR': 400.0, 'NDX': 2565.0, 'DEC': 72.46376811, 'ORN': 2.0, 'MTA': 2.68168409, 'UTK': 32.89473684, 'OWL': 0.01, 'WNXM': 0.19016829, 'RARI': 0.97115664, 'DFS': 0.1, 'USDD': 10.0, 'MW': 2.5, 'YFI': 0.00031754, 'QXGS': 1.0, 'CTAFY': 1.0, 'DXD': 0.05145674, 'SWINGBY': 6.0, 'MTR': 1.0, 'MTRG': 1.0, 'RPL': 2.18292949, 'FIO': 5.0, 'KTON': 0.09029589, 'DMST': 400.0, 'DEV': 1.52462265, 'GEN': 72.46376811, 'DOT': 0.1, 'DAD': 54.34782608, 'YFII': 0.00483186, 'IFT': 10000.0, 'TIFT': 10.0, 'BUIDL': 4.92853622, 'PUX': 833.33333333, 'DIA': 4.52284034, 'BOT': 0.00492678, 'FNX': 44.64285714, 'XFT': 4.8756704, 'STRONG': 0.10902747, 'YAM': 0.4, 'SPA': 769.23076923, 'ETHV': 114.94252873, 'CRV': 3.25626831, 'TLOS': 1.0, 'BART': 294.11764705, 'XRT': 0.33882225, 'OM': 69.93006993, 'OGX': 0.0, 'HU': 0.01, 'CREDIT': 434.78260869, 'HAKKA': 212.76595744, 'PCX': 0.001, 'WBTC': 0.00025464, 'DIP': 3.0, 'LIEN': 0.14774103, 'BOX': 0.0, 'DF': 42.91845493, 'CVP': 3.48675034, 'SUSHI': 0.71813285, 'PEARL': 0.001, 'TAI': 0.01, 'OIN': 20.0, 'ADEL': 49.01960784, 'CRT': 0.0, 'SAL': 0.0, 'SWRV': 7.21500721, 'CREAM': 0.03840983, 'FARM': 0.03606722, 'FSW': 37.45318352, 'ULU': 11.9760479, 'DMD': 0.001, 'ZILD': 0.10673611, 'UP': 1.0, 'SUN': 0.1, 'PERP': 1.37608366, 'GOF': 4.80538202, 'GTF':5.0, 'WING': 0.01, 'ONES': 16.20745542, 'PICKLE': 0.36695901, 'HGET': 2.17485863, 'GHST': 12.45330012, 'SAFE': 2.50062515, 'MEME': 0.01222329, 'HEGIC': 32.89473684, 'UNI': 0.51948051, 'FRONT': 12.82051282, 'LINA': 113.63636363, 'DHT': 3.23101777, 'DEGO': 7.41839762, 'BAND': 0.83801223, 'OBEE': 2000.0, 'WHALE': 1.38908181, 'CRU': 1.0670081, 'AVAX': 0.01, 'UNII': 250.0, 'COVAL': 10000.0, 'BONK': 63.29113924, 'ZOM': 0.90661831, 'SHROOM': 78.125, 'HOO': 169.49152542, 'SLP': 384.61538461, 'ARTE': 3.68867576, 'SKL': 57.14285714, 'LAYER': 24.50980392, 'NFT': 86.95652173, 'BID': 833.33333333, 'RFUEL': 116.27906976, 'DANDY': 0.06664933, 'BUILD': 0.17283993, 'WANATHA': 117.64705882, 'IFT-TRC20': 1000.0, 'FIN': 26.73796791, 'YELD': 0.23375409, 'PGT': 0.07208246, 'GTH': 100.0, 'AAVE': 0.09837407, 'DAOFI': 33.89830508, 'PLOT': 166.66666666, 'UFT': 11.87648456, 'NU': 19.08396946, 'HEZ': 1.59489633, 'RAMP': 40.32258064, 'REVV': 136.98630136, 'BIW': 25.0, 'RGT': 2.19635405, 'RAK': 0.27956388, 'BOND': 0.15405946, 'WOO': 163.93442622, 'KP3R': 0.02653082, 'BVB': 500.0, 'YF': 0.10257462, 'DOUGH': 5.92768227, 'NSURE': 13.19261213, 'PTERIA': 4.3047783, 'ROOK': 0.01858425, 'LTX': 86.20689655, 'SPKL': 5000.0, 'APY': 10.83423618, 'BCHA': 0.001, 'DSLA': 5000.0, 'CFX': 1.0, 'DVI': 68.96551724, 'PRQ': 8.15660685, 'AC': 7.65110941, 'SFI': 0.00791941, 'SYN': 44.24778761, 'INDEX': 0.48255561, 'EXRD': 86.20689655, 'FYZ': 20.0, 'ANT': 1.83183733, 'ATRI': 100.0, 'MPH': 0.003, 'ORAI': 0.2, 'EPAN': 20.0, 'ATP': 0.2, 'TRU': 25.0, 'KOMET': 0.05, 'ARCH': 5.27704485, 'MARK': 1.5, 'AIN': 160.0, 'YFC': 0.05, 'WDP': 0.1, 'KEX': 19.01140684, 'FWT': 1000.0, 'CFI': 1.0, 'BUND': 1.0, 'MTS': 1.5, 'WON': 500.0, 'YFD': 0.01, 'TME': 0.01, 'GDAO': 2.0, 'CLIQ': 100.0, 'OPEN': 7.1890726, 'WFIL': 0.1, 'UMEX': 20.0, 'ZIN': 500.0, 'API3': 2.16966804, 'ZORA': 0.01, 'SWISS': 0.01, 'CRBN': 100.0, 'BIRD': 1.0, 'STV':500.0, 'DG': 0.13357555, 'LOAD': 100.0, 'BETC': 0.5, 'EOC': 1.0, 'STPL': 250.0, 'BUP': 15.0, 'IDLE': 2.0, 'PSK': 50.0, 'MIXS': 25.0, 'BADGER': 0.11894566, 'BSC': 0.015, 'ZEN': 10000.001, 'MONA': 0.005, 'ITS': 0.3, 'UCAP': 3.0, 'XCUR': 4.73933649, 'PPAY': 140.84507042, 'YFIA': 3.0, 'YLD': 0.15, 'MVEDA': 80.0, 'SKD': 0.01, 'FAR': 10.0, 'SPDR': 322.58064516, 'DEFO': 0.02, 'DFO': 40.0, 'GRT': 10.30927835, 'ANRX': 60.0, 'MAHA': 0.73904367, 'FXS': 1.58378207, 'POND': 144.92753623, 'LON': 1.58982511, 'TWT1': 0.8, 'FRM': 26.31578947, 'UDT': 2.02675314, 'DDX': 1.02019995, '1INCH': 1.97316495, 'DRIP': 50.0, 'CBK': 20.0, 'DUCK': 125.0, 'DATX': 10000.0, 'REEF': 312.5, 'WHITE': 0.00274246, 'ORI': 1.0, 'FIRE': 23.36448598, 'HYPE': 5.0, 'GUSDT': 0.2, 'MIS': 0.34843205, 'KEK': 500.0, 'BAFI': 2.0, '3XT': 0.003, 'BAS': 0.07616146, 'BLW': 5.38793103, 'PIS': 0.39602391, 'XED': 20.12072434, 'LDO': 3.8595137, 'FOX': 20.49180327, 'NFTX': 0.2, 'RFY': 50.0, 'DSWAP': 5.0, 'RBC': 20.0, 'SPI': 2.0, 'PFI': 0.08, 'TTC': 0.0, 'SIL': 10.0, 'COMBO': 2.10304942, 'NORD': 1.44112984, 'PRT': 300.0, 'MIR': 1.89250567, 'DXF': 120.0, 'CURRY': 7.0, 'VRX': 0.03, 'RBYTE': 10.0, 'GFC': 87.71929824, 'POOLZ': 0.38412783, 'YOP': 9.02527075, 'MFT': 625.0, 'MUST': 0.01, 'PSI': 10.0, 'ARTH': 10.0, 'SUBS': 4.99750124, 'POLS': 4.33651344, 'AXS': 8.03212851, 'SDT': 0.80411707, 'CVR': 17.92114695, 'ARMOR': 5.0, 'MDX': 0.01, 'TROP': 0.01, 'TOZ': 27.0, 'UNDG': 0.01, 'JULB': 0.01111012, 'JULD': 5.91715976, 'FLOW': 0.0, 'OPIUM': 1.0, 'SH': 0.12490632, 'DONUT': 83.33333333, 'RAZOR': 2.35849056, 'NCT': 12.34567901}
    #{'EOS': 0.1, 'BTC': 0.0005, 'ETH': 0.007, 'HC': 0.5, 'DASH': 0.02, 'NEO': 0.0, 'QTUM': 0.1, 'VET': 100.0, 'XRP': 0.1, 'DOGE':50.0, 'XMR': 0.01, 'BTM': 10.0, 'DCR': 0.01, 'HT': 0.8, 'PUB': 0.0, 'TPT': 100.0, 'RBF': 2.39391625, 'KAN': 900.0, 'BNB': 0.001, 'OMG': 1.5, 'ZRX': 10.0, 'ZIL': 0.1, 'DLB': 20.0, 'AE': 10.0, 'AION': 94.0, 'AMB': 499.0, 'AOA': 700.0, 'ATX': 4031.20482777, 'AUTO': 3625.30649559, 'BAT': 5.0, 'BIX': 11.53565654, 'BLZ': 50.0, 'BNT': 5.0, 'BRD': 13.7355291, 'CENNZ': 50.0, 'CMT': 122.73254237, 'CTXC': 12.93088277, 'CVC': 70.0, 'CVT': 40.0, 'DRGN': 68.52871512, 'FSN': 1.0, 'FUN': 1000.0, 'FXT': 1958.87870481, 'GNO': 0.06, 'GNT': 25.26006977, 'HOT': 2000.0, 'IOST': 5.0, 'KNC': 4.0, 'LINK': 0.5, 'LRC': 20.0, 'MANA': 24.01449913, 'MCO': 0.3, 'MKR': 0.008, 'NAS': 2.0, 'NEC': 7.0, 'NEXO': 20.0, 'PAY': 21.38080805, 'QKC': 1.0, 'SNT': 200.0, 'SOC': 311.67374462, 'STORJ': 13.0, 'AISA': 100.0, 'DCC': 1000.0, 'EOSRAM': 100.0, 'HVT': 0.0, 'EBTC': 0.0, 'EETH': 0.0, 'IHT': 937.03953101, 'VNS': 1000.0, 'DICE': 0.0, 'EKT': 1000.0, 'SPC': 1235.37086057, 'CHAT': 612.88362251, 'HPY': 2.0, 'MAX': 0.0, 'OCT': 0.0, 'RIDL': 0.0, 'BLACK': 0.0, 'ECTT': 0.0, 'TOOK': 0.0, 'SEED': 0.0, 'PGL': 0.0, 'TOS': 817.10132117, 'UGAS': 10.0, 'MXC': 591.90921228, 'ZIP': 8720.90229578, 'PAI': 90.0, 'HX': 0.1, 'PAX': 4.0, 'PIN': 1000.0, 'BOS': 0.1, 'TRX': 1.0, 'BTT': 150.0, 'RVN': 1.0, 'WICC': 100.0, 'UB': 0.0, 'XIN': 0.02, 'ATOM': 0.005, 'OKB': 0.6, 'GT': 5.0, 'DLX': 0.0, 'LEO': 5.0, 'BKBT': 7067.75286918, 'ENTC': 1000.0, 'ONT': 1.0, 'ARN': 0.0, 'ATD': 100.0, 'BEAN': 10.0, 'BETX': 0.0, 'BOID': 10.0, 'BRM': 0.0, 'BUFF': 0.0, 'CET': 0.0, 'CHL': 0.0, 'DRAGON': 0.0, 'EAP': 0.0, 'ECASH': 0.0, 'EMT': 0.0, 'ENB': 0.0, 'EOSABC': 0.0, 'FAST': 0.0, 'GCHIP': 0.0, 'GGS': 0.0, 'HASH': 0.0, 'HIG': 10.0, 'HORUS': 0.0, 'INF': 0.0, 'IQ': 100.0, 'JKR': 0.0, 'JOY': 0.0, 'KING': 0.0, 'LLG': 0.0, 'LUCK': 0.0, 'LYNX': 0.0, 'MEV': 0.0, 'MGT': 0.0, 'MUR': 0.0, 'NEWS': 1400.0, 'OGM': 0.0, 'OKT': 0.0, 'ONE': 0.0, 'POKER': 0.0, 'POOR': 0.0, 'PTI': 0.0, 'SENSE': 0.0, 'SKY': 0.0, 'SLAM': 10.0, 'TKC': 10.0, 'TOB': 0.0, 'TRYBE': 0.0, 'TXT': 10.0, 'UCTT': 0.0, 'VIP': 0.0, 'VOID': 0.0, 'XPC': 0.0, 'ZKS': 0.0, 'CUSE': 1000.0, 'SCEC': 1000.0, 'USE': 1000.0, 'UNC': 1000.0, 'FREC': 29355.5198973, 'FCC': 1000.0, 'EVS': 8.42585785, 'SGN': 5508.13729426, 'PIZZA': 0.0, 'KEY': 0.0, 'ARP': 1000.0, 'ALGO': 0.2, 'DNAT': 20.0, 'YEC': 0.5, 'AXE': 1.0, 'RRB': 50.0, 'GLO': 18000.0, 'CKB': 20.0, 'GDP': 1000.0, 'DILIO': 800.0, 'TC': 8700.0, 'NST':100.0, 'WICM': 0.1, 'KOC': 7.0, 'MX': 15.0, '5TH': 20.0, 'TZS': 1000.0, 'MOF': 2.5, 'SKR': 3000.0, 'ZVC': 10.5, 'GLOS': 300.0, 'TZVC': 25.0, 'STX': 50.0, 'CLC': 10.0, 'FCT': 50.0, 'PGS': 8000.0, 'FBT': 20000.0, 'KAVA': 0.2, 'RNDR': 12.0, 'HZT': 20.0, 'PROPS': 15.0, 'EIDOS': 400.0, 'KSM': 0.1, 'AIX': 10000.0, 'OGN': 20.0, 'RUTM': 0.0001, 'SIN': 5.0, 'TRB': 0.1, 'BWT': 0.0, 'OXT': 15.0, 'PYP': 0.0, 'BPT': 20.0, 'FO': 50.0, 'TFO': 100.0, 'MDU': 1.0, 'UA': 1.0, 'UCT': 0.1, 'HDAO': 50.0, 'YAS': 5.0, 'FCH': 5.0, 'TKM': 0.1, 'SVVC': 500.0, 'EXN': 5.0, 'SBC': 100.0, 'HNEO': 0.1, 'HQTUM': 10.0, 'TROY': 2000.0, 'ETF': 0.0, 'BKCM': 500.0, 'JMC': 100.0, 'KLAY': 0.5, 'TRT': 1000.0, 'SOL': 0.2, 'MASS': 1.0, 'COMP': 0.03, 'GXC': 0.5, 'HNT': 0.05, 'TWT': 10.0, 'UMA': 0.4, 'JST': 25.0, 'CELO': 0.1, 'DSG': 20.0, 'ZDN': 10.0, 'KEEP': 5.0, '2KEY': 20.0, 'MSC': 20.0, 'ANJ': 25.0, 'XIO': 10.0, 'RING': 70.0, 'ESH': 10.0, 'GTG': 1.5, 'NEST': 100.0, 'JRT': 1.0, 'RVC': 20.0, 'CDS': 2.0, 'SNX': 1.0, 'CLX': 20.0, 'ONG':1.0, 'ROR': 10.0, 'IDK': 10.0, 'TCAD': 10.0, 'TAUD': 10.0, 'RSV': 10.0, 'AR': 1.0, 'KAI': 300.0, 'LYXE': 4.0, 'OKS': 5.0, 'BHD': 0.05, 'DASV': 100.0, 'FOR': 100.0, 'DAPP': 1.0, 'REN': 20.0, 'FIL': 0.05, 'IDEX': 64.0, 'WGRT': 10.0, 'MLN': 0.15, 'CNYT':0.0, 'CDT': 166.0, 'SCS': 16.0, 'CRING': 650.0, 'STAKE': 0.2, 'DMG': 12.0, 'CEL': 1.0, 'NMR': 0.1, 'CHZ': 150.0, 'BAL': 0.3, 'JT': 30.0, 'RSR': 400.0, 'REL': 1.0, 'PNK': 64.0, 'SWTH': 15.0, 'DEXT': 90.0, 'ALEPH': 30.0, 'CAN': 10.0, 'GBT': 10.0, 'LPT':0.2, 'AUC': 5.0, 'DSF': 100.0, 'AKRO': 400.0, 'XOR': 0.025, 'AMPL': 4.0, 'STA': 10.0, 'COT': 10000.0, 'ASKO': 600.0, 'UTO': 1.2, 'MCX': 120.0, 'DAM': 5.0, 'ATTN': 30.0, 'AVA': 1.0, 'FLUX': 0.28, 'VRA': 5555.0, 'AST': 28.0, 'UCA': 10.0, 'IDRT': 15000.0, 'BIDR': 600.0, 'BKRW': 100.0, 'BZRX': 22.0, 'PLR': 70.0, 'NDX': 2565.0, 'DEC': 50.0, 'ORN': 2.0, 'MCB': 0.35, 'MTA': 2.0, 'UTK': 40.0, 'OWL': 0.01, 'WNXM': 0.28, 'RARI': 1.0, 'DFS': 0.2, 'USDD': 10.0, 'PLT': 60.0, 'MW': 2.5, 'YFI': 0.0002, 'QXGS': 1.0, 'CTAFY': 1.0, 'DXD': 0.02, 'SWINGBY': 6.0, 'MTR': 1.0, 'MTRG': 1.0, 'RPL': 3.0, 'FIO': 5.0, 'KTON': 0.03, 'DMST': 66.0, 'DEV': 0.6, 'GEN': 12.0, 'DOT': 0.1, 'DAD': 7.0, 'YFII': 0.001, 'IFT': 2000.0, 'TIFT': 10.0, 'BUIDL': 1.0, 'PUX': 285.0, 'DIA': 0.8, 'BOT': 0.01, 'FNX': 6.0, 'XFT': 2.0, 'STRONG': 0.02, 'YAM': 0.4, 'ETHV': 4.0, 'CRV': 4.0, 'TLOS': 1.0, 'BART': 100.0, 'XRT': 0.25, 'OM': 6.0, 'OGX': 2.0, 'HU': 0.01, 'CREDIT': 60.0, 'HAKKA': 6.0, 'DIP': 3.0, 'LIEN': 0.1, 'BOX': 0.25, 'DF': 26.0, 'CVP': 2.0, 'SUSHI': 3.0, 'PEARL': 0.0003, 'TAI': 0.06, 'OIN': 10.0, 'ADEL': 8.0, 'CRT': 1.0, 'SAL': 0.07, 'SWRV': 3.0, 'CREAM':0.04, 'FARM': 0.005, 'FSW': 20.0, 'ULU': 0.0125, 'DMD': 0.0025, 'ZILD': 0.04, 'UP': 5.0, 'SUN': 0.05, 'PERP': 4.0, 'GOF': 3.0, 'GTF': 5.0, 'WING': 0.01, 'ONES': 5.0, 'PICKLE': 0.2, 'HGET': 0.8, 'GHST': 20.0, 'SAFE': 0.02, 'MEME': 0.03, 'SLM': 0.01, 'HEGIC': 20.0, 'UNI': 1.0, 'FRONT': 10.0, 'LINA': 200.0, 'DHT': 5.0, 'DEGO': 20.0, 'BAND': 1000.01, 'OBEE': 2000.0, 'WHALE': 0.5, 'CRU': 1.0, 'AVAX': 0.01, 'UNII': 250.0, 'COVAL': 800.0, 'BONK': 10.0, 'ASTRO': 6.0, 'ZOM': 0.1, 'SHROOM': 20.0, 'HOO': 70.0, 'SLP': 100.0, 'ARTE': 1.0, 'SKL': 120.0, 'LAYER': 20.0, 'NFT': 30.0, 'BID': 150.0, 'RFUEL': 30.0, 'DANDY': 0.015, 'BUILD': 0.15, 'FIN': 1.0, 'YELD': 0.05, 'PGT': 0.03, 'GTH': 80.0, 'AAVE': 0.1, 'DAOFI': 40.0, 'PLOT': 20.0, 'UFT': 8.0, 'NU': 30.0, 'HEZ': 1.0, 'RAMP': 100.0, 'REVV': 160.0, 'CFS': 25.0, 'BIW': 25.0, 'RGT': 4.0, 'RAK': 0.05, 'BOND': 0.02, 'WOO': 45.0, 'KP3R': 0.02, 'BVB': 40.0, 'YF': 0.01, 'DOUGH': 5.0, 'NSURE': 10.0, 'PTERIA': 0.7, 'ROOK': 0.03, 'LTX': 10.0, 'SPKL': 5000.0, 'BCHA': 0.001, 'CFX': 1.0, 'FC': 0.1, 'DVI': 100.0, 'PRQ': 10.0, 'AC': 10.0, 'SFI': 0.0001, 'SYN': 8.0, 'INDEX': 0.5, 'FIS': 0.3, 'EXRD': 25.0, 'FYZ': 10.0, 'ANT': 1.0, 'ATRI': 100.0, 'ORAI': 0.2, 'EPAN': 20.0, 'TRU': 25.0, 'KOMET': 0.05, 'ARCH': 12.0, 'MARK': 1.5, 'AIN': 160.0, 'YFC': 0.05, 'WDP': 0.1, 'KEX': 1.0, 'FWT': 1000.0, 'CFI': 1.0, 'BUND': 1.0, 'MTS': 1.5, 'WON': 500.0, 'YFD': 0.01, 'TME': 0.01, 'GDAO': 2.0, 'CLIQ': 50.0, 'OPEN': 80.0, 'WFIL': 0.1, 'UMEX': 20.0, 'ZIN': 500.0, 'API3': 2.0, 'ZORA': 0.01, 'SWISS': 0.01, 'CRBN': 100.0, 'BIRD': 1.0, 'STV': 500.0, 'DG': 0.2, 'LOAD': 100.0, 'BETC': 0.5, 'EOC': 1.0, 'STPL': 250.0, 'BUP': 15.0, 'PSK': 50.0, 'MIXS': 25.0, 'BADGER': 0.5, 'BSC': 0.015, 'MONA': 0.005, 'ITS': 0.3, 'UCAP': 3.0, 'XCUR': 150.0, 'PPAY': 50.0, 'YFIA': 3.0, 'YLD': 0.15, 'MVEDA': 80.0, 'SKD': 0.01, 'FAR': 10.0, 'SPDR': 80.0, 'DEFO': 0.02, 'DFO': 40.0, 'GRT': 8.0, 'ANRX': 60.0, 'MAHA': 0.5, 'FXS': 0.15, 'POND': 30.0, 'LON': 3.0, 'TWT1': 1.0, 'FRM': 35.0, 'UDT': 0.7, 'DDX': 1.0, '1INCH': 5.0, 'DRIP': 50.0, 'CBK': 20.0, 'DATX': 10000.0, 'REEF': 35.0, 'WHITE': 0.002, 'ORI': 0.05, 'FIRE': 8.0, 'HYPE': 5.0, 'MIS': 0.008, 'KEK': 500.0, 'BAFI': 2.0, '3XT': 0.003}
    get_binance_fee = {'STPT': 321.0, 'MXN': 0.0, 'UGX': 0.0, 'RENBTC': 0.00026, 'GLM': 37.0, 'NEAR': 0.072, 'AUDIO': 34.0, 'HNT': 0.05, 'CDT': 753.0, 'SPARTA': 0.15, 'SUSD': 13.0, 'AION': 67.0, 'NPXS': 4598.0, 'DGB': 0.2, 'ZRX': 7.92, 'BCD': 0.01, 'EASY': 0.7, 'WING': 0.002, 'AE': 131.0, 'WNXM': 0.25, 'BCH': 0.023, 'JST': 50.0, 'HOT': 4189.0, 'IRIS': 1.0, 'BCX': 0.5, 'SEK': 0.0, 'TRIG': 50.0, 'RCN': 163.0, 'COVER': 0.012, 'FLM': 0.5, 'GNT': 0.0, 'VITE': 1.0, 'BKRW': 10.0, 'XPR': 1.0, 'SFP': 0.087, 'DIA': 5.43, 'RDN': 19.0, 'ARDR': 2.0, 'CLOAK': 0.02, 'NEBL': 0.01, 'BEL': 5.67, 'JUV': 0.0, 'VTHO': 200.0, 'SALT': 5.2, 'STORM': 100.0, 'REN': 11.0, 'REP': 0.46, 'ADA': 1.0, 'ELF': 53.0, 'REQ': 131.0, 'STORJ': 19.0, 'CHF': 0.0, 'ADD': 100.0, 'BZRX': 25.0, 'SGT': 200.0, 'DF': 35.0, 'PAXG': 0.005, 'YOYO': 497.0, 'PAX': 14.0, 'CHR': 231.0, 'VND': 0.0, 'WAVES': 0.002, 'CHZ': 293.0, 'ADX': 20.0, 'XRP': 0.25, 'WPR': 517.0, 'AED': 0.0, 'SAND': 48.0, 'DKK': 0.0, 'OCEAN': 13.0, 'FOR': 227.0, 'UMA': 0.61, 'SCRT': 0.1, 'TUSD': 14.0, 'WABI': 62.0, 'IDRT': 219780.0, 'ENG': 0.0, 'ENJ': 27.0, 'YFII': 0.0052, 'KZT': 0.0, 'OAX': 51.0, 'GRT': 7.09, 'GRS': 0.2,'UND': 5.0, 'HARD': 0.1, 'TFUEL': 3.66, 'LEND': 1.0, 'DLT': 110.0, 'TROY': 1758.0, 'UNI': 0.53, 'HUF': 0.0, 'SBTC': 0.0005, 'CKB': 1.0, 'WRX': 44.0, 'XTZ': 0.5, 'LUNA': 0.01, 'AGI': 83.0, 'BCHA': 0.001, 'EON': 10.0, 'EOP': 5.0, 'EOS': 0.1, 'GO': 0.01,'NCASH': 5798.0, 'RIF': 3.0, 'EOSBULL': 0.005, 'SKL': 100.0, 'PEN': 0.0, 'BLINK': 50.0, 'HC': 0.005, 'SKY': 0.02, 'BURGER': 0.024, 'NAS': 0.1, 'NAV': 0.2, 'GTO': 643.0, 'WTC': 13.0, 'XVG': 0.1, 'TNB': 4082.0, 'DNT': 51.0, 'BULL': 0.0, 'XVS': 0.0028, 'STEEM': 0.01, 'BVND': 6913.0, 'SLP': 204.0, 'TNT': 1758.0, 'NBS': 1.0, 'DOT': 0.1, 'IQ': 50.0, 'CMT': 1.0, '1INCH': 3.22, 'XRPBULL': 0.076, 'MITH': 694.0, 'ERD': 1000.0, 'CND': 694.0, 'UNFI': 0.5, 'FTM': 31.0, 'POWR': 54.0, 'GVT': 3.1, 'WINGS': 20.0, 'FTT': 0.43, 'RLC': 7.92, 'PHB': 3.0, 'ATOM': 0.005, 'BLZ': 78.0, 'SNM': 586.0, 'MBL': 15.0, 'SNT': 139.0, 'SNX': 0.68, 'FUN': 454.0, 'COS': 799.0, 'USD': 0.0, 'QKC': 909.0, 'ROSE': 0.1, 'SOL': 0.01, 'ETC': 0.01, 'ETF': 1.0, 'BNB': 0.0, 'CELR': 712.0, 'OGN': 38.0, 'ETH': 0.006, 'MCO': 1.41, 'NEO': 0.0, 'TOMO': 0.01, 'CELO': 0.001, 'GXS': 0.3, 'TRB': 0.36, 'BNT': 2.25, 'QLC': 1.0, 'LBA': 10.0, 'MDA': 11.0, 'UTK': 33.0, 'EOSBEAR': 0.022, 'HEGIC': 36.0, 'AMB': 296.0, 'TRU': 36.0, 'WBNB': 0.002, 'FUEL': 564.0, 'DREP': 1758.0, 'TRY': 0.0, 'TRX': 1.0, 'MDT': 280.0, 'MDX': 100.0, 'AERGO': 112.0, 'EUR': 0.0, 'BOT': 0.0052, 'NULS': 24.0, 'NGN': 0.0, 'EGLD': 0.001, 'ANTOLD': 1.0, 'FXS': 1.48, 'HNST': 10.0, 'CRV': 5.56, 'EVX': 23.0, 'BAKE': 0.11, 'ANT': 2.76, 'SRM': 2.45, 'PLN': 0.0, 'ETHBEAR': 0.0, 'OG': 0.0, 'MFT': 859.0, 'BETH': 0.0081, 'BQX': 2.27, 'BRD': 67.0, 'BUSD': 10.0, 'CTK': 0.01, 'ARPA': 356.0, 'BRL': 0.0, 'CTR': 35.0, 'MATIC': 96.0, 'IOTX': 0.0, 'FRONT': 4.18, 'ZAR': 0.0, 'DOCK': 333.0, 'STX': 10.0, 'PNT': 8.95, 'DENT': 7018.0, 'BCPT': 6162.0, 'BNBBEAR': 0.011, 'VIBE': 4240.0, 'SUB': 40.0, 'POA': 214.0, 'IOST': 246.0, 'CAKE': 0.014, 'POE': 20000.0, 'OMG': 2.62, 'BAND': 0.87, 'SUN': 0.0031, 'BTC': 0.00026, 'TWT': 0.38, 'NKN': 280.0, 'RSR': 283.0, 'CVC': 35.0, 'IOTA': 0.5, 'REEF': 387.0, 'BTG': 0.001, 'KES': 0.0, 'ARK': 0.2, 'BTM': 5.0, 'CVP': 4.31, 'ARN': 17.0, 'KEY': 1185.0, 'BTS': 1.0, 'BTT': 32.0, 'ONE': 0.001, 'ONG': 0.11, 'ANKR': 454.0, 'SUSHI': 0.83, 'ALGO': 0.01, 'ZCX': 1.0, 'SC':0.1, 'WBTC': 0.00026, 'ONT': 1.0, 'PPT': 7.19, 'ONX': 7.0, 'RUB': 0.0, 'PIVX': 0.2, 'ASR': 0.0, 'FIRO': 0.02, 'AST': 58.0, 'MANA': 53.0, 'MEETONE': 300.0, 'QSP': 274.0, 'ATD': 100.0, 'NMR': 0.33, 'MKR': 0.006, 'DODO': 2.57, 'LIT': 1.56, 'ZEC': 0.005, 'ATM': 0.0, 'APPC': 170.0, 'JEX': 50.0, 'ICX': 0.02, 'LOOM': 108.0, 'ZEN': 0.002, 'KP3R': 0.045, 'DUSK': 58.0, 'ALPHA': 9.95, 'DOGE': 50.0, 'BOLT': 10.0, 'SXP': 5.16, 'HBAR': 1.0, 'RVN': 1.0, 'AUD': 0.0, 'NANO': 0.01, 'IDR': 0.0, 'CTSI': 74.0, 'KAVA': 0.001, 'PSG': 0.0, 'HCC': 0.0005, 'VIDT': 20.0, 'NOK': 0.0, 'AVA': 0.097, 'SYS': 1.0, 'COCOS': 16.0, 'STRAX': 0.1, 'CZK': 0.0,'GAS': 0.005, 'COVEROLD': 0.055, 'THETA': 0.1, 'WAN': 0.1, 'ORN': 1.43, 'PERL': 229.0, 'AAVE': 0.1, 'XRPBEAR': 0.0012, 'GBP':0.0, 'LLT': 100.0, 'YFI': 0.00037, 'PERLOLD': 0.0, 'MOD': 5.0, 'OST': 732.0, 'AXS': 8.84, 'ZIL': 0.0, 'VAI': 0.8, 'XEM': 4.0,'CTXC': 74.0, 'BIDR': 4032.0, 'BCHSV': 0.0001, 'COMP': 0.033, 'ETHBNT': 5.0, 'RUNE': 0.059, 'GHST': 11.0, 'KMD': 0.002, 'IDEX': 212.0, 'DEXE': 1.49, 'AVAX': 0.01, 'UAH': 0.0, 'KNC': 7.43, 'PROS': 0.029, 'PROM': 0.79, 'CHAT': 100.0, 'BGBP': 2.81, 'HIVE': 0.01, 'SNGLS': 1054.0, 'DAI': 14.0, 'FET': 52.0, 'ETHBULL': 0.0, 'LRC': 21.0, 'REPV1': 0.1, 'ADXOLD': 5.0, 'MTH': 676.0, 'MTL': 14.0, 'VET': 100.0, 'USDT': 0.5, 'USDS': 2.0, 'OXT': 24.0, 'DASH': 0.002, 'NVT': 0.1, 'SWRV': 9.89, 'EDO': 2.23, 'GHS': 0.0, 'BTCST': 0.00066, 'HKD': 0.0, 'LSK': 0.1, 'CAD': 0.0, 'BEAR': 0.0, 'BEAM': 0.1, 'CAN': 5.0, 'DCR': 0.01, 'CREAM': 0.078, 'DATA': 153.0, 'ENTRP': 10.0, 'LTC': 0.0013, 'USDC': 14.0, 'WIN': 1135.0, 'BNBBULL': 0.012, 'INJ': 0.92, 'TCT': 599.0, 'LTO': 42.0, 'NXS': 0.02, 'INR': 0.0, 'CBK': 1.2, 'CBM': 200.0, 'INS': 52.0, 'JPY': 0.0, 'XLM': 0.01, 'LINK': 0.46, 'QTUM': 0.01, 'UFT': 5.0, 'LUN': 1.54, 'KSM': 0.01, 'FIL': 0.36, 'POLY': 45.0, 'STMX': 1318.0, 'BAL': 0.35, 'FIO': 5.0, 'VIB': 237.0, 'VIA': 0.01, 'BAT': 27.0, 'VRAB': 300.0, 'AKRO': 371.0, 'NZD': 0.0, 'XMR': 0.0001, 'COTI': 71.0}
    #get_binance_fee = {'CTR': 35.0, 'MATIC': 328.0, 'STPT': 339.0, 'MXN': 0.0, 'UGX': 0.0, 'RENBTC': 0.0002, 'IOTX': 0.0, 'GLM': 53.0, 'FRONT': 20.0, 'ZAR': 0.0, 'NEAR': 0.01, 'AUDIO': 36.0, 'HNT': 0.05, 'CDT': 856.0, 'SPARTA': 0.54, 'DOCK': 334.0, 'SUSD': 5.63, 'STX': 10.0, 'PNT': 16.0, 'DENT': 29630.0, 'AION': 83.0, 'NPXS': 33334.0, 'BCPT': 294.0, 'BNBBEAR': 0.011, 'DGB': 0.2, 'VIBE': 345.0, 'ZRX': 15.0, 'SUB': 40.0, 'BCD': 0.01, 'EASY': 1.46, 'WING': 0.0016, 'POA': 307.0, 'AE': 0.1, 'WNXM': 0.25, 'IOST': 1037.0, 'BCH': 0.017, 'CAKE': 0.12, 'POE': 20000.0, 'OMG': 2.3, 'JST': 50.0, 'BAND': 1.06, 'HOT': 9855.0, 'SUN': 0.0044, 'BTC': 0.0002, 'TWT': 0.46, 'NKN': 312.0, 'RSR': 234.0, 'IRIS': 1.0, 'CVC': 67.0, 'IOTA': 0.5, 'REEF': 469.0, 'BTG': 0.001, 'BCX': 0.5, 'SEK': 0.0, 'KES': 0.0, 'ARK': 0.2, 'BTM': 5.0, 'TRIG': 50.0, 'RCN': 153.0, 'CVP': 3.23, 'ARN': 17.0, 'KEY': 2836.0, 'BTS': 1.0, 'COVER': 0.054, 'BTT': 91.0, 'FLM': 0.5, 'ONE': 0.001, 'ONG': 0.11, 'ANKR': 657.0, 'SUSHI': 1.81, 'GNT': 0.0, 'VITE': 1.0, 'ALGO':0.01, 'SC': 0.1, 'BKRW': 10.0, 'WBTC': 0.0002, 'ONT': 1.0, 'PPT': 11.0, 'XPR': 1.0, 'DIA': 4.84, 'RDN': 35.0, 'RUB': 0.0, 'PIVX': 0.2, 'ASR': 0.011, 'ARDR': 2.0, 'AST': 74.0, 'CLOAK': 0.02, 'MANA': 71.0, 'NEBL': 0.01, 'BEL': 6.56, 'JUV': 0.01, 'VTHO':200.0, 'MEETONE': 300.0, 'QSP': 209.0, 'SALT': 5.2, 'STORM': 100.0, 'ATD': 100.0, 'NMR': 0.26, 'MKR': 0.01, 'REN': 18.0, 'ATM': 0.0075, 'REP': 0.34, 'APPC': 219.0, 'JEX': 50.0, 'ELF': 54.0, 'REQ': 201.0, 'STORJ': 19.0, 'ICX': 0.02, 'CHF': 0.0, 'ADD': 100.0, 'BZRX': 36.0, 'SGT': 200.0, 'DF': 51.0, 'LOOM': 195.0, 'ZEN': 0.002, 'PAXG': 0.005, 'YOYO': 1.0, 'PAX': 5.77, 'KP3R': 0.026, 'DUSK': 134.0, 'ALPHA': 26.0, 'DOGE': 50.0, 'BOLT': 10.0, 'SXP': 8.2, 'HBAR': 1.0, 'RVN': 1.0, 'CHR': 255.0, 'VND': 0.0,'AUD': 0.0, 'NANO': 0.01, 'WAVES': 0.002, 'CHZ': 285.0, 'ADX': 16.0, 'IDR': 0.0, 'XRP': 0.25, 'WPR': 788.0, 'CTSI': 140.0, 'AED': 0.0, 'SAND': 156.0, 'KAVA': 0.001, 'DKK': 0.0, 'PSG': 0.01, 'OCEAN': 17.0, 'FOR': 365.0, 'UMA': 0.74, 'HCC': 0.0005, 'VIDT': 9.89, 'NOK': 0.0, 'AVA': 0.048, 'SYS': 1.0, 'COCOS': 1.0, 'STRAX': 0.1, 'SCRT': 0.1, 'TUSD': 5.77, 'CZK': 0.0, 'GAS': 0.005, 'WABI': 59.0, 'COVEROLD': 0.055, 'IDRT': 82126.0, 'ENG': 0.0, 'THETA': 0.1, 'ENJ': 43.0, 'YFII': 0.0038, 'KZT': 0.0, 'WAN':0.1, 'OAX': 63.0, 'GRT': 16.0, 'GRS': 0.2, 'UND': 5.0, 'HARD': 0.1, 'TFUEL': 6.18, 'ORN': 2.75, 'PERL': 243.0, 'LEND': 1.0, 'DLT': 135.0, 'TROY': 2190.0, 'UNI': 1.26, 'AAVE': 0.1, 'XRPBEAR': 0.0012, 'GBP': 0.0, 'LLT': 100.0, 'HUF': 0.0, 'SBTC': 0.0005, 'WRX': 87.0, 'YFI': 0.00027, 'XTZ': 0.5, 'LUNA': 0.01, 'PERLOLD': 50.0, 'AGI': 115.0, 'MOD': 5.0, 'EON': 10.0, 'EOP': 5.0, 'EOS': 0.1, 'GO': 0.01, 'NCASH': 7476.0, 'EOSBULL': 0.005, 'OST': 365.0, 'SKL': 100.0, 'PEN': 0.0, 'BLINK': 50.0, 'HC': 0.005, 'AXS': 9.9, 'ZIL': 0.01, 'SKY': 0.02, 'BURGER': 0.13, 'NAS': 0.1, 'XEM': 4.0, 'NAV': 0.2, 'GTO': 597.0, 'CTXC': 70.0, 'WTC': 20.0, 'XVG': 0.1, 'TNB': 2815.0, 'BIDR': 527.0, 'DNT': 123.0, 'BCHSV': 0.0001, 'BULL': 0.0, 'COMP': 0.04, 'ETHBNT': 5.0, 'XVS':0.021, 'STEEM': 0.01, 'BVND': 100.0, 'SLP': 321.0, 'TNT': 1314.0, 'RUNE': 0.03, 'NBS': 1.0, 'GHST': 9.87, 'KMD': 0.002, 'DOT': 0.72, 'IQ': 50.0, 'CMT': 1.0, 'IDEX': 182.0, '1INCH': 5.09, 'XRPBULL': 0.076, 'AVAX': 0.01, 'MITH': 480.0, 'ERD': 1000.0, 'CND': 657.0, 'UNFI': 1.06, 'UAH': 0.0, 'FTM': 351.0, 'POWR': 56.0, 'KNC': 7.32, 'GVT': 3.91, 'WINGS': 20.0, 'PROM': 2.51, 'FTT': 1.0, 'CHAT': 100.0, 'RLC': 7.93, 'BGBP': 2.81, 'ATOM': 0.005, 'BLZ': 91.0, 'HIVE': 0.01, 'SNM': 635.0, 'MBL': 15.0, 'SNT': 189.0, 'SNX': 0.71, 'FUN': 895.0, 'SNGLS': 1037.0, 'COS': 788.0, 'USD': 0.0, 'QKC': 1095.0, 'ROSE': 0.1, 'DAI': 5.74, 'SOL': 0.01, 'FET': 108.0, 'ETF': 1.0, 'ETHBULL': 0.0, 'BNB': 0.0, 'CELR': 1231.0, 'OGN': 48.0, 'ETH': 0.005, 'MCO': 1.41, 'NEO': 0.0, 'LRC': 33.0, 'REPV1': 0.1, 'XZC': 0.02, 'ADXOLD': 5.0, 'MTH': 758.0, 'GXS': 0.3, 'MTL': 14.0, 'VET': 100.0, 'TRB': 0.34, 'BNT': 4.5, 'QLC': 1.0, 'USDT': 3.0, 'LBA': 10.0, 'USDS': 2.0, 'OXT': 24.0, 'MDA': 11.0, 'UTK': 47.0, 'DASH': 0.002, 'NVT': 0.1, 'SWRV': 12.0, 'EOSBEAR': 0.022, 'EDO': 2.23, 'HEGIC': 48.0, 'GHS': 0.0, 'AMB': 447.0, 'WBNB': 0.002, 'FUEL': 564.0, 'DREP': 1516.0, 'TRY': 0.0, 'TRX': 216.0, 'MDT': 262.0, 'MDX': 100.0, 'HKD': 0.0, 'AERGO': 125.0, 'EUR': 0.0, 'LSK': 0.1, 'BOT': 0.011, 'CAD': 0.0, 'NULS': 0.01, 'BEAR': 0.0, 'BEAM': 0.1, 'CAN': 5.0, 'DCR': 0.01, 'NGN': 0.0, 'CREAM': 0.086, 'DATA': 152.0, 'ENTRP':10.0, 'USDC': 5.77, 'ANTOLD': 1.0, 'WIN': 457.0, 'BNBBULL': 0.012, 'INJ': 1.45, 'TCT': 679.0, 'HNST': 10.0, 'CRV': 10.0, 'EVX': 20.0, 'LTO': 44.0, 'BAKE': 4.98, 'ANT': 1.83, 'NXS': 0.02, 'INR': 0.0, 'CBK': 1.2, 'SRM': 5.29, 'CBM': 200.0, 'INS': 52.0, 'JPY': 0.0, 'PLN': 0.0, 'ETHBEAR': 0.0, 'OG': 0.012, 'XLM': 0.01, 'LINK': 0.5, 'MFT': 2197.0, 'QTUM': 0.01, 'LUN': 1.54, 'KSM': 0.01, 'BETH': 0.0075, 'BQX': 36.0, 'FIL': 0.26, 'POLY': 61.0, 'STMX': 2463.0, 'BAL': 0.42, 'FIO': 5.0, 'VIB': 312.0, 'VIA': 0.01, 'BRD': 94.0, 'BAT': 28.0, 'VRAB': 300.0, 'AKRO': 615.0, 'NZD': 0.0, 'BUSD': 3.0, 'ARPA': 255.0, 'XMR': 0.0001, 'BRL': 0.0, 'COTI': 128.0}
    while True:
        min_profit = 1
        pairs_all=[]
        try:
            pairs_all.append(get_binance_pairs())    
            pairs_all.append(get_bitmax_pairs())    
            pairs_all.append(get_huobi_pairs())
            pairs_all.append(get_pol_pairs())
            pairs_all.append(get_gate_pairs())
            pairs_all.append(get_hoo_pairs())
            #gate_fee = get_gate_fee()  
            #gate_fee={}
        except:
            continue
        # DELETE COINS---------------
        for i in range(len(exchangeNames)): 
            #pairs_new[i]=[] 
            for key in pairs_all[i]:
                del_status = False
                if delete_coins[i] != []:
                    for de_coin in delete_coins[i]:
                        #print(de_coin)
                        if de_coin in key:
                            del_status = True
                            break
                    if del_status:
                        pass
                    else:
                        pairs_new[i].append(key)
                else:
                    pairs_new[i].append(key)       
                        #print(exchangeNames[i], key)
        #---------------------------------------
        for i in range(len(exchangeNames)):    
            if i == 0:  #change
                for j in range(len(exchangeNames)):
                    if j>i :
                        com_pairs = set(pairs_new[i]) & set (pairs_new[j])
                        #print(com_pairs)
                        print('\n',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),exchangeNames[i],'---',exchangeNames[j],'Start Checking!','\n')
                        n = ''
                        p = 0
                        #print(com_pairs)
                        if com_pairs !=[]:
                            for s in com_pairs:
                                #deposit = get_hoo_wallet(s.split('/')[0])
                                #print(deposit)
                                try:
                                    #print(s)
                                    a_bid_price=[]
                                    a_bid_vol=[]
                                    a_ask_price=[]
                                    a_ask_vol=[]
                                    b_bid_price=[]
                                    b_bid_vol=[]
                                    b_ask_price=[]
                                    b_ask_vol=[]
                                    min_vol=0
                                    profit =0
                                    a_bid_real=0
                                    a_ask_real=0
                                    b_bid_real=0
                                    b_ask_real=0
                                    #try:
                                    if exchangeNames[i]=='Binance':
                                        a = get_binance_data(s)
                                    elif exchangeNames[i]=='GateIO':
                                        a = get_gate_data(s)
                                    elif exchangeNames[i]=='Bitmax':
                                        a = get_bitmax_data(s)
                                    elif exchangeNames[i]=='Hoo':
                                        a = get_hoo_data(s)
                                    elif exchangeNames[i]=='Pwang':
                                        a = get_pol_data(s) 
                                    elif exchangeNames[i]=='Huobi':
                                        a = get_huobi_data(s)                              
                                    else:
                                        pass

                                    if exchangeNames[j]=='Binance':
                                        b = get_binance_data(s)
                                    elif exchangeNames[j]=='GateIO':
                                        b = get_gate_data(s)
                                    elif exchangeNames[j]=='Bitmax':
                                        b = get_bitmax_data(s)
                                    elif exchangeNames[j]=='Hoo':
                                        b = get_hoo_data(s)
                                    elif exchangeNames[j]=='Pwang':
                                        b = get_pol_data(s)    
                                    elif exchangeNames[j]=='Huobi':
                                        b = get_huobi_data(s)                             
                                    else:
                                        pass
                                    if a[0] !=[] and a[1] !=[] and b[0] !=[] and b[1] !=[]:
                                        #print(a)
                                        #print(b)
                                        a_bid_price.append(float(a[0][0][0]))
                                        a_bid_vol.append(float(a[0][0][1]))
                                        a_ask_price.append(float(a[1][0][0]))
                                        a_ask_vol.append(float(a[1][0][1]))
                                        b_bid_price.append(float(b[0][0][0]))
                                        b_bid_vol.append(float(b[0][0][1]))
                                        b_ask_price.append(float(b[1][0][0]))
                                        b_ask_vol.append(float(b[1][0][1]))
                                        temp_ask_price=[]

                                        for t in range(10):
                                            if b_bid_price[-1]/a_ask_price[-1] > 1:
                                                #print('option-1')                                        
                                                if sum(a_ask_vol) > sum(b_bid_vol):
                                                    #print('option-1-1') 
                                                    #print(b_bid_vol,a_ask_vol)
                                                    min_vol = sum(b_bid_vol)
                                                    if len(a_ask_vol)>1:
                                                        a_ask_vol[-1] = min_vol-sum(a_ask_vol[0:-1])
                                                        if a_ask_vol[-1] < 0:
                                                            a_ask_vol[-2] = a_ask_vol[-2] + a_ask_vol[-1]
                                                            del a_ask_vol[-1]
                                                            break
                                                    else:
                                                        a_ask_vol[0] = min_vol
                                                    b_bid_real = sum(map(lambda x,y: x * y, b_bid_price,b_bid_vol))
                                                    a_ask_real = sum(map(lambda x,y: x * y, a_ask_price,a_ask_vol))
                                                    if b_bid_real-a_ask_real > profit:
                                                        profit = b_bid_real-a_ask_real
                                                        #print(s,'Profit: ',profit,'$')
                                                        b_bid_price.append(float(b[0][t+1][0]))
                                                        b_bid_vol.append(float(b[0][t+1][1]))
                                                        if len(a_ask_vol)>1:  #change back
                                                            a_ask_vol[-1] = float(a[1][len(a_ask_vol)-1][1])
                                                        else:
                                                            a_ask_vol[0] = float(a[1][0][1])
                                                        #print(b_bid_vol,a_ask_vol)
                                                    elif  b_bid_real-a_ask_real < profit:
                                                        break                                    
                                                
                                                elif  sum(a_ask_vol) < sum(b_bid_vol):
                                                    #print('option-1-2')
                                                    #print(b_bid_vol,a_ask_vol)
                                                    min_vol =  sum(a_ask_vol)
                                                    if len(b_bid_vol)>1:
                                                        b_bid_vol[-1] = min_vol-sum(b_bid_vol[0:-1])
                                                        if b_bid_vol[-1]<0:
                                                            b_bid_vol[-2] = b_bid_vol[-2] + b_bid_vol[-1]
                                                            del b_bid_vol[-1]
                                                            break                                            
                                                    else:
                                                        b_bid_vol[0] = min_vol                                            
                                                    b_bid_real = sum(map(lambda x,y: x * y, b_bid_price,b_bid_vol))
                                                    a_ask_real = sum(map(lambda x,y: x * y, a_ask_price,a_ask_vol))
                                                    if b_bid_real-a_ask_real > profit:
                                                        profit = b_bid_real-a_ask_real
                                                        #print(s,'Profit: ',profit,'$')
                                                        a_ask_price.append(float(a[1][t+1][0]))
                                                        a_ask_vol.append(float(a[1][t+1][1]))
                                                        if len(b_bid_vol)>1:
                                                            b_bid_vol[-1] = float(b[0][len(b_bid_vol)-1][1])
                                                        else:
                                                            b_bid_vol[0] = float(b[0][0][1])  
                                                        #print(b_bid_vol,a_ask_vol)
                                                    elif  b_bid_real-a_ask_real < profit:
                                                        break                                          
                                                '''
                                                if profit > min_profit and b_bid_price[0]/a_ask_price[0] > 1.01:
                                                    print('-'*60)
                                                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$')
                                                    print('S1: ',b_bid_price[0],'B1: ',a_ask_price[0],'Qty: ',min_vol)
                                                    print('Price: ',b_bid_price,a_ask_price,'|','Vol: ',b_bid_vol,a_ask_vol)
                                                    print('-'*60)
                                                    #break                                       
                                                '''
                                            elif a_bid_price[-1]/b_ask_price[-1] > 1:
                                                #print('option-2')
                                                if sum(b_ask_vol) > sum(a_bid_vol):
                                                    #print('option-2-1')
                                                    #print(a_bid_vol,b_ask_vol)
                                                    min_vol = sum(a_bid_vol)
                                                    if len(b_ask_vol)>1:
                                                        b_ask_vol[-1] = min_vol-sum(b_ask_vol[0:-1])
                                                        if b_ask_vol[-1]<0:
                                                            b_ask_vol[-2]=b_ask_vol[-2]+b_ask_vol[-1]
                                                            del b_ask_vol[-1]
                                                            break
                                                    else:
                                                        b_ask_vol[0] = min_vol
                                                    b_ask_real = sum(map(lambda x,y: x * y, b_ask_price,b_ask_vol))
                                                    a_bid_real = sum(map(lambda x,y: x * y, a_bid_price,a_bid_vol))                  
                                                    if a_bid_real-b_ask_real > profit :
                                                        profit = a_bid_real-b_ask_real
                                                        #print(s,'Profit: ',profit,'$')
                                                        a_bid_price.append(float(a[0][t+1][0]))
                                                        a_bid_vol.append(float(a[0][t+1][1]))
                                                        if len(b_ask_vol)>1:
                                                            b_ask_vol[-1] = float(b[1][len(b_ask_vol)-1][1])
                                                        else:
                                                            b_ask_vol[0] = float(b[1][0][1])
                                                        #print(a_bid_vol,b_ask_vol)
                                                    else:
                                                        break                                   
                                                elif  sum(b_ask_vol) < sum(a_bid_vol):
                                                    #print('option-2-2')
                                                    #print(a_bid_vol,b_ask_vol)
                                                    min_vol =  sum(b_ask_vol)
                                                    if len(a_bid_vol)>1:
                                                        a_bid_vol[-1] = min_vol-sum(a_bid_vol[0:-1])
                                                        if a_bid_vol[-1] < 0:
                                                            a_bid_vol[-2]=a_bid_vol[-2]+a_bid_vol[-1]
                                                            del a_bid_vol[-1]
                                                            break
                                                    else:
                                                        a_bid_vol[0] = min_vol                        
                                                    b_ask_real = sum(map(lambda x,y: x * y, b_ask_price,b_ask_vol))
                                                    a_bid_real = sum(map(lambda x,y: x * y, a_bid_price,a_bid_vol))                  
                                                    if a_bid_real-b_ask_real > profit :
                                                        profit = a_bid_real-b_ask_real
                                                        #print(s,'Profit: ',profit,'$')
                                                        b_ask_price.append(float(b[1][t+1][0]))
                                                        b_ask_vol.append(float(b[1][t+1][1]))
                                                        if len(a_bid_vol)>1:
                                                            a_bid_vol[-1] = float(a[0][len(a_bid_vol)-1][1])
                                                        else:
                                                            a_bid_vol[0] = float(a[0][0][1])  
                                                        #print(a_bid_vol,b_ask_vol)
                                                    else:
                                                        break  
                                                '''
                                                if profit > min_profit and a_bid_price[0]/b_ask_price[0] > 1.01:
                                                    print('-'*60)
                                                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[i],'-->',exchangeNames[j],'|',s,'|',format(a_bid_real-b_ask_real,'.1f'),'$')
                                                    print('S1: ',a_bid_price[0],'B1: ',b_ask_price[0],'Qty: ',min_vol)
                                                    print('Price: ',a_bid_price,b_ask_price,'|','Vol: ',a_bid_vol,b_ask_vol)
                                                    print('-'*60)
                                                    #break 
                                                '''
                                            else:
                                                break
                                    else:
                                        continue #if [] next pair            
                                    #print(s,profit)
                                    if b_bid_price[0]/a_ask_price[0] > 1.01 and b_bid_price[0]/a_ask_price[0] < 10 and profit >10:
                                        '''
                                        print('-'*60)
                                        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$')
                                        print('S1: ',b_bid_price[0],'B1: ',a_ask_price[0],'Qty: ',min_vol)
                                        print('Price: ',b_bid_price,a_ask_price,'|','Vol: ',b_bid_vol,a_ask_vol)
                                        print('-'*60)
                                        '''
                                        try:
                                            deposit=0
                                            if exchangeNames[i]=='Binance':
                                                f = get_binance_fee[s.split('/')[0]]
                                            elif exchangeNames[i]=='GateIO':
                                                f = get_gate_fee[s.split('/')[0]]
                                                #f = gate_fee[s.split('/')[0]]['withdraw_fix']
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_gate_wallet(s.split('/')[0])
                                            elif exchangeNames[i]=='Bitmax':
                                                f = get_bitmax_fee(s)
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_bitmax_wallet(s.split('/')[0])
                                            elif exchangeNames[i]=='Hoo':
                                                f = get_hoo_fee[s.split('/')[0]]
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_hoo_wallet(s.split('/')[0])
                                                #print(deposit)
                                            elif exchangeNames[i]=='Pwang':
                                                f = get_pol_fee(s) 
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_poloniex_wallet(s.split('/')[0])
                                            elif exchangeNames[i]=='Huobi':
                                                f = get_huobi_fee(s)
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_huobi_wallet(s.split('/')[0])                             
                                            else:
                                                pass
                                        except:
                                            f =0
                                            deposit=0
                                        #print(s,'fee:',f,exchangeNames[i])
                                        if profit-f*a_ask_price[0]>10:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[j])+'====>'+str(exchangeNames[i])+'\n'+s+' || '+str(format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(b_bid_real-a_ask_real,'.1f'))+'$'+'\n'+'='*20+'\n'+'|| RP: '+str(format(profit-f*a_ask_price[0],'.1f'))+'$'+' || Fee: '+str(f)+' '+str(s.split('/')[0])+'\n'
                                            Msg3='-'*40+'\n'+'Sell1: '+str(b_bid_price[0])+'\n'+'Buy1: '+str(a_ask_price[0])+'\n'+'Qty: '+str(min_vol+f)+'\n'+'Wallet: '+str(deposit)+'\n'+'USDT: '+str(format(a_ask_price[0]*min_vol,'.1f'))+'\n'
                                            Msg4='-'*40+'\n'+'Price: '+'\n'+str(b_bid_price)+'\n'+str(a_ask_price)+'\n'
                                            Msg5='Vol: '+'\n'+str(b_bid_vol)+'\n'+str(a_ask_vol)
                                            Msg=Msg1+Msg2+Msg3+Msg4+Msg5                                        
                                            print(Msg)
                                            url = 'https://api.telegram.org/bot1416495682:AAHApsU56yr5Xvd4S9sjhGWgJQkYV9ErAVI/sendMessage?chat_id=-1001320208517&text='+Msg
                                            data = requests.get(url, headers={
                                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()

                                    #else:
                                        #print('-'*40)
                                        #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$','|','No depth!')
                                        #print(b_bid_price,b_bid_vol,'|',a_ask_price,a_ask_vol)
                                        #break                                        
                                    elif a_bid_price[0]/b_ask_price[0] > 1.01 and a_bid_price[0]/b_ask_price[0] <10 and profit >10:

                                        '''
                                        print('-'*60)
                                        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[i],'-->',exchangeNames[j],'|',s,'|',format(a_bid_real-b_ask_real,'.1f'),'$')
                                        print('S1: ',a_bid_price[0],'B1: ',b_ask_price[0],'Qty: ',min_vol)
                                        print('Price: ',a_bid_price,b_ask_price,'|','Vol: ',a_bid_vol,b_ask_vol)
                                        print('-'*60)
                                        '''
                                        try:
                                            deposit=0
                                            if exchangeNames[j]=='Binance':
                                                f = get_binance_fee[s.split('/')[0]]
                                            elif exchangeNames[j]=='GateIO':
                                                f = get_gate_fee[s.split('/')[0]]
                                                #f = gate_fee[s.split('/')[0]]['withdraw_fix']
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_gate_wallet(s.split('/')[0])
                                            elif exchangeNames[j]=='Bitmax':
                                                f = get_bitmax_fee(s)
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_bitmax_wallet(s.split('/')[0])
                                            elif exchangeNames[j]=='Hoo':
                                                f = f = get_hoo_fee[s.split('/')[0]]
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_hoo_wallet(s.split('/')[0])
                                                #print(deposit)
                                            elif exchangeNames[j]=='Pwang':
                                                f = get_pol_fee(s)
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_poloniex_wallet(s.split('/')[0])
                                            elif exchangeNames[j]=='Huobi':
                                                f = get_huobi_fee(s)
                                                if profit-f*a_ask_price[0]>10:
                                                    deposit = get_huobi_wallet(s.split('/')[0])                                  
                                            else:
                                                pass
                                        except:
                                            f =0
                                            deposit=0
                                        #print(s,'fee:',f,exchangeNames[j])
                                        if profit-f*b_ask_price[0]>10:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[i])+'====>'+str(exchangeNames[j])+'\n'+s+' || '+str(format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(a_bid_real-b_ask_real,'.1f'))+'$'+'\n'+'='*20+'\n'+'|| RP: '+str(format(profit-f*b_ask_price[0],'.1f'))+'$'+' || Fee: '+str(f)+' '+str(s.split('/')[0])+'\n'
                                            Msg3='-'*40+'\n'+'Sell1: '+str(a_bid_price[0])+'\n'+'Buy1: '+str(b_ask_price[0])+'\n'+'Qty: '+str(min_vol+f)+'\n'+'Wallet: '+str(deposit)+'\n'+'USDT: '+str(format(b_ask_price[0]*min_vol,'.1f'))+'\n'
                                            Msg4='-'*40+'\n'+'Price:'+'\n'+str(a_bid_price)+'\n'+str(b_ask_price)+'\n'
                                            Msg5='Vol:'+'\n'+str(a_bid_vol)+'\n'+str(b_ask_vol)
                                            Msg=Msg1+Msg2+Msg3+Msg4+Msg5                                        
                                            print(Msg)
                                            url = 'https://api.telegram.org/bot1416495682:AAHApsU56yr5Xvd4S9sjhGWgJQkYV9ErAVI/sendMessage?chat_id=-1001320208517&text='+Msg
                                            data = requests.get(url, headers={
                                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()

                                    else:
                                        pass
                                        #print('-'*40)
                                        #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[i],'-->',exchangeNames[j],'|',s,'|',format(a_bid_real-b_ask_real,'.1f'),'$','|','No depth!' ) 
                                        #print(a_bid_price,a_bid_vol,'|',b_ask_price,b_ask_vol) 
                                        #break
                                    
                                    time.sleep(random.uniform(0.5, 1))                        
                                    p += 1
                                    n = '#' *int(p/len(com_pairs)*40)
                                    sys.stdout.write(str(int((p/((len(com_pairs)))*100)))+'% ('+str(p)+'/'+str(len(com_pairs))+') ||'+n+'->'+"\r")
                                    sys.stdout.flush()
                                except:
                                    pass