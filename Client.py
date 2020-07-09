#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
1. 20200705-条件1：死叉作为判断进场的依据，触发1s监控，
2. 20200705-条件2：需要率震动ATR指标大于0.025；条件3：SMIIO指标，金叉 条件4：价格低于之前一半
'''

from gateAPI import GateIO
import time
import talib
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import datetime
import json

# 填写 apiKey APISECRET
apiKey = 'EDF07FEF-02E9-4E5A-B171-B2A9A7E48207'
secretKey = '059e9f6cfad083e092446325377b02570fb92d59e33006719c57d6d43b4f1572'

# address
btcAddress = 'your btc address'


# Provide constants

API_QUERY_URL = 'data.gateio.la'
API_TRADE_URL = 'api.gateio.la'

# Create a gate class instance

gate_query = GateIO(API_QUERY_URL, apiKey, secretKey)
gate_trade = GateIO(API_TRADE_URL, apiKey, secretKey)
currency_pair='eos_usdt'
step = 0.01
interval = 10 #second
coin_status = 'Normal'
GROUP_SEC = 60
RANGE_HOUR = 2
condit_1 = 0 # 金叉判断
condit_2 = 0 # 震荡ATR判断
condit_3 = 0 # 震荡ATR判断
condit_4 = 0 # 震荡ATR判断

# Download candle data
'''
def download_data():
    print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'--------GATEIO HAIWWHAI TEST-------',currency_pair,'---------------------')
    while True:
        try:
            coin_candle_1M = gate_query.candlestick(currency_pair,60,1)
            coin_candle_5M = gate_query.candlestick(currency_pair,300,10)
