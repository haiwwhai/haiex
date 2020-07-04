#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
1.
'''

from gateAPI import GateIO
import time
import talib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import datetime

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
        df['DIFF'],df['DEA'],df['BAR'] = talib.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)   
        #df['EMA12'] = talib.EMA(np.array(close), timeperiod=12)  
        #df['EMA26'] = talib.EMA(np.array(close), timeperiod=26) 
        #print(df)
        #df.to_csv('./test.csv', encoding='utf-8', index=None)
        nn = df.shape[0]
        #for i in range(33,nn-1):            
        if ((df.iloc[119, 6] < df.iloc[119, 7]) & (df.iloc[120, 6] > df.iloc[120, 7])):
            print("MACD 金叉的日期：" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000))
            f.write("MACD 金叉的日期：" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000)+"\n")
            if (df['Volume'].sum()/nn < df.iloc[120, 1]):
                print('有量，加速追踪！准备获利卖出，准备空仓买进！')
                coin_status = '↓↓↓↑↑↑'
                interval = 1 #second
            else:
                print('恢复正常！')
                coin_status = 'Normal'
                interval = 10 #second                
        else:
            coin_status = 'Normal'
            interval = 10 #second 
        if ((df.iloc[119, 6] > df.iloc[119, 7]) & (df.iloc[120, 6] < df.iloc[120, 7])):
            print("MACD 死叉的日期：" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000))
            f.write("MACD 死叉的日期：" + str(df.index[120]),datetime.datetime.fromtimestamp(df.iloc[120, 0]/1000))
            if (df['Volume'].sum()/nn < df.iloc[120, 1]):
                print('有量，加速追踪！准备止损卖出，准备空仓买进！')
                coin_status = '↑↑↑↓↓↓'
                interval = 1 #second
            else:
                print('恢复正常！')
                coin_status = 'Normal'
                interval = 10 #second 
        else:
            coin_status = 'Normal'
            interval = 10 #second 

        time.sleep(random.random()/3 + interval)   
    except IOError:
        print("Exception when calling API!")
        time.sleep(random.random()/3 + 0.1)

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
