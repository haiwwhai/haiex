# -*- coding: utf-8 -*-
#binance bitmax hoo gateIO Poloneix huobi
import requests
import time
import random
#import wxpy
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
    url='https://api.binance.com/api/v3/ticker/bookTicker'
    data=[]    
    try:
        data=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('币安网站正常')
        for i in data:
            str_list = list(i['symbol'])
            nPos = i['symbol'].find('USDT')
            if nPos >=3:
                str_list.insert(nPos,'/')
                str_2="".join(str_list)
                i['symbol']=str_2
        coinjson = list(filter(lambda x:x['symbol'] == symbol,data))[0]
        #print(coinjson)
        data = list(map(float,[coinjson['bidPrice'],coinjson['bidQty'],coinjson['askPrice'],coinjson['askQty']]))   
        
    except:
        data=[]
        print("Binance "+symbol+" not response!")
            
    return data   #'bidPrice': 'bidQty' 'askPrice':  'askQty': 


#得到gate深度
def get_bitmax_data(symbol):
    url = 'https://bitmax.io/api/pro/v1/ticker'
    data=[]
    try:
        data = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('获取',symbol1,'币深度正常')
        tickers = data['data']  
        coinjson = list(filter(lambda x:x['symbol'] == symbol,tickers))[0]
        #print(coinjson)
        data = list(map(float,[coinjson['bid'][0],coinjson['bid'][1],coinjson['ask'][0],coinjson['ask'][1]]))      
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
        data.append(float(depth['bids'][0][0]))
        data.append(float(depth['bids'][0][1]))
        data.append(float(depth['asks'][-1][0]))
        data.append(float(depth['asks'][-1][1]))
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print('Gate '+symbol+' not response!')
    return data
def get_huobi_data(symbol):
    i=symbol.replace('/','').lower()
    url = 'https://api.huobi.pro/market/depth?symbol='+i+'&type=step0&depth=5'
    data=[]
    try:
        depth = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(depth['bids'])
        data.append(float(depth['tick']['bids'][-1][0]))
        data.append(float(depth['tick']['bids'][-1][1]))
        data.append(float(depth['tick']['asks'][0][0]))
        data.append(float(depth['tick']['asks'][0][1]))
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
        data.append(float(h_depth['bids'][0]['price']))
        data.append(float(h_depth['bids'][0]['quantity']))
        data.append(float(h_depth['asks'][0]['price']))
        data.append(float(h_depth['asks'][0]['quantity']))
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
    url="https://poloniex.com/public?command=returnOrderBook&currencyPair="+c+"&depth=1"
    data=[]
    try:
        data1=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print('P网正常')
        data.append(data1['bids'][0][0])
        data.append(data1['bids'][0][1])
        data.append(data1['asks'][0][0])
        data.append(data1['asks'][0][1])
    except:
        data = []
        print("Pwang "+symbol+" not response!")
    return data

#得到gate pair
def get_gate_pairs():
    url = 'https://data.gateapi.io/api2/1/pairs'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data = [i.replace('_','/') for i in data1 if 'USDT' in i]
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
        
        print('Get HOO     pairs sucessfully！')
    except:
        pairs=[]
        print('Can HOO     Get GATE pairs！') 
    return pairs
def get_bitmax_pairs():
    url = 'https://bitmax.io/api/pro/v1/products'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        #print(data1['data'])
        data = [i['symbol'] for i in data1['data'] if 'USDT' in i['symbol']]
        print('Get BITMAX  pairs sucessfully')
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
        print("Get BINANCE pairs sucessfully")        
    except:
        binance_pairs=[]
        print("Can not Get BINANCE pairs!")
            
    return binance_pairs   #'bidPrice': 'bidQty' 'askPrice':  'askQty':
def get_pol_pairs():
    url="https://poloniex.com/public?command=returnTicker"
    temp=[]
    try:
        data1=requests.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        data=data1.keys()
        for i in data:
            a=i.split('_')[0]
            b=i.split('_')[1]
            c=b+'/'+a        
            temp.append(c)
        print('Get PWANG   pairs sucessfully!')
    except:
        temp = []
        print("Can not Get PWANG pairs!")
    return temp
def get_huobi_pairs():
    url = 'https://api.huobi.pro/v1/common/symbols'
    try:
        data1 = requests.get(url, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}).json()
        ss = data1['data']
        data = [(i['base-currency']+'/'+i['quote-currency']).upper() for i in ss]
        print('Get HUOBI   pairs sucessfully')
    except:
        data=[]
        #time.sleep(random.uniform(1, 3))
        print("Can not Get HUOBI pairs!")
    return data

def sendmail(content,title):
    s=''
    msg_from='280773242@qq.com' #发送方邮箱
    passwd='settbbjsoxlxbihf'   #填入发送方邮箱的授权码
    msg_to='haiwwhai@qq.com'    #收件人邮箱
                                
    subject=title     #主题     
    #content="12323"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        #print("Send Sucessfully!") 
    except:
        pass
        # print("发送失败") 
    finally:
        s.quit()

#==================main================================================================
exchangeNames=['Hoo','Bitmax','GateIO','Binance','Huobi','P网']
pairs_all = []
data_all = []
pairs_new =[[] for i in exchangeNames]
delete_coins=[['CET'],['CET'],['STX','ETC','RVC'],['ETC'],[],['DOT']]

pairs_all.append(get_hoo_pairs())
pairs_all.append(get_bitmax_pairs())
pairs_all.append(get_gate_pairs())
pairs_all.append(get_binance_pairs())
pairs_all.append(get_huobi_pairs())
pairs_all.append(get_pol_pairs())

 
# DELETE COINS---------------
for i in range(len(exchangeNames)): 
    pairs_new[i]=[] 
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

