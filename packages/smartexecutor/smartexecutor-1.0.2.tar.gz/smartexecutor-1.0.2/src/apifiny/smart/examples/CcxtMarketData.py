import os
import json
import redis
import ccxt
import pandas as pd

class CcxtMarketData():
    def __init__(self,exchange, symbol_coin,symbol_basecoin):
        self.ex = exchange
        self.data_name = symbol_coin + "/" + symbol_basecoin
        #adding support exchange later
        if self.ex == "OKEX":
            self.client = ccxt.okex()
            self.exlabel = "O"

    def get_price(self):
        orderbook = self.client.fetch_order_book(self.data_name)
        self.bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        self.ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        self.mid = (self.ask+self.bid)/2
        self.spread = (self.ask - self.bid) if (self.bid and self.ask) else None
        print ('market price', { 'bid': self.bid, 'ask': self.ask, 'mid': self.mid, 'spread': self.spread })
    
    def get_candle_data(self, timeframe):
        #Get Historical data (ohlcv) from a coin_pair
        # optional: exchange.fetch_ohlcv(coin_pair, '1h', since)
        data = self.client.fetch_ohlcv(self.data_name, timeframe)
        # update timestamp to human readable timestamp
        data = [[self.client.iso8601(candle[0])] + candle[1:] for candle in data]
        header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.df = pd.DataFrame(data, columns=header)
        #print(df)
        return self.df

    def get_ema(self, timeframe, halflife):
        cd = self.get_candle_data(timeframe)
        ema =  cd.ewm(
            ignore_na=False,
            halflife = halflife,
            min_periods=0,
            adjust=True).mean()
        #print(ema)
        return ema
        