'''
def myTicker(currency_pair,coin_status):
        # Market depth of pair
        #order_book = gate_query.orderBook(currency_pair)
    while True:    
        coin_ticker = gate_query.ticker(currency_pair)
        #print(coin_ticker)
        if coin_ticker['result'] :
            coin_last = coin_ticker['last']
            coin_lowestAsk = coin_ticker['lowestAsk']
            coin_highestedBid = coin_ticker['highestBid']
            coin_high24hr = coin_ticker['high24hr']
            coin_low24hr = coin_ticker['low24hr']
            print(currency_pair,'<<< ', coin_status,' >>> LAST: ',coin_last,' LowAsk: ',coin_lowestAsk,' HighBid: ',coin_highestedBid,' H24hr: ',coin_high24hr,' L23hr: ',coin_low24hr)
            time.sleep(random.random()/3 + 0.1)     
            break
        else:
            print('Can not get Ticker, re-try!')
            time.sleep(random.random()/3 + 0.1) 
    return coin_ticker

def myCandle(currency_pair,GROUP_SEC,RANGE_HOUR):
    df =[]
    while True:
        #print(gate_query.balances())
        # Market candle of pair
        #GROUP_SEC 和 RANGE_HOUR 替换为需要获取的时间区域.
        coin_candle = gate_query.candlestick(currency_pair,GROUP_SEC,RANGE_HOUR)
        if coin_candle['result'] :
            #close = [float(x) for x in coin_candle['data']]
            #print(coin_candle['data'])
            coin_Time = list(zip(*coin_candle['data']))[0]
            coin_Volume = list(zip(*coin_candle['data']))[1]
            coin_Close = list(zip(*coin_candle['data']))[2]
            coin_High = list(zip(*coin_candle['data']))[3]
            coin_Low = list(zip(*coin_candle['data']))[4]        
            coin_Open = list(zip(*coin_candle['data']))[5]
            df = pd.DataFrame({'Time': coin_Time, 'Volume': coin_Volume, 'Close': coin_Close, 'High': coin_High, 'Low': coin_Low, 'Open': coin_Open}) 
            #print(df)
            break
        else:
            print('Can not get MACD, re-try!')
            time.sleep(random.random()/3 + 0.1) 
    return df

f = open('./data.txt',"a")
while True:
    try:
        print ('\n',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'--------GATEIO HAIWWHAI TEST-------',currency_pair,'---------------------')
        myTicker(currency_pair,coin_status)   
        df = myCandle(currency_pair,GROUP_SEC,RANGE_HOUR)        
        #差离值（DIF）的计算： DIF = EMA12 - EMA26，即为talib-MACD返回值macd
        #今日DEA = （前一日DEA X 8/10 + 今日DIF X 2/10），即为talib-MACD返回值signal
        #BAR=（DIF-DEA)2，即为MACD柱状图。
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        df['DIFF'],df['DEA'],df['BAR'] = talib.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)   
        df['EMA3'] = talib.EMA(np.array(close), timeperiod=3)  
        df['EMA9'] = talib.EMA(np.array(close), timeperiod=9)
        df['EMA18'] = talib.EMA(np.array(close), timeperiod=18)
        #KDJ
        df['slowk'], df['slowd'] = talib.STOCH(high, low, close,
                        fastk_period=9,
                        slowk_period=3,
                        slowk_matype=0,
                        slowd_period=3,
                        slowd_matype=0)
        df['slowj'] = 3* df['slowk'] - 2* df['slowd']
        #df['ATR'] = talib.ATR(high, low, close, 14)
        print(df.iloc[120, 12],'  ',df.iloc[120, 13],'  ',df.iloc[120, 14])
        #df.to_csv('./test.csv', encoding='utf-8', index=None)
        #print('成功写入')
        #nn = df.shape[0]
        #coin_avg = close.sum()/nn #近期平均值
        
        #for i in range(33,nn-1):            
        if ((df.iloc[119, 6] < df.iloc[119, 7]) & (df.iloc[120, 6] > df.iloc[120, 7]) ):
            print("MACD/EMA up date:" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000))
            f = open('./data.txt',"a")
            f.write("MACD/EMA up date:" + str(df.index[120]) + str(datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000)) + '\n')
            f.close()
            coin_status = 'upupup'
            interval = 1 #second
            coin_ticker = myTicker(currency_pair,coin_status)
            coin_buy = json.loads(gate_trade.buy(currency_pair,float(coin_ticker['last']), 1))
            print(coin_buy)
            if coin_buy['result']:
                f = open('./data.txt',"a")
                f.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Buy one EOS date:" + '\n')
                f.close()
                print('Sucess buy one EOS！')   
                check_order = json.loads(gate_trade.getOrder(coin_buy['orderNumber'],currency_pair))
                #print(check_order)
                time.sleep(3) #for buy close
                if check_order['order']['status'] == 'closed' :
                    myBalances = json.loads(gate_trade.balances())
                    print(myBalances)
                    if float(myBalances['available']['EOS']) > 20 and float(myBalances['available']['USDT']) > 50 :
                        coin_sell = json.loads(gate_trade.sell(currency_pair, format(float(coin_buy['filledRate'])*1.01,'.4f'),1))
                        print(coin_sell)
                        if coin_sell['result']:
                            f = open('./data.txt',"a")
                            f.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + " Sell EOS date：" + '\n')
                            f.close()
                            print('Sucess Sell one EOS！')  
                    else:
                        print('No enough cash!')                           
        else:
            coin_status = 'Normal'
            interval = 10 #second 
            
        if ((df.iloc[119, 6] > df.iloc[119, 7]) & (df.iloc[120, 6] < df.iloc[120, 7])):
            print("MACD down date:" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000))
            f = open('./data.txt',"a")
            f.write("MACD down date:" + str(datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000)) + '\n')
            f.close()
            interval = 1 #second
            coin_status = 'downdown'
        else:
            coin_status = 'Normal'
            interval = 10 #second 



        time.sleep(random.random()/3 + interval)   
    except IOError:
        print("Exception when calling API!")
        time.sleep(random.random()/3 + 1)

# Trading Pairs
#print(gate_query.pairs())

# Below, use general methods that query the exchange

#  Market Info
# print(gate_query.marketinfo())

# Market Details
# print(gate_query.marketlist())

# Tickers
# print(gate_query.tickers())
# Depth
# print(gate_query.orderBooks())

# orders
# print(gate_query.openOrders())

# Below, use methods that make use of the users keys

# Ticker
# print(gate_query.ticker(currency_pair))

# Market depth of pair
# print(gate_query.orderBook(currency_pair))

# Market candle of pair
# GROUP_SEC 和 RANGE_HOUR 替换为需要获取的时间区域.
# print(gate_query.candlestick(currency_pair,10,1))

# Trade History
# print(gate_query.tradeHistory('btc_usdt'))

# Get account fund balances
#print(gate_trade.balances())

# get new address
# print(gate_trade.depositAddres('btc'))

# get deposit withdrawal history
# print(gate_trade.depositsWithdrawals('1469092370', '1569092370'))

# Place order sell
# print(gate_trade.buy('etc_btc', '0.001', '123'))

# Place order sell
# print(gate_trade.sell('etc_btc', '0.001', '123'))

# Cancel order
# print(gate_trade.cancelOrder('267040896', 'etc_btc'))

# Cancel all orders
# print(gate_trade.cancelAllOrders('0', 'etc_btc'))

# Get order status
# print(gate_trade.getOrder('267040896', 'eth_btc'))

# Get my last 24h trades
# print(gate_trade.mytradeHistory('etc_btc', '267040896'))

# withdraw
# print(gate_trade.withdraw('btc', '88', btcAddress))
