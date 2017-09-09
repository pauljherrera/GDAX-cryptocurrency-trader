# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:53:02 2017

@author: Paúl Herrera
"""

import gdax
import pandas as pd
import datetime as dt
import time
from tqdm import tqdm



class DataFeeder():
    """
    Abstract Base Class. The DataFeeder provides the data 
    to the strategy in an event-driven way.
    """
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.subscribers = []

        
    @classmethod
    def append_data(cls, client, df, product, columns, start_timestamp, 
                    end_timestamp, granularity=1):
        newData = client.get_product_historic_rates(product, 
                         dt.datetime.fromtimestamp(start_timestamp).isoformat(),
                         dt.datetime.fromtimestamp(end_timestamp).isoformat(),
                         granularity=granularity)
        data = pd.concat([df, pd.DataFrame(newData, columns=columns)])
        
        return data
    
    
    def feed(self):
        raise NotImplementedError
    
    
    @classmethod
    def get_historic_rates(cls, client, product, start_date, end_date, 
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
                data = cls.append_data(client, data, product, columns, 
                                        timeRange[i], timeRange[i+1])
            except ValueError:
                time.sleep(3)
                data = cls.append_data(data, columns, product, 
                                        timeRange[i], timeRange[i+1])
        
        # Reindexing dataframe.
        data['time'] = data.time.apply(dt.datetime.fromtimestamp)
        data.set_index('time', inplace=True)
        
        # Using data points where the price has changed.
        data = data.where(data.close != data.close.shift()).dropna().sort_index()
        
        return data
    
    def publish(self, msg):
        for s in self.subscribers:
            s.receive(msg)
        
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    

class HistoricalDataFeeder(DataFeeder):
    """
    Data feeder for backtesting purposes.
    It uses historical data prices to feed a strategy.
    """
    def feed(self, data):
        for t, p in tqdm(zip(data.index, data.open.values)):
            self.strategy.calculate(t, p, 'BID')
        

class RealTimeFeeder(DataFeeder, gdax.WebsocketClient):
    """
    Data feeder that uses the gdax API to feed real time data
    to a strategy.
    It filters the incoming messages to provide only 'match' messages.
    """
    def __init__(self, strategy, product='BTC-USD', *args, **kwargs):
        super().__init__(strategy, *args, **kwargs)
        self.products = [product]
    
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        
    def on_message(self, msg):
        if (msg['type'] == 'match'):
            if (msg['side'] == 'sell'):
                food = (msg['time'], msg['price'], 'ASK')
                self.feed(food)
                self.publish(food)
            elif (msg['side'] == 'buy'):
                food = (msg['time'], msg['price'], 'BID')
                self.feed(food)
                self.publish(food)
    
    def feed(self, data):
        self.strategy.calculate(data[0], float(data[1]), data[2])
        

class AllMesages(gdax.WebsocketClient):
    """
    Data feeder that uses the gdax API to feed real time data
    to a strategy.
    It filters the incoming messages to provide only 'match' messages.
    """    
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ['BTC-USD']

    def on_message(self, msg):
        print(msg)
    
    def feed(self, data):
        self.strategy.calculate(data[0], float(data[1]), data[2])
        
        
if __name__ == "__main__":
    f = AllMesages()
    f.start()
    