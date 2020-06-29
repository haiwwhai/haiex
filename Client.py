#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Provide user specific data and interact with gate.io
'''

from gateAPI import GateIO
import time
import numpy

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
currency_pair='eth_usdt'


while True:
    try:
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'--------GATEIO HAIWWHAI TEST-------',currency_pair,'---------------------')

        # Market depth of pair
        order_book = gate_query.orderBook(currency_pair)
        if order_book['result'] :
            print(order_book['asks'][-5:-1])
           
        else:
            print('Can not get API, re-try!')    

        # Market candle of pair
        #GROUP_SEC 和 RANGE_HOUR 替换为需要获取的时间区域.
        #print(gate_query.candlestick(currency_pair,10,1))

        time.sleep( 0.2 )

    except IOError:
        print("Exception when calling API!")

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
