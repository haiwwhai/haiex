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
        path = "/open/v1/tickers"
        obj = gen_sign(client_id, client_key)
        res = requests.get(host + path, params=obj)
        temp = json.loads(res.content)['data']
        for i in temp:
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

get_gate_fee = {'BTC': 0.0005, 'BCH': 0.0005, 'ETH': 5.0, 'ETC': 0.01, 'QTUM': 0.01, 'LTC': 0.001, 'DASH': 0.002, 'ZEC': 0.001, 'BTM': 5.0, 'EOS': 0.1, 'REQ': 90.0, 'SNT': 96.0, 'OMG': 1.1, 'PAY': 53.0, 'CVC': 34.0, 'ZRX': 10.0, 'XMR': 0.001, 'XRP': 0.1, 'DOGE': 20.0, 'BAT': 14.0, 'PST': 210.0, 'DPY': 560.0, 'LRC': 18.0, 'STORJ': 9.8, 'RDN': 18.0, 'KNC': 3.5, 'LINK': 0.3, 'AE': 1.0, 'RLC':3.4, 'RCN': 79.0, 'TRX': 5.0, 'VET': 100.0, 'MCO': 5.0, 'FUN': 780.0, 'DATA': 72.0, 'ZSC': 23000.0, 'MDA': 5.5, 'XTZ': 0.1, 'GEM': 19000.0, 'RFR': 850.0, 'ABT': 43.0, 'OST': 200.0, 'XLM': 0.01, 'MOBI': 1.0, 'OCN': 11000.0, 'COFI': 3100.0, 'JNT': 250.0, 'BLZ': 40.0, 'GXS': 1.0, 'MTN': 1800.0, 'RUFF': 550.0, 'TNC': 10.0, 'ZIL': 10.0, 'THETA': 10.0, 'DDD': 1400.0, 'MKR': 0.0051, 'DAI': 3.0, 'SMT': 50.0, 'MDT': 120.0, 'MANA': 50.0, 'SALT': 9.7, 'FUEL': 12000.0, 'ELF': 28.0, 'DRGN': 65.0, 'GTC': 630.0, 'QLC': 10.0, 'DBC': 10.0, 'BNTY': 3600.0, 'ICX': 0.2, 'ADA': 1.0, 'WAVES': 0.1, 'MDS': 1200.0, 'QASH': 95.0, 'POWR': 30.0, 'BCD': 0.02, 'QSP': 96.0, 'INK': 0.3, 'QBT': 5.0, 'GNX': 320.0, 'NEO': 0.0, 'GAS': 0.02, 'NAS': 0.5, 'OAX': 33.0, 'SNET': 1100.0,'BTS': 1.0, 'USDG': 4.0, 'GT': 4.0, 'ATOM': 0.01, 'HARD': 0.01, 'KAVA': 0.01, 'IRIS': 5.0, 'ANT': 96.0, 'STPT': 170.0, 'RSR':170.0, 'RSV': 3.0, 'KAI': 120.0, 'CTSI': 68.0, 'COMP': 0.022, 'OCEAN': 8.4, 'KSM': 0.05, 'FIRO': 0.5, 'DOT': 0.1, 'MTR': 1.0,'MTRG': 2.0, 'SOL': 0.01, 'COTI': 56.0, 'AMPL': 3.2, 'WNXM': 0.15, 'LUNA': 5.0, 'AVAX': 0.1, 'BZRX': 17.0, 'PCX': 0.2, 'YAMV2': 0.65, 'YAM': 500.0, 'BOX': 0.1, 'CRV': 5.9, 'UNI': 2.0, 'SUSHI': 1.1, 'AAVE': 20.0, 'POLS': 6.2, 'ERG': 10.0, 'GOF': 7.1, 'PHA': 32.0, 'SASHIMI': 88.0, 'FARM': 0.032, 'SWRV': 7.0, 'BOT': 0.01, 'OIN': 11000.0, 'AGS': 38.0, 'ADEL': 12.0, 'TON': 0.2, 'KTON': 0.047, 'RING': 79.0, 'CREAM': 0.052, 'JGN': 39.0, 'DEGO': 5.8, 'RFUEL': 79.0, 'SFG': 6.8, 'NEST': 150.0, 'CORE': 0.00095, 'NEAR': 3.0, 'NU': 17.0, 'STAKE': 0.32, 'TRU': 22.0, 'ROSE': 10.0, 'BADGER': 0.51, 'GLM': 26.0, 'PICKLE': 0.3, 'HEGIC': 29.0, 'GTH': 110.0, 'DUSK': 59.0, '88MPH': 0.095, 'UNFI': 0.43, 'FLM': 10.0, 'GHST': 5.1, 'ACH': 120.0, 'DUCK': 110.0, 'GRT': 20.0, 'ESD': 3.2, 'ALEPH': 19.0, 'FRAX': 3.0, 'FXS': 0.74, 'BOR': 0.013, 'ROOK': 0.03, 'BAC': 2.7, 'BAS': 5.8, 'LON': 12.0, 'MAHA': 0.36, 'WOZX': 2.3, 'FAR': 0.032, 'POND': 80.0, '1INCH': 2.5, 'DSD': 6.8, 'OCTO': 0.095, 'SHARE': 0.05, 'LINA': 250.0, 'WHITE': 0.002, 'WOM': 16.0, 'API3': 1.5, 'FIN': 5.8, 'SKL': 0.1, 'PRQ': 13.0, 'FRONT': 11.0, 'INJ': 1.3, 'ALPA': 31.0, 'ROOBEE': 1500.0, 'NSURE': 3.8, 'KP3R': 0.01, 'WOO': 100.0, 'HYVE': 230.0, 'KFC': 0.26, 'RAMP': 300.0, 'SYLO': 3500.0, 'RARI': 1.3, 'DVP': 80.0, 'MPH': 0.095, 'DF': 23.0, 'CVP': 1.5, 'VALUE': 0.1, 'UMA': 0.4, 'YFII': 0.0021, 'SWAP': 2.0, 'SXP': 4.3, 'BAL': 0.21, 'BAND': 0.53, 'AST': 72.0, 'TROY': 1100.0, 'OM': 5.0, 'SPA': 230.0, 'AKRO': 12.0, 'FOR': 3.2, 'CREDIT': 180.0, 'DIA': 20.0, 'AXIS': 8.6, 'TRB': 0.17, 'LIEN': 0.094, 'PEARL': 0.001, 'CORN': 0.018, 'SLM': 0.12, 'CRT': 1.2, 'MTA': 3.0, 'YFI': 0.0021, 'DKA': 130.0, 'REN': 3.8, 'DOS': 50.0, 'SUTER': 850.0, 'SRM': 2.9, 'JST': 9.8, 'LBK': 430.0, 'BTMX': 82.0, 'WEST': 1.0, 'XEM': 5.0, 'BU': 0.1, 'HNS': 1.0, 'GRIN3L': 1.0, 'GRIN3S': 1.0, 'BEAM3L': 1.0, 'BEAM3S': 1.0, 'SOL3L': 1.0, 'SOL3S': 1.0, 'SKL3L': 1.0,
'SKL3S': 1.0, '1INCH3L': 1.0, '1INCH3S': 1.0, 'LON3L': 1.0, 'LON3S': 1.0, 'DOGE3L': 1.0, 'DOGE3S': 1.0, 'GRT3L': 1.0, 'GRT3S': 1.0, 'QTUM3S': 1.0, 'XLM3L': 1.0, 'XLM3S': 1.0, 'XRP3L': 1.0, 'XRP3S': 1.0, 'BCHSV': 0.0005, 'RVN': 5.0, 'AR': 0.05, 'DCR': 0.02, 'NBS': 100.0, 'STEEM': 1.0, 'HIVE': 1.0, 'BCHA': 1.0, 'ATP': 0.5, 'NAX': 0.5, 'KLAY': 1.0, 'NBOT': 110.0, 'GRIN': 1.0, 'BEAM': 1.0, 'HBAR': 0.1, 'OKB': 1.0, 'REP': 0.18, 'STAR': 6.2, 'ZEN': 1.0, 'FIL': 0.2, 'FIC': 3100.0, 'SUP': 0.01, 'STOX': 42,'VTHO': 50.0, 'VIDYX': 20.0, 'BTT': 330.0, 'TFUEL': 10.0, 'CELR': 600.0, 'MAN': 50.0, 'REM': 1300.0, 'LYM': 910.0, 'ZPT': 10.0, 'ONG': 0.1, 'WING': 81.0, 'ONT': 1.0, 'BFT': 350.0, 'IHT': 5400.0, 'SENC': 2800.0, 'TOMO': 1.0, 'ELEC': 3800.0, 'SNX': 1.0,'NKN': 5.0, 'SOUL': 5.0, 'EOSDAC': 20.0, 'DOCK': 180.0, 'RATING': 25000.0, 'HSC': 150000.0, 'HIT': 0.002, 'DX': 2400.0, 'CNNS': 1100.0, 'DREP': 670.0, 'MBL': 10.0, 'MIX': 1600.0, 'LAMB': 200.0, 'LEO': 2.2, 'BTCBULL': 0.0001, 'BTCBEAR': 100.0, 'ETHBEAR': 740.0, 'ETHBULL': 0.0018, 'EOSBULL': 4.8, 'EOSBEAR': 4.2, 'XRPBEAR': 2.8, 'XRPBULL': 1.4, 'WICC': 2.0, 'WGRT': 100.0, 'SERO': 5.0, 'CORAL': 2.0, 'VIDY': 20.0, 'KGC': 22000.0, 'FTM': 170.0, 'RUNE': 2.0, 'COS': 0.01, 'CBK': 1.0, 'CHZ': 120.0, 'TWT': 1.0, 'AVA': 0.01, 'CRO': 50.0, 'ALY': 8300.0, 'WIN': 81.0, 'SUN': 0.015, 'MTV': 8500.0, 'ONE': 20.0, 'ARPA': 140.0, 'ALGO': 1.0, 'CKB': 1.0, 'BKC': 1.0, 'BXC': 13000.0, 'PAX': 3.0, 'USDC': 3.0, 'TUSD': 3.0, 'HC': 0.2, 'GARD': 100.0, 'CELO': 0.5, 'CFX': 1.0, 'FTI': 10000.0, 'SOP': 91000.0, 'LEMO': 4000.0, 'QKC': 20.0, 'IOTX': 20.0, 'RED': 180.0, 'LBA': 0.21, 'MITH': 230.0, 'SKM': 1600.0, 'XVG': 20.0, 'HT': 10.0, 'BNB': 1.0, 'MET': 1.0, 'TCT': 320.0, 'MXC': 270.0}

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
        print('Huobi '+symbol+' not response!')
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
    return data
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
    delete_coins=[['ETC'],[],['HOT','3L','3S','ETC'],['MPH','ETC','COVER','SWINGBY','OM'],['RAMP','COVER','CET','ETC','BCHA'],['COVER','BOND','AGS','ATP','CET','ETC','OM']]
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
        except:
            pass
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
            if i == 1:  #just pwang
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
                                    
                                    if b_bid_price[0]/a_ask_price[0] > 1.02 and profit >3:
                                        '''
                                        print('-'*60)
                                        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'),'%','|',exchangeNames[j],'-->',exchangeNames[i],'|',s,'|',format(b_bid_real-a_ask_real,'.1f'),'$')
                                        print('S1: ',b_bid_price[0],'B1: ',a_ask_price[0],'Qty: ',min_vol)
                                        print('Price: ',b_bid_price,a_ask_price,'|','Vol: ',b_bid_vol,a_ask_vol)
                                        print('-'*60)
                                        '''
                                        if exchangeNames[i]=='Binance':
                                            f = 0
                                        elif exchangeNames[i]=='GateIO':
                                            f = get_gate_fee[s]
                                        elif exchangeNames[i]=='Bitmax':
                                            f = get_bitmax_fee(s)
                                        elif exchangeNames[i]=='Hoo':
                                            f = 0
                                        elif exchangeNames[i]=='Pwang':
                                            fa = get_pol_fee(s) 
                                        elif exchangeNames[i]=='Huobi':
                                            f = get_huobi_fee(s)                              
                                        else:
                                            pass
                                        #print('fee:',f)
                                        if profit-f*a_ask_price[0]>3:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[j])+'====>'+str(exchangeNames[i])+'\n'+s+' || '+str(format((b_bid_price[0]/a_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(b_bid_real-a_ask_real,'.1f'))+'$ || '+str(format(profit-f*a_ask_price[0],'.1f'))+'$'+'\n'
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
                                        if exchangeNames[j]=='Binance':
                                            f = 0
                                        elif exchangeNames[j]=='GateIO':
                                            f = get_gate_fee[s]
                                        elif exchangeNames[j]=='Bitmax':
                                            f = get_bitmax_fee(s)
                                        elif exchangeNames[j]=='Hoo':
                                            f = 0
                                        elif exchangeNames[j]=='Pwang':
                                            f = get_pol_fee(s) 
                                        elif exchangeNames[j]=='Huobi':
                                            f = get_huobi_fee(s)                              
                                        else:
                                            pass
                                        #print('fee:',f)
                                        if profit-f*b_ask_price[0]>3:
                                            Msg1=str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))+'\n'
                                            Msg2=str(exchangeNames[i])+'====>'+str(exchangeNames[j])+'\n'+s+' || '+str(format((a_bid_price[0]/b_ask_price[0]-1)*100,'.3f'))+'%  || '+str(format(a_bid_real-b_ask_real,'.1f'))+'$ || '+str(format(profit-f*b_ask_price[0],'.1f'))+'$'+'\n'
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