while True:
    for i in range(len(exchangeNames)):      
        for j in range(len(exchangeNames)):
            if i < j :
                com_pairs = set(pairs_new[i]) & set (pairs_new[j])
                print('\n',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),exchangeNames[i],'---',exchangeNames[j],'Start Checking!','\n')
                n = ''
                p = 0
                #print(com_pairs)
                if com_pairs !=[]:
                    for s in com_pairs:
                        ticker=[]
                        try:
                            if exchangeNames[i]=='Binance':
                                ticker = get_binance_data(s)
                            elif exchangeNames[i]=='GateIO':
                                ticker = get_gate_data(s)
                            elif exchangeNames[i]=='Bitmax':
                                ticker = get_bitmax_data(s)
                            elif exchangeNames[i]=='Hoo':
                                ticker = get_hoo_data(s)
                            elif exchangeNames[i]=='P网':
                                ticker = get_pol_data(s) 
                            elif exchangeNames[i]=='Huobi':
                                ticker = get_huobi_data(s)                              
                            else:
                                pass
                            bidPrice_i=ticker[0]
                            bidVolum_i=ticker[1]
                            askPrice_i=ticker[2]                    
                            askVolum_i=ticker[3]
                            if exchangeNames[j]=='Binance':
                                ticker = get_binance_data(s)
                            elif exchangeNames[j]=='GateIO':
                                ticker = get_gate_data(s)
                            elif exchangeNames[j]=='Bitmax':
                                ticker = get_bitmax_data(s)
                            elif exchangeNames[j]=='Hoo':
                                ticker = get_hoo_data(s)
                            elif exchangeNames[j]=='P网':
                                ticker = get_pol_data(s)    
                            elif exchangeNames[j]=='Huobi':
                                ticker = get_huobi_data(s)                             
                            else:
                                pass
                            bidPrice_j=ticker[0]
                            bidVolum_j=ticker[1]
                            askPrice_j=ticker[2]                    
                            askVolum_j=ticker[3]
                            profit = 0
                            #print(s,'||',exchangeNames[i],bidPrice_i,askPrice_i,bidVolum_i,askVolum_i,'||',exchangeNames[j],bidPrice_j,askPrice_j,bidVolum_j,askVolum_j,'||',float(bidPrice_i)/float(askPrice_j))
                            #message = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'  '+format((float(bidPrice_j)-float(askPrice_i))/float(bidPrice_j)*100,'.3f')+'%'+' || '+s+' || '+str(profit)+'$'+'\n'+' SELL: '+exchangeNames[j]+' | '+str(bidPrice_j)+' | '+str(bidVolum_j)+'\n'+' BUY: '+exchangeNames[i]+' | '+str(askPrice_i)+' | '+str(askVolum_i)
                            #print('-'*60,'\n',message)
                            #sendmail(str(message),str(s+' SELL: '+exchangeNames[j]+' BUY: ',exchangeNames[i]))                        
                            if float(bidPrice_i)/float(askPrice_j) > 1.01 :
                                profit = format((float(bidPrice_i)-float(askPrice_j))*float(min(bidVolum_i,askVolum_j)),'.1f')
                                #print(profit)
                                #if  profit > 0:#and  float(bidPrice_i) * float(bidVolum_i>1):     float(askPrice_j) * float(askVolum_j>10) and                               
                                message = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'-->'+format((float(bidPrice_i)-float(askPrice_j))/float(bidPrice_i)*100,'.3f')+'%'+' || '+s+' || '+str(profit)+'$'+'\n'+' SELL: '+exchangeNames[i]+' | '+str(bidPrice_i)+' | '+str(bidVolum_i)+'\n'+' BUY: '+exchangeNames[j]+'|  '+str(askPrice_j)+' | '+str(askVolum_j)
                                print('-'*60,'\n',message)
                                if float(profit) > 1.5:
                                    sendmail(str(message),str(s+' SELL: '+exchangeNames[i]+' BUY: '+exchangeNames[j]))

                                #print('Pair:' ,s,'--->',Names[i],' Sell ',Names[j],' Buy----Profit: No depth!')
                            elif float(bidPrice_j)/float(askPrice_i) > 1.01:
                                profit = format((float(bidPrice_j)-float(askPrice_i))*float(min(bidVolum_j,askVolum_i)),'.1f')
                                #print(profit)
                                #if profit > 0:# and  float(askPrice_i) * float(askVolum_i>1):float(bidPrice_j) *s float(bidVolum_j>10) and 
                                message = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'-->'+format((float(bidPrice_j)-float(askPrice_i))/float(bidPrice_j)*100,'.3f')+'%'+' || '+s+' || '+str(profit)+'$'+'\n'+' SELL: '+exchangeNames[j]+' | '+str(bidPrice_j)+' | '+str(bidVolum_j)+'\n'+' BUY: '+exchangeNames[i]+' | '+str(askPrice_i)+' | '+str(askVolum_i)
                                print('-'*60,'\n',message)
                                if float(profit) > 1.5:
                                    sendmail(str(message),str(s+' SELL: '+exchangeNames[j]+' BUY: ',exchangeNames[i]))
                                #print('Pair:' ,s,'--->',Names[j],' Sell ',Names[i],' Buy----Profit: No depth!')
                            else:
                                pass
                        except:
                            pass       
                        time.sleep(random.uniform(0.5, 1))                        
                        p += 1
                        n = '#' *int(p/len(com_pairs)*40)
                        sys.stdout.write(str(int((p/((len(com_pairs)))*100)))+'% ('+str(p)+'/'+str(len(com_pairs))+') ||'+n+'->'+"\r")
                        sys.stdout.flush()
                


    


