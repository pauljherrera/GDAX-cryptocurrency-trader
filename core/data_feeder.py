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
    
    
    def feed(self):
        raise NotImplementedError
    
        

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
    

        
if __name__ == "__main__":
    f = AllMesages()
    f.start()
    