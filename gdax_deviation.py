# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:23:10 2017

@author: Paúl Herrera
"""

import gdax
import pandas as pd
import numpy as np
import datetime as dt
import time
from tqdm import tqdm


class Strategy():
    """
    Abstract Base Class for strategies.
    """
    def __init__(self):
        self.subscribers = []
        self.accountState = 'CLOSE'
        self.ask = [0]
        self.bid = [0]
    
    
class DeviationStrategy(Strategy):
    """
    Trading strategy that enters and exits the market when the price
    deviates X standard deviations from the Y period mean. 
    """
    def __init__(self, period=20, entry_std=2, exit_std=1):
        super().__init__()
        self.period = period
        self.entryStd = entry_std
        self.exitStd = exit_std
        self.lastTimestamp = dt.datetime.now()

    def calculate(self, time, tick, _type):
        """
        Main method. It has the core logic of the strategy.
        """
        time = dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")\
                          .replace(microsecond=0)
        # Updating data.
        if (_type == 'ASK') and (tick != self.ask[-1]):
            self.ask.append(tick)
        elif (_type == 'BID') and (tick != self.bid[-1]) \
        and (time >= self.lastTimestamp + dt.timedelta(seconds=1)):
            self.bid.append(tick)
            self.lastTimestamp = time
            print(time, tick, _type)
            
        # Mean calculations.
        if (len(self.bid) >= self.period + 1) and (_type == 'BID'):
            mean = np.mean(self.bid[-self.period:])
            std = np.std(self.bid[-self.period:])
            # Entry logic.
            if self.accountState == 'CLOSE':
                highStd = mean + self.entryStd * std
                lowStd = mean - self.entryStd * std
                if tick > highStd:
                    self.send_signal((time, 'SELL', tick))
                elif tick < lowStd:
                    self.send_signal((time, 'BUY', tick))
            # Exit logic.
            elif self.accountState != 'CLOSE':
                highStd = mean + self.exitStd * std
                lowStd = mean - self.exitStd * std
                if (tick > highStd) & (self.accountState == 'BUY'):
                    self.send_signal((time, 'CLOSE', tick))
                elif (tick < lowStd) & (self.accountState == 'SELL'):
                    self.send_signal((time, 'CLOSE', tick))
                    
    
    def send_signal(self, signal):
        for s in self.subscribers:
            s.notify(signal)
        self.accountState = signal[1]

                
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    
                
              

class TickFeeder():
    """
    Abstract Base Class. The TickFeeder provides the data 
    to the strategy in an event-driven way.
    """
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        
        
    def append_data(client, df, columns, start_timestamp, end_timestamp, granularity=1):
        newData = client.get_product_historic_rates(product, 
                         dt.datetime.fromtimestamp(start_timestamp).isoformat(),
                         dt.datetime.fromtimestamp(end_timestamp).isoformat(),
                         granularity=granularity)
        data = pd.concat([df, pd.DataFrame(newData, columns=columns)])
        
        return data
    
    
    def feed(self):
        raise NotImplementedError
    
    
    def get_product_historic_rates(self, client, product, start_date, end_date, 
                                   granularity=1):
        """
        Gets the historical data of a product making the necessary
        calls to the GDAX API and returns a pandas DataFrame with
        the data.
        """
        startDate = dt.datetime.strptime(start_date, "%Y-%m-%d")
        startDateTimestamp = startDate.timestamp()
        endDate = dt.datetime.strptime(end_date, "%Y-%m-%d")
        endDateTimestamp = endDate.timestamp()
        
        # List of time divisions for retrieving data.
        timeRange = range(int(startDateTimestamp), int(endDateTimestamp), 
                          200 * granularity)
        timeRange = list(timeRange) + [endDateTimestamp]
        
        # New DataFrame.
        columns = ['time', 'low', 'high', 'open', 'close', 'volume']
        data = pd.DataFrame(columns=columns)
        
        # Populating dataframe.
        for i in tqdm(range(len(timeRange) - 1)):
            try:
                data = self.append_data(client, data, columns, timeRange[i], 
                                   timeRange[i+1])
            except ValueError:
                time.sleep(3)
                data = self.append_data(data, columns, timeRange[i], timeRange[i+1])
        
        # Reindexing dataframe.
        data['time'] = data.time.apply(dt.datetime.fromtimestamp)
        data.set_index('time', inplace=True)
        
        # Using data points where the price has changed.
        data = data.where(data.close != data.close.shift()).dropna().sort_index()
        
        return data
    



class HistoricalDataFeeder(TickFeeder):
    """
    Data feeder for backtesting purposes.
    It uses historical data prices to feed a strategy.
    """
    def feed(self, data):
        for t, p in tqdm(zip(data.index, data.open.values)):
            self.strategy.calculate(t, p, 'BID')
        

class RealTimeFeeder(TickFeeder, gdax.WebsocketClient):
    """
    Data feeder that uses the gdax API to feed real time data
    to a strategy.
    It filters the incoming messages to provide only 'match' messages.
    """
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["BTC-USD"]
        
    def on_message(self, msg):
        if (msg['type'] == 'match'):
            print(msg)
            if (msg['side'] == 'sell'):
                self.feed((msg['time'], msg['price'], 'ASK'))
            elif (msg['side'] == 'buy'):
                self.feed((msg['time'], msg['price'], 'BID'))
    
    def feed(self, data):
        self.strategy.calculate(data[0], float(data[1]), data[2])



class Trader():
    """
    Abstract Base Class. A trader receives the signals from
    the strategy.
    """
    def notify(self, msg):
        raise NotImplementedError


class PaperTrader(Trader):
    """
    Saves the signals in a pandas dataframe.
    """
    def __init__(self):
        super().__init__()
        self._columns = ['time', 'type', 'price']
        self.trades = pd.DataFrame(columns=self._columns)
        
    
    def notify(self, msg):
        self.trades = pd.concat([self.trades, pd.DataFrame([msg], 
                                              columns=self._columns)])
        
    
class RealTimeTrader(Trader):
    """
    Trades in real time through the gdax API.
    It takes a client object as first initialization parameter, so a
    'sandbox' client could be passed.
    """
    def __init__(self, client, product='BTC-USD', size=0.01):
        self.client = client
        self.product = product
        self.size = size
        self.orderId = 0
        self.orderType = 'CLOSE'
        
    def notify(self, msg):
        if msg[1] == 'BUY':
            r = client.buy(msg[2], size=self.size, product_id=self.product)
            self.orderId = r['id']
            self.orderType = 'BUY'
        elif msg[1] == 'SELL':
            r = client.sell(msg[2], size=self.size, product_id=self.product)
            self.orderId = r['id']
            self.orderType = 'SELL'
        elif msg[1] == 'CLOSE':
            if self.orderType == 'BUY':
                r = client.sell(msg[2], size=self.size, product_id=self.product)
            elif self.orderType == 'SELL':
                r = client.buy(msg[2], size=self.size, product_id=self.product)
        
        try: print(r)
        except: pass
    






if __name__ == '__main__':
    # Settig variables.
    key = ''
    secret = ''
    passphrase = ''
    client = gdax.AuthenticatedClient(key, secret, passphrase)
    product = 'BTC-USD'
    startDate = '2017-06-19'
    endDate = '2017-06-26'
    
    # Getting data.
    data = pd.read_csv('BTC-USD_20170619-20170626.csv', index_col=0)
    
    # Initializing objects.
    client = gdax.AuthenticatedClient(key, secret, passphrase)
    strategy = DeviationStrategy(period=10, entryStd=1, exitStd=1)
    feeder = RealTimeFeeder(strategy)
    trader = PaperTrader()
    strategy.subscribe(trader)
    
    # Backtest.
    feeder.start()
    
    
    
    
