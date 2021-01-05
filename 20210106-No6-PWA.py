# -*- coding: utf-8 -*-
#20210106-update the gateio withdraw fee
import requests
import time
import random
import sys
import hmac
import hashlib
import json
import http.client
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

def get_gate_fee():
    url= 'data.gateapi.io'
    URL = "/api2/1/private/feelist"
    apiKey = 'EDF07FEF-02E9-4E5A-B171-B2A9A7E48207'
    secretKey = '059e9f6cfad083e092446325377b02570fb92d59e33006719c57d6d43b4f1572'
    params = {}
    fee={}
    try:
        fee = httpPost(url, URL, params, apiKey, secretKey)
        print('Get Gate fee sucessfully!')
    except:
        fee={}    
    return eval(fee)

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
    pairs_new =[[] for i in exchangeNames]
    delete_coins=[['ETC'],[],['HOT','3L','3S','ETC'],['MPH','ETC','COVER','SWINGBY','OM'],['RAMP','COVER','CET','ETC','BCHA'],['COVER','BOND','AGS','ATP','CET','ETC','OM','BAS']]
    #get_gate_fee = {'MIS':0.0041,'BTC': 0.0005, 'BCH': 0.0005, 'ETH': 0.005, 'ETC': 0.01, 'QTUM': 0.01, 'LTC': 0.001, 'DASH': 0.002, 'ZEC':0.001, 'BTM': 5.0, 'EOS': 0.1, 'REQ': 89.0, 'SNT': 96.0, 'OMG': 1.1, 'PAY': 51.0, 'CVC': 34.0, 'ZRX': 10.0, 'TNT': 680.0, 'XMR': 0.001, 'XRP': 0.1, 'DOGE': 20.0, 'BAT': 14.0, 'PST': 200.0, 'BTG': 0.002, 'DPY': 530.0, 'LRC': 19.0, 'STORJ': 9.9, 'RDN': 18.0, 'KNC': 3.7, 'LINK': 0.3, 'CDT': 430.0, 'AE': 1.0, 'RLC': 3.6, 'RCN': 78.0, 'TRX': 5.0, 'VET': 100.0, 'MCO': 5.0, 'FUN': 800.0, 'DATA': 70.0, 'ZSC': 23000.0, 'MDA': 5.3, 'XTZ': 0.1, 'GEM': 19000.0, 'RFR': 860.0, 'ABT': 44.0, 'OST': 220.0, 'XLM': 0.01, 'MOBI': 1.0, 'OCN': 12000.0, 'COFI': 2900.0, 'JNT': 270.0, 'BLZ': 41.0, 'GXS': 1.0, 'MTN': 1700.0, 'RUFF': 550.0, 'TNC': 10.0, 'ZIL': 10.0, 'BTO': 10.0, 'THETA': 10.0, 'DDD': 1500.0, 'MKR': 0.0052, 'DAI': 3.0, 'SMT': 50.0, 'MDT': 120.0, 'MANA': 50.0, 'LUN': 1.2, 'SALT': 9.9, 'FUEL': 13000.0, 'ELF': 28.0, 'DRGN': 66.0, 'GTC': 610.0, 'QLC': 10.0, 'DBC': 10.0, 'BNTY': 42, 'ICX': 0.2, 'BTF': 0.1, 'ADA': 1.0, 'LSK': 0.1, 'WAVES': 0.1, 'BIFI': 0.2, 'MDS': 1200.0, 'QASH': 95.0, 'POWR': 30.0, 'BCD': 0.02, 'SBTC': 0.05, 'GOD': 0.1, 'BCX': 30.0, 'QSP': 100.0, 'INK': 0.3, 'QBT': 5.0, 'TSL': 10.0, 'GNX': 320.0, 'NEO': 0.0, 'GAS':0.02, 'IOTA': 0.1, 'NAS': 0.5, 'OAX': 34.0, 'BCDN': 2100.0, 'SNET': 1100.0, 'BTS': 1.0, 'USDG': 4.0, 'GT': 610.0, 'ATOM': 0.01, 'ETH2': 0.005, 'HARD': 0.01, 'KAVA': 0.01, 'IRIS': 5.0, 'ANT': 0.99, 'ANKR': 340.0, 'STPT': 170.0, 'RSR': 170.0, 'RSV': 3.0, 'KAI': 120.0, 'CTSI': 65.0, 'COMP': 0.022, 'OCEAN': 8.8, 'KSM': 0.05, 'FIRO': 0.5, 'DOT': 0.1, 'MTR': 1.0, 'MTRG': 2.0, 'SOL': 0.01, 'COTI': 60.0, 'AMPL': 3.1, 'WNXM': 0.17, 'LUNA': 5.0, 'AVAX': 0.1, 'BZRX': 18.0, 'PCX': 0.2, 'YAMV2': 0.67, 'YAM': 500.0, 'BOX': 0.1, 'CRV': 6.1, 'UNI': 2.0, 'SUSHI': 1.1, 'AAVE': 0.037, 'POLS': 8.0, 'ERG': 2.0, 'GOF': 7.2, 'PHA': 34.0, 'SASHIMI': 96.0, 'FARM': 0.031, 'SWRV': 7.0, 'BOT': 0.01, 'ULU': 0.55, 'OIN': 12000.0, 'AGS': 39.0, 'ADEL': 13.0, 'TON': 260.0, 'KIMCHI': 100.0, 'KTON': 0.046, 'RING': 84.0, 'MINI': 98.0, 'CREAM': 0.05, 'JGN': 39.0, 'DEGO': 5.9, 'RFUEL': 78.0, 'SFG': 6.8, 'NEST': 140.0, 'CORE': 0.00097, 'NEAR': 3.0, 'NU': 18.0, 'STAKE': 0.34, 'ARNX': 680.0, 'TRU': 23.0, 'ROSE': 10.0, 'BADGER': 0.5,'COVER': 0.0035, 'GLM': 26.0, 'BASE': 5.6, 'PICKLE': 0.3, 'HEGIC': 26.0, 'GTH': 100.0, 'DUSK': 61.0, '88MPH': 0.091, 'UNFI': 0.43, 'FLM': 10.0, 'GHST': 4.9, 'ACH': 120.0, 'DUCK': 110.0, 'GRT': 20.0, 'ESD': 3.3, 'ALEPH': 19.0, 'FRAX': 3.1, 'FXS': 0.81,'BOR': 0.013, 'ROOK': 0.03, 'BAC': 2.9, 'BAS': 5.6, 'LON': 12.0, 'MAHA': 0.32, 'WOZX': 2.2, 'FAR': 0.031, 'POND': 75.0, '1INCH': 2.7, 'DSD': 5.7, 'OCTO': 0.11, 'SHARE': 0.81, 'LINA': 280.0, 'WHITE': 0.002, 'WOM': 16.0, 'API3': 1.4, 'FIN': 5.9, 'SKL': 33.0, 'PRQ': 13.0, 'FRONT': 11.0, 'INJ': 1.3, 'ALPA': 32.0, 'ROOBEE': 1500.0, 'NSURE': 5.5, 'KP3R': 0.01, 'WOO': 100.0, 'HYVE': 280.0, 'KFC': 0.27, 'RAMP': 300.0, 'SYLO': 3500.0, 'RARI': 1.3, 'DVP': 80.0, 'MPH': 0.091, 'DF': 23.0, 'CVP': 1.4, 'VALUE': 0.1, 'UMA': 0.4, 'YFII': 0.0021, 'SWAP': 2.0, 'SXP': 4.4, 'BAL': 0.21, 'BAND': 0.54, 'AST': 8.0, 'TROY': 1100.0, 'OM': 1.1, 'SPA': 220.0, 'AKRO': 13.0, 'FOR': 3.1, 'CREDIT': 170.0, 'DIA': 20.0, 'AXIS': 8.2, 'TRB': 0.17, 'LIEN': 0.089, 'PEARL': 0.001, 'CORN': 0.017, 'SLM': 0.11, 'SAL': 9.9, 'TAI': 37.0, 'CRT': 1.3, 'JFI': 0.0012, 'MTA': 3.0, 'YFI': 0.0021, 'KIN': 10000.0, 'DKA': 130.0, 'REN': 5.5, 'DOS': 50.0, 'SUTER': 820.0, 'SRM': 2.9, 'JST': 9.9, 'LBK': 430.0, 'BTMX': 82.0, 'WEST': 1.0, 'XEM': 5.0, 'BU': 0.1, 'HNS': 1.0, 'BTC3L': 1.0, 'BTC3S': 1.0, 'LINK3L': 1.0, 'LINK3S': 1.0, 'SOL3L': 1.0, 'SOL3S': 1.0, 'SKL3L': 1.0, 'SKL3S': 1.0, '1INCH3L': 1.0, '1INCH3S': 1.0, 'LON3L': 1.0, 'LON3S': 1.0, 'DOGE3L': 1.0, 'DOGE3S': 1.0, 'GRT3L': 1.0, 'GRT3S': 1.0, 'BNB3L': 1.0, 'BNB3S': 1.0, 'TRX3L': 1.0, 'TRX3S': 1.0, 'ATOM3L': 1.0, 'ATOM3S': 1.0, 'AVAX3L': 1.0, 'AVAX3S': 1.0, 'NEAR3L': 1.0, 'NEAR3S': 1.0, 'ROSE3L': 1.0, 'ROSE3S': 1.0, 'ZEN3L': 1.0, 'ZEN3S': 1.0, 'QTUM3L': 1.0, 'QTUM3S': 1.0, 'XLM3L': 1.0,'XLM3S': 1.0, 'XRP3L': 1.0, 'XRP3S': 1.0, 'CFX3L': 1.0, 'CFX3S': 1.0, 'BCHA3L': 1.0, 'BCHA3S': 1.0, 'OMG3L': 1.0, 'OMG3S': 1.0, 'ALGO3L': 1.0, 'ALGO3S': 1.0, 'WAVES3L': 1.0, 'WAVES3S': 1.0, 'NEO3L': 1.0, 'NEO3S': 1.0, 'ONT3L': 1.0, 'ONT3S': 1.0, 'ETC3L': 1.0, 'ETC3S': 1.0, 'CVC3L': 1.0, 'CVC3S': 1.0, 'SNX3L': 1.0, 'SNX3S': 1.0, 'ADA3L': 1.0, 'ADA3S': 1.0, 'DASH3L': 1.0, 'DASH3S': 1.0, 'AAVE3L': 1.0, 'AAVE3S': 1.0, 'SRM3L': 1.0, 'SRM3S': 1.0, 'KSM3L': 1.0, 'KSM3S': 1.0, 'BTM3L': 1.0, 'BTM3S': 1.0, 'ZEC3L': 1.0, 'ZEC3S': 1.0, 'XMR3L': 1.0, 'XMR3S': 1.0, 'AMPL3L': 1.0, 'AMPL3S': 1.0, 'CRV3L': 1.0, 'CRV3S': 1.0, 'COMP3L': 1.0, 'COMP3S': 1.0, 'YFII3L': 1.0, 'YFII3S': 1.0, 'YFI3L': 1.0, 'YFI3S': 1.0, 'HT3L': 1.0, 'HT3S': 1.0, 'OKB3L': 1.0, 'OKB3S': 1.0, 'UNI3L': 1.0, 'UNI3S': 1.0, 'DOT3L': 1.0, 'DOT3S': 1.0, 'FIL3L': 1.0, 'FIL3S': 1.0, 'SUSHI3L': 1.0, 'SUSHI3S': 1.0, 'ETH3L': 1.0, 'ETH3S': 1.0, 'EOS3L': 1.0, 'EOS3S': 1.0, 'BSV3L': 1.0, 'BSV3S': 1.0, 'BCH3L': 1.0, 'BCH3S': 1.0, 'LTC3L': 1.0, 'LTC3S': 1.0, 'XTZ3L': 1.0, 'XTZ3S': 1.0, 'BCHSV': 0.0005, 'RVN': 5.0, 'RVC': 6.1, 'AR': 320.0, 'DCR': 0.02, 'BCN': 10.0, 'XMC': 0.05, 'NBS': 100.0, 'STEEM': 1.0, 'HIVE': 1.0, 'COCOS': 10.0, 'BCHA': 1.0, 'ATP': 0.5, 'NAX': 0.5, 'KLAY': 1.0, 'NBOT': 110.0, 'MED': 100.0, 'GRIN': 0.1, 'BEAM': 0.1, 'HBAR': 0.1, 'OKB': 1.0, 'REP': 0.19, 'STAR': 8.0, 'ZEN': 1.0, 'ABBC': 10.0, 'FIL': 1.0, 'FIC': 2900.0, 'FIL6': 0.1, 'SUP': 0.01, 'STOX': 42, 'VTHO': 50.0, 'VIDYX': 20.0, 'BTT': 330.0, 'TFUEL': 10.0, 'CELR': 600.0, 'CS': 10.0, 'MAN': 50.0, 'REM': 1400.0, 'LYM': 950.0, 'ZPT': 10.0, 'ONG': 0.1, 'WING': 83.0, 'ONT': 1.0, 'BFT': 350.0, 'IHT': 5500.0, 'SENC': 2800.0, 'TOMO': 1.0, 'ELEC': 3900.0, 'SNX': 1.0, 'SWTH': 5.0, 'NKN': 5.0, 'SOUL': 5.0, 'LRN': 5.0, 'EOSDAC': 20.0, 'DOCK': 170.0, 'GSE': 110000.0, 'RATING': 25000.0, 'HSC': 150000.0, 'HIT': 0.002, 'DX': 2400.0, 'CNNS': 1100.0, 'DREP': 680.0, 'MBL': 10.0, 'GMAT': 11000.0, 'MIX': 1500.0, 'LAMB': 210.0, 'LEO': 2.2, 'BTCBULL': 0.0001, 'BTCBEAR': 100.0, 'ETHBEAR': 670.0, 'ETHBULL': 0.002, 'EOSBULL': 5.3, 'EOSBEAR': 3.8, 'XRPBEAR': 2.3, 'XRPBULL': 1.6, 'WICC': 2.0, 'WGRT': 100.0, 'SERO': 5.0, 'CORAL': 2.0, 'VIDY': 20.0, 'KGC': 22000.0, 'FTM': 180.0, 'RUNE': 2.0, 'COS': 0.01, 'CBK': 1.0, 'CHZ': 120.0, 'TWT': 1.0, 'AVA': 0.01, 'CRO': 52.0, 'ALY': 8200.0, 'WIN': 83.0, 'SUN': 0.016, 'MTV': 7900.0, 'ONE': 20.0, 'ARPA': 140.0, 'DILI': 12000.0, 'ALGO': 1.0, 'PI': 10.0, 'CKB': 1.0, 'BKC': 1.0, 'BXC': 14000.0, 'PAX': 3.0, 'USDC': 3.0, 'TUSD': 3.0, 'HC': 0.2, 'GARD': 100.0, 'CELO': 0.5, 'CFX': 1.0, 'FTI': 10000.0, 'SOP': 91000.0, 'LEMO': 3700.0, 'QKC': 20.0, 'IOTX': 20.0, 'RED': 170.0, 'LBA': 0.21, 'OPEN': 4000.0, 'MITH': 180.0, 'SKM': 1600.0, 'XVG': 20.0, 'NANO': 20.0, 'HT': 170.0, 'BNB': 1.0, 'MET': 1.0, 'TCT': 310.0, 'MXC': 270.0}
    get_hoo_fee = {'EOS': 0.1, 'BTC': 0.0005, 'ETH': 0.007, 'HC': 0.5, 'DASH': 0.02, 'NEO': 0.0, 'QTUM': 0.1, 'VET': 100.0, 'XRP': 0.1, 'DOGE':50.0, 'XMR': 0.01, 'BTM': 10.0, 'DCR': 0.01, 'HT': 0.8, 'PUB': 0.0, 'TPT': 100.0, 'RBF': 2.39391625, 'KAN': 900.0, 'BNB': 0.001, 'OMG': 1.5, 'ZRX': 10.0, 'ZIL': 0.1, 'DLB': 20.0, 'AE': 10.0, 'AION': 94.0, 'AMB': 499.0, 'AOA': 700.0, 'ATX': 4031.20482777, 'AUTO': 3625.30649559, 'BAT': 5.0, 'BIX': 11.53565654, 'BLZ': 50.0, 'BNT': 5.0, 'BRD': 13.7355291, 'CENNZ': 50.0, 'CMT': 122.73254237, 'CTXC': 12.93088277, 'CVC': 70.0, 'CVT': 40.0, 'DRGN': 68.52871512, 'FSN': 1.0, 'FUN': 1000.0, 'FXT': 1958.87870481, 'GNO': 0.06, 'GNT': 25.26006977, 'HOT': 2000.0, 'IOST': 5.0, 'KNC': 4.0, 'LINK': 0.5, 'LRC': 20.0, 'MANA': 24.01449913, 'MCO': 0.3, 'MKR': 0.008, 'NAS': 2.0, 'NEC': 7.0, 'NEXO': 20.0, 'PAY': 21.38080805, 'QKC': 1.0, 'SNT': 200.0, 'SOC': 311.67374462, 'STORJ': 13.0, 'AISA': 100.0, 'DCC': 1000.0, 'EOSRAM': 100.0, 'HVT': 0.0, 'EBTC': 0.0, 'EETH': 0.0, 'IHT': 937.03953101, 'VNS': 1000.0, 'DICE': 0.0, 'EKT': 1000.0, 'SPC': 1235.37086057, 'CHAT': 612.88362251, 'HPY': 2.0, 'MAX': 0.0, 'OCT': 0.0, 'RIDL': 0.0, 'BLACK': 0.0, 'ECTT': 0.0, 'TOOK': 0.0, 'SEED': 0.0, 'PGL': 0.0, 'TOS': 817.10132117, 'UGAS': 10.0, 'MXC': 591.90921228, 'ZIP': 8720.90229578, 'PAI': 90.0, 'HX': 0.1, 'PAX': 4.0, 'PIN': 1000.0, 'BOS': 0.1, 'TRX': 1.0, 'BTT': 150.0, 'RVN': 1.0, 'WICC': 100.0, 'UB': 0.0, 'XIN': 0.02, 'ATOM': 0.005, 'OKB': 0.6, 'GT': 5.0, 'DLX': 0.0, 'LEO': 5.0, 'BKBT': 7067.75286918, 'ENTC': 1000.0, 'ONT': 1.0, 'ARN': 0.0, 'ATD': 100.0, 'BEAN': 10.0, 'BETX': 0.0, 'BOID': 10.0, 'BRM': 0.0, 'BUFF': 0.0, 'CET': 0.0, 'CHL': 0.0, 'DRAGON': 0.0, 'EAP': 0.0, 'ECASH': 0.0, 'EMT': 0.0, 'ENB': 0.0, 'EOSABC': 0.0, 'FAST': 0.0, 'GCHIP': 0.0, 'GGS': 0.0, 'HASH': 0.0, 'HIG': 10.0, 'HORUS': 0.0, 'INF': 0.0, 'IQ': 100.0, 'JKR': 0.0, 'JOY': 0.0, 'KING': 0.0, 'LLG': 0.0, 'LUCK': 0.0, 'LYNX': 0.0, 'MEV': 0.0, 'MGT': 0.0, 'MUR': 0.0, 'NEWS': 1400.0, 'OGM': 0.0, 'OKT': 0.0, 'ONE': 0.0, 'POKER': 0.0, 'POOR': 0.0, 'PTI': 0.0, 'SENSE': 0.0, 'SKY': 0.0, 'SLAM': 10.0, 'TKC': 10.0, 'TOB': 0.0, 'TRYBE': 0.0, 'TXT': 10.0, 'UCTT': 0.0, 'VIP': 0.0, 'VOID': 0.0, 'XPC': 0.0, 'ZKS': 0.0, 'CUSE': 1000.0, 'SCEC': 1000.0, 'USE': 1000.0, 'UNC': 1000.0, 'FREC': 29355.5198973, 'FCC': 1000.0, 'EVS': 8.42585785, 'SGN': 5508.13729426, 'PIZZA': 0.0, 'KEY': 0.0, 'ARP': 1000.0, 'ALGO': 0.2, 'DNAT': 20.0, 'YEC': 0.5, 'AXE': 1.0, 'RRB': 50.0, 'GLO': 18000.0, 'CKB': 20.0, 'GDP': 1000.0, 'DILIO': 800.0, 'TC': 8700.0, 'NST':100.0, 'WICM': 0.1, 'KOC': 7.0, 'MX': 15.0, '5TH': 20.0, 'TZS': 1000.0, 'MOF': 2.5, 'SKR': 3000.0, 'ZVC': 10.5, 'GLOS': 300.0, 'TZVC': 25.0, 'STX': 50.0, 'CLC': 10.0, 'FCT': 50.0, 'PGS': 8000.0, 'FBT': 20000.0, 'KAVA': 0.2, 'RNDR': 12.0, 'HZT': 20.0, 'PROPS': 15.0, 'EIDOS': 400.0, 'KSM': 0.1, 'AIX': 10000.0, 'OGN': 20.0, 'RUTM': 0.0001, 'SIN': 5.0, 'TRB': 0.1, 'BWT': 0.0, 'OXT': 15.0, 'PYP': 0.0, 'BPT': 20.0, 'FO': 50.0, 'TFO': 100.0, 'MDU': 1.0, 'UA': 1.0, 'UCT': 0.1, 'HDAO': 50.0, 'YAS': 5.0, 'FCH': 5.0, 'TKM': 0.1, 'SVVC': 500.0, 'EXN': 5.0, 'SBC': 100.0, 'HNEO': 0.1, 'HQTUM': 10.0, 'TROY': 2000.0, 'ETF': 0.0, 'BKCM': 500.0, 'JMC': 100.0, 'KLAY': 0.5, 'TRT': 1000.0, 'SOL': 0.2, 'MASS': 1.0, 'COMP': 0.03, 'GXC': 0.5, 'HNT': 0.05, 'TWT': 10.0, 'UMA': 0.4, 'JST': 25.0, 'CELO': 0.1, 'DSG': 20.0, 'ZDN': 10.0, 'KEEP': 5.0, '2KEY': 20.0, 'MSC': 20.0, 'ANJ': 25.0, 'XIO': 10.0, 'RING': 70.0, 'ESH': 10.0, 'GTG': 1.5, 'NEST': 100.0, 'JRT': 1.0, 'RVC': 20.0, 'CDS': 2.0, 'SNX': 1.0, 'CLX': 20.0, 'ONG':1.0, 'ROR': 10.0, 'IDK': 10.0, 'TCAD': 10.0, 'TAUD': 10.0, 'RSV': 10.0, 'AR': 1.0, 'KAI': 300.0, 'LYXE': 4.0, 'OKS': 5.0, 'BHD': 0.05, 'DASV': 100.0, 'FOR': 100.0, 'DAPP': 1.0, 'REN': 20.0, 'FIL': 0.05, 'IDEX': 64.0, 'WGRT': 10.0, 'MLN': 0.15, 'CNYT':0.0, 'CDT': 166.0, 'SCS': 16.0, 'CRING': 650.0, 'STAKE': 0.2, 'DMG': 12.0, 'CEL': 1.0, 'NMR': 0.1, 'CHZ': 150.0, 'BAL': 0.3, 'JT': 30.0, 'RSR': 400.0, 'REL': 1.0, 'PNK': 64.0, 'SWTH': 15.0, 'DEXT': 90.0, 'ALEPH': 30.0, 'CAN': 10.0, 'GBT': 10.0, 'LPT':0.2, 'AUC': 5.0, 'DSF': 100.0, 'AKRO': 400.0, 'XOR': 0.025, 'AMPL': 4.0, 'STA': 10.0, 'COT': 10000.0, 'ASKO': 600.0, 'UTO': 1.2, 'MCX': 120.0, 'DAM': 5.0, 'ATTN': 30.0, 'AVA': 1.0, 'FLUX': 0.28, 'VRA': 5555.0, 'AST': 28.0, 'UCA': 10.0, 'IDRT': 15000.0, 'BIDR': 600.0, 'BKRW': 100.0, 'BZRX': 22.0, 'PLR': 70.0, 'NDX': 2565.0, 'DEC': 50.0, 'ORN': 2.0, 'MCB': 0.35, 'MTA': 2.0, 'UTK': 40.0, 'OWL': 0.01, 'WNXM': 0.28, 'RARI': 1.0, 'DFS': 0.2, 'USDD': 10.0, 'PLT': 60.0, 'MW': 2.5, 'YFI': 0.0002, 'QXGS': 1.0, 'CTAFY': 1.0, 'DXD': 0.02, 'SWINGBY': 6.0, 'MTR': 1.0, 'MTRG': 1.0, 'RPL': 3.0, 'FIO': 5.0, 'KTON': 0.03, 'DMST': 66.0, 'DEV': 0.6, 'GEN': 12.0, 'DOT': 0.1, 'DAD': 7.0, 'YFII': 0.001, 'IFT': 2000.0, 'TIFT': 10.0, 'BUIDL': 1.0, 'PUX': 285.0, 'DIA': 0.8, 'BOT': 0.01, 'FNX': 6.0, 'XFT': 2.0, 'STRONG': 0.02, 'YAM': 0.4, 'ETHV': 4.0, 'CRV': 4.0, 'TLOS': 1.0, 'BART': 100.0, 'XRT': 0.25, 'OM': 6.0, 'OGX': 2.0, 'HU': 0.01, 'CREDIT': 60.0, 'HAKKA': 6.0, 'DIP': 3.0, 'LIEN': 0.1, 'BOX': 0.25, 'DF': 26.0, 'CVP': 2.0, 'SUSHI': 3.0, 'PEARL': 0.0003, 'TAI': 0.06, 'OIN': 10.0, 'ADEL': 8.0, 'CRT': 1.0, 'SAL': 0.07, 'SWRV': 3.0, 'CREAM':0.04, 'FARM': 0.005, 'FSW': 20.0, 'ULU': 0.0125, 'DMD': 0.0025, 'ZILD': 0.04, 'UP': 5.0, 'SUN': 0.05, 'PERP': 4.0, 'GOF': 3.0, 'GTF': 5.0, 'WING': 0.01, 'ONES': 5.0, 'PICKLE': 0.2, 'HGET': 0.8, 'GHST': 20.0, 'SAFE': 0.02, 'MEME': 0.03, 'SLM': 0.01, 'HEGIC': 20.0, 'UNI': 1.0, 'FRONT': 10.0, 'LINA': 200.0, 'DHT': 5.0, 'DEGO': 20.0, 'BAND': 1000.01, 'OBEE': 2000.0, 'WHALE': 0.5, 'CRU': 1.0, 'AVAX': 0.01, 'UNII': 250.0, 'COVAL': 800.0, 'BONK': 10.0, 'ASTRO': 6.0, 'ZOM': 0.1, 'SHROOM': 20.0, 'HOO': 70.0, 'SLP': 100.0, 'ARTE': 1.0, 'SKL': 120.0, 'LAYER': 20.0, 'NFT': 30.0, 'BID': 150.0, 'RFUEL': 30.0, 'DANDY': 0.015, 'BUILD': 0.15, 'FIN': 1.0, 'YELD': 0.05, 'PGT': 0.03, 'GTH': 80.0, 'AAVE': 0.1, 'DAOFI': 40.0, 'PLOT': 20.0, 'UFT': 8.0, 'NU': 30.0, 'HEZ': 1.0, 'RAMP': 100.0, 'REVV': 160.0, 'CFS': 25.0, 'BIW': 25.0, 'RGT': 4.0, 'RAK': 0.05, 'BOND': 0.02, 'WOO': 45.0, 'KP3R': 0.02, 'BVB': 40.0, 'YF': 0.01, 'DOUGH': 5.0, 'NSURE': 10.0, 'PTERIA': 0.7, 'ROOK': 0.03, 'LTX': 10.0, 'SPKL': 5000.0, 'BCHA': 0.001, 'CFX': 1.0, 'FC': 0.1, 'DVI': 100.0, 'PRQ': 10.0, 'AC': 10.0, 'SFI': 0.0001, 'SYN': 8.0, 'INDEX': 0.5, 'FIS': 0.3, 'EXRD': 25.0, 'FYZ': 10.0, 'ANT': 1.0, 'ATRI': 100.0, 'ORAI': 0.2, 'EPAN': 20.0, 'TRU': 25.0, 'KOMET': 0.05, 'ARCH': 12.0, 'MARK': 1.5, 'AIN': 160.0, 'YFC': 0.05, 'WDP': 0.1, 'KEX': 1.0, 'FWT': 1000.0, 'CFI': 1.0, 'BUND': 1.0, 'MTS': 1.5, 'WON': 500.0, 'YFD': 0.01, 'TME': 0.01, 'GDAO': 2.0, 'CLIQ': 50.0, 'OPEN': 80.0, 'WFIL': 0.1, 'UMEX': 20.0, 'ZIN': 500.0, 'API3': 2.0, 'ZORA': 0.01, 'SWISS': 0.01, 'CRBN': 100.0, 'BIRD': 1.0, 'STV': 500.0, 'DG': 0.2, 'LOAD': 100.0, 'BETC': 0.5, 'EOC': 1.0, 'STPL': 250.0, 'BUP': 15.0, 'PSK': 50.0, 'MIXS': 25.0, 'BADGER': 0.5, 'BSC': 0.015, 'MONA': 0.005, 'ITS': 0.3, 'UCAP': 3.0, 'XCUR': 150.0, 'PPAY': 50.0, 'YFIA': 3.0, 'YLD': 0.15, 'MVEDA': 80.0, 'SKD': 0.01, 'FAR': 10.0, 'SPDR': 80.0, 'DEFO': 0.02, 'DFO': 40.0, 'GRT': 8.0, 'ANRX': 60.0, 'MAHA': 0.5, 'FXS': 0.15, 'POND': 30.0, 'LON': 3.0, 'TWT1': 1.0, 'FRM': 35.0, 'UDT': 0.7, 'DDX': 1.0, '1INCH': 5.0, 'DRIP': 50.0, 'CBK': 20.0, 'DATX': 10000.0, 'REEF': 35.0, 'WHITE': 0.002, 'ORI': 0.05, 'FIRE': 8.0, 'HYPE': 5.0, 'MIS': 0.008, 'KEK': 500.0, 'BAFI': 2.0, '3XT': 0.003}
    get_binance_fee = {'CTR': 35.0, 'MATIC': 328.0, 'STPT': 339.0, 'MXN': 0.0, 'UGX': 0.0, 'RENBTC': 0.0002, 'IOTX': 0.0, 'GLM': 53.0, 'FRONT': 20.0, 'ZAR': 0.0, 'NEAR': 0.01, 'AUDIO': 36.0, 'HNT': 0.05, 'CDT': 856.0, 'SPARTA': 0.54, 'DOCK': 334.0, 'SUSD': 5.63, 'STX': 10.0, 'PNT': 16.0, 'DENT': 29630.0, 'AION': 83.0, 'NPXS': 33334.0, 'BCPT': 294.0, 'BNBBEAR': 0.011, 'DGB': 0.2, 'VIBE': 345.0, 'ZRX': 15.0, 'SUB': 40.0, 'BCD': 0.01, 'EASY': 1.46, 'WING': 0.0016, 'POA': 307.0, 'AE': 0.1, 'WNXM': 0.25, 'IOST': 1037.0, 'BCH': 0.017, 'CAKE': 0.12, 'POE': 20000.0, 'OMG': 2.3, 'JST': 50.0, 'BAND': 1.06, 'HOT': 9855.0, 'SUN': 0.0044, 'BTC': 0.0002, 'TWT': 0.46, 'NKN': 312.0, 'RSR': 234.0, 'IRIS': 1.0, 'CVC': 67.0, 'IOTA': 0.5, 'REEF': 469.0, 'BTG': 0.001, 'BCX': 0.5, 'SEK': 0.0, 'KES': 0.0, 'ARK': 0.2, 'BTM': 5.0, 'TRIG': 50.0, 'RCN': 153.0, 'CVP': 3.23, 'ARN': 17.0, 'KEY': 2836.0, 'BTS': 1.0, 'COVER': 0.054, 'BTT': 91.0, 'FLM': 0.5, 'ONE': 0.001, 'ONG': 0.11, 'ANKR': 657.0, 'SUSHI': 1.81, 'GNT': 0.0, 'VITE': 1.0, 'ALGO':0.01, 'SC': 0.1, 'BKRW': 10.0, 'WBTC': 0.0002, 'ONT': 1.0, 'PPT': 11.0, 'XPR': 1.0, 'DIA': 4.84, 'RDN': 35.0, 'RUB': 0.0, 'PIVX': 0.2, 'ASR': 0.011, 'ARDR': 2.0, 'AST': 74.0, 'CLOAK': 0.02, 'MANA': 71.0, 'NEBL': 0.01, 'BEL': 6.56, 'JUV': 0.01, 'VTHO':200.0, 'MEETONE': 300.0, 'QSP': 209.0, 'SALT': 5.2, 'STORM': 100.0, 'ATD': 100.0, 'NMR': 0.26, 'MKR': 0.01, 'REN': 18.0, 'ATM': 0.0075, 'REP': 0.34, 'APPC': 219.0, 'JEX': 50.0, 'ELF': 54.0, 'REQ': 201.0, 'STORJ': 19.0, 'ICX': 0.02, 'CHF': 0.0, 'ADD': 100.0, 'BZRX': 36.0, 'SGT': 200.0, 'DF': 51.0, 'LOOM': 195.0, 'ZEN': 0.002, 'PAXG': 0.005, 'YOYO': 1.0, 'PAX': 5.77, 'KP3R': 0.026, 'DUSK': 134.0, 'ALPHA': 26.0, 'DOGE': 50.0, 'BOLT': 10.0, 'SXP': 8.2, 'HBAR': 1.0, 'RVN': 1.0, 'CHR': 255.0, 'VND': 0.0,'AUD': 0.0, 'NANO': 0.01, 'WAVES': 0.002, 'CHZ': 285.0, 'ADX': 16.0, 'IDR': 0.0, 'XRP': 0.25, 'WPR': 788.0, 'CTSI': 140.0, 'AED': 0.0, 'SAND': 156.0, 'KAVA': 0.001, 'DKK': 0.0, 'PSG': 0.01, 'OCEAN': 17.0, 'FOR': 365.0, 'UMA': 0.74, 'HCC': 0.0005, 'VIDT': 9.89, 'NOK': 0.0, 'AVA': 0.048, 'SYS': 1.0, 'COCOS': 1.0, 'STRAX': 0.1, 'SCRT': 0.1, 'TUSD': 5.77, 'CZK': 0.0, 'GAS': 0.005, 'WABI': 59.0, 'COVEROLD': 0.055, 'IDRT': 82126.0, 'ENG': 0.0, 'THETA': 0.1, 'ENJ': 43.0, 'YFII': 0.0038, 'KZT': 0.0, 'WAN':0.1, 'OAX': 63.0, 'GRT': 16.0, 'GRS': 0.2, 'UND': 5.0, 'HARD': 0.1, 'TFUEL': 6.18, 'ORN': 2.75, 'PERL': 243.0, 'LEND': 1.0, 'DLT': 135.0, 'TROY': 2190.0, 'UNI': 1.26, 'AAVE': 0.1, 'XRPBEAR': 0.0012, 'GBP': 0.0, 'LLT': 100.0, 'HUF': 0.0, 'SBTC': 0.0005, 'WRX': 87.0, 'YFI': 0.00027, 'XTZ': 0.5, 'LUNA': 0.01, 'PERLOLD': 50.0, 'AGI': 115.0, 'MOD': 5.0, 'EON': 10.0, 'EOP': 5.0, 'EOS': 0.1, 'GO': 0.01, 'NCASH': 7476.0, 'EOSBULL': 0.005, 'OST': 365.0, 'SKL': 100.0, 'PEN': 0.0, 'BLINK': 50.0, 'HC': 0.005, 'AXS': 9.9, 'ZIL': 0.01, 'SKY': 0.02, 'BURGER': 0.13, 'NAS': 0.1, 'XEM': 4.0, 'NAV': 0.2, 'GTO': 597.0, 'CTXC': 70.0, 'WTC': 20.0, 'XVG': 0.1, 'TNB': 2815.0, 'BIDR': 527.0, 'DNT': 123.0, 'BCHSV': 0.0001, 'BULL': 0.0, 'COMP': 0.04, 'ETHBNT': 5.0, 'XVS':0.021, 'STEEM': 0.01, 'BVND': 100.0, 'SLP': 321.0, 'TNT': 1314.0, 'RUNE': 0.03, 'NBS': 1.0, 'GHST': 9.87, 'KMD': 0.002, 'DOT': 0.72, 'IQ': 50.0, 'CMT': 1.0, 'IDEX': 182.0, '1INCH': 5.09, 'XRPBULL': 0.076, 'AVAX': 0.01, 'MITH': 480.0, 'ERD': 1000.0, 'CND': 657.0, 'UNFI': 1.06, 'UAH': 0.0, 'FTM': 351.0, 'POWR': 56.0, 'KNC': 7.32, 'GVT': 3.91, 'WINGS': 20.0, 'PROM': 2.51, 'FTT': 1.0, 'CHAT': 100.0, 'RLC': 7.93, 'BGBP': 2.81, 'ATOM': 0.005, 'BLZ': 91.0, 'HIVE': 0.01, 'SNM': 635.0, 'MBL': 15.0, 'SNT': 189.0, 'SNX': 0.71, 'FUN': 895.0, 'SNGLS': 1037.0, 'COS': 788.0, 'USD': 0.0, 'QKC': 1095.0, 'ROSE': 0.1, 'DAI': 5.74, 'SOL': 0.01, 'FET': 108.0, 'ETF': 1.0, 'ETHBULL': 0.0, 'BNB': 0.0, 'CELR': 1231.0, 'OGN': 48.0, 'ETH': 0.005, 'MCO': 1.41, 'NEO': 0.0, 'LRC': 33.0, 'REPV1': 0.1, 'XZC': 0.02, 'ADXOLD': 5.0, 'MTH': 758.0, 'GXS': 0.3, 'MTL': 14.0, 'VET': 100.0, 'TRB': 0.34, 'BNT': 4.5, 'QLC': 1.0, 'USDT': 3.0, 'LBA': 10.0, 'USDS': 2.0, 'OXT': 24.0, 'MDA': 11.0, 'UTK': 47.0, 'DASH': 0.002, 'NVT': 0.1, 'SWRV': 12.0, 'EOSBEAR': 0.022, 'EDO': 2.23, 'HEGIC': 48.0, 'GHS': 0.0, 'AMB': 447.0, 'WBNB': 0.002, 'FUEL': 564.0, 'DREP': 1516.0, 'TRY': 0.0, 'TRX': 216.0, 'MDT': 262.0, 'MDX': 100.0, 'HKD': 0.0, 'AERGO': 125.0, 'EUR': 0.0, 'LSK': 0.1, 'BOT': 0.011, 'CAD': 0.0, 'NULS': 0.01, 'BEAR': 0.0, 'BEAM': 0.1, 'CAN': 5.0, 'DCR': 0.01, 'NGN': 0.0, 'CREAM': 0.086, 'DATA': 152.0, 'ENTRP':10.0, 'USDC': 5.77, 'ANTOLD': 1.0, 'WIN': 457.0, 'BNBBULL': 0.012, 'INJ': 1.45, 'TCT': 679.0, 'HNST': 10.0, 'CRV': 10.0, 'EVX': 20.0, 'LTO': 44.0, 'BAKE': 4.98, 'ANT': 1.83, 'NXS': 0.02, 'INR': 0.0, 'CBK': 1.2, 'SRM': 5.29, 'CBM': 200.0, 'INS': 52.0, 'JPY': 0.0, 'PLN': 0.0, 'ETHBEAR': 0.0, 'OG': 0.012, 'XLM': 0.01, 'LINK': 0.5, 'MFT': 2197.0, 'QTUM': 0.01, 'LUN': 1.54, 'KSM': 0.01, 'BETH': 0.0075, 'BQX': 36.0, 'FIL': 0.26, 'POLY': 61.0, 'STMX': 2463.0, 'BAL': 0.42, 'FIO': 5.0, 'VIB': 312.0, 'VIA': 0.01, 'BRD': 94.0, 'BAT': 28.0, 'VRAB': 300.0, 'AKRO': 615.0, 'NZD': 0.0, 'BUSD': 3.0, 'ARPA': 255.0, 'XMR': 0.0001, 'BRL': 0.0, 'COTI': 128.0}
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
            gate_fee = get_gate_fee()  
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
            if i >= 3:  #change
                for j in range(len(exchangeNames)):
                    if i < j :
                        com_pairs = set(pairs_new[i]) & set (pairs_new[j])
                        #print(com_pairs)
                        print('\n',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),exchangeNames[i],'---',exchangeNames[j],'Start Checking!','\n')
                        n = ''
                        p = 0
                        #print(com_pairs)
                        if com_pairs !=[]:
                            for s in com_pairs:
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
                                    if b_bid_price[0]/a_ask_price[0] > 1.02 and profit >3:
                                        '''
                                        print('-'*60)
                                        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$')
                                        print('S1: ',b_bid_price[0],'B1: ',a_ask_price[0],'Qty: ',min_vol)
                                        print('Price: ',b_bid_price,a_ask_price,'|','Vol: ',b_bid_vol,a_ask_vol)
                                        print('-'*60)
                                        '''
                                        try:
                                            if exchangeNames[i]=='Binance':
                                                f = get_binance_fee[s.split('/')[0]]
                                            elif exchangeNames[i]=='GateIO':
                                                f = gate_fee[s.split('/')[0]]['withdraw_fix']
                                            elif exchangeNames[i]=='Bitmax':
                                                f = get_bitmax_fee(s)
                                            elif exchangeNames[i]=='Hoo':
                                                f = get_hoo_fee[s.split('/')[0]]
                                            elif exchangeNames[i]=='Pwang':
                                                f = get_pol_fee(s) 
                                            elif exchangeNames[i]=='Huobi':
                                                f = get_huobi_fee(s)                              
                                            else:
                                                pass
                                        except:
                                            f =0
                                        #print(s,'fee:',f,exchangeNames[i])
                                        if profit-f*a_ask_price[0]>3:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[j])+'====>'+str(exchangeNames[i])+'\n'+s+' || '+str(format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(b_bid_real-a_ask_real,'.1f'))+'$'+'\n'+'='*20+'\n'+'|| RP: '+str(format(profit-f*a_ask_price[0],'.1f'))+'$'+' || Fee: '+str(f)+' '+str(s.split('/')[0])+'\n'
                                            Msg3='-'*40+'\n'+'Sell1: '+str(b_bid_price[0])+'\n'+'Buy1: '+str(a_ask_price[0])+'\n'+'Qty: '+str(min_vol)+'\n'+'USDT: '+str(format(a_ask_price[0]*min_vol,'.1f'))+'\n'
                                            Msg4='-'*40+'\n'+'Price: '+'\n'+str(b_bid_price)+'\n'+str(a_ask_price)+'\n'
                                            Msg5='Vol: '+'\n'+str(b_bid_vol)+'\n'+str(a_ask_vol)
                                            Msg=Msg1+Msg2+Msg3+Msg4+Msg5                                        
                                            #print(Msg)
                                            url = 'https://api.telegram.org/bot1416495682:AAHApsU56yr5Xvd4S9sjhGWgJQkYV9ErAVI/sendMessage?chat_id=-1001320208517&text='+Msg
                                            data = requests.get(url, headers={
                                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()

                                    #else:
                                        #print('-'*40)
                                        #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$','|','No depth!')
                                        #print(b_bid_price,b_bid_vol,'|',a_ask_price,a_ask_vol)
                                        #break                                        
                                    elif a_bid_price[0]/b_ask_price[0] > 1.02 and profit >3:

                                        '''
                                        print('-'*60)
                                        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[i],'-->',exchangeNames[j],'|',s,'|',format(a_bid_real-b_ask_real,'.1f'),'$')
                                        print('S1: ',a_bid_price[0],'B1: ',b_ask_price[0],'Qty: ',min_vol)
                                        print('Price: ',a_bid_price,b_ask_price,'|','Vol: ',a_bid_vol,b_ask_vol)
                                        print('-'*60)
                                        '''
                                        try:
                                            if exchangeNames[j]=='Binance':
                                                f = get_binance_fee[s.split('/')[0]]
                                            elif exchangeNames[j]=='GateIO':
                                                f = gate_fee[s.split('/')[0]]['withdraw_fix']
                                            elif exchangeNames[j]=='Bitmax':
                                                f = get_bitmax_fee(s)
                                            elif exchangeNames[j]=='Hoo':
                                                f = f = get_hoo_fee[s.split('/')[0]]
                                            elif exchangeNames[j]=='Pwang':
                                                f = get_pol_fee(s) 
                                            elif exchangeNames[j]=='Huobi':
                                                f = get_huobi_fee(s)                              
                                            else:
                                                pass
                                        except:
                                            f =0
                                        #print(s,'fee:',f,exchangeNames[j])
                                        if profit-f*b_ask_price[0]>3:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[i])+'====>'+str(exchangeNames[j])+'\n'+s+' || '+str(format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(a_bid_real-b_ask_real,'.1f'))+'$'+'\n'+'='*20+'\n'+'|| RP: '+str(format(profit-f*b_ask_price[0],'.1f'))+'$'+' || Fee: '+str(f)+' '+str(s.split('/')[0])+'\n'
                                            Msg3='-'*40+'\n'+'Sell1: '+str(a_bid_price[0])+'\n'+'Buy1: '+str(b_ask_price[0])+'\n'+'Qty: '+str(min_vol)+'\n'+'USDT: '+str(format(b_ask_price[0]*min_vol,'.1f'))+'\n'
                                            Msg4='-'*40+'\n'+'Price:'+'\n'+str(a_bid_price)+'\n'+str(b_ask_price)+'\n'
                                            Msg5='Vol:'+'\n'+str(a_bid_vol)+'\n'+str(b_ask_vol)
                                            Msg=Msg1+Msg2+Msg3+Msg4+Msg5                                        
                                            #print(Msg)
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