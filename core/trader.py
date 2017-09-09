# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:56:48 2017

@author: forex
"""

import pandas as pd
# from winsound import Beep


class Trader():
    """
    Abstract Base Class. A trader receives the signals from
    the strategy.
    """
    def notify(self, msg):
        raise NotImplementedError
        
    def publish(self, msg):
        for s in self.subscribers:
            s.receive(msg)        

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)


class PaperTrader(Trader):
    """
    Saves the signals in a pandas dataframe.
    """
    def __init__(self):
        super().__init__()
        self._columns = ['time', 'type', 'price']
        self.trades = pd.DataFrame(columns=self._columns)
        self.subscribers = []
        
    
    def notify(self, msg):
        self.trades = pd.concat([self.trades, pd.DataFrame([msg], 
                                              columns=self._columns)])
        self.publish(msg)
                    
    
class RealTimeTrader(Trader):
    """
    Trades in real time through the gdax API.
    It takes a client object as first initialization parameter, so a
    'sandbox' client could be passed.
    """
    def __init__(self, client, product='BTC-USD', 
                 orders_type='market', size=0.01):
        self.client = client
        self.product = product
        self.size = size
        self.orderId = 0
        self.order_type = orders_type
        self.subscribers = []
    
    def check_pending_orders(self):
        pending_orders = len(self.client.get_orders()[0])
        if pending_orders == 0:
            return False
        elif pending_orders == 1:
            return True
        else:
            print('Error: more than one pending order.')
        
    def notify(self, msg):
        print('\n\n')
        print(msg)
        print('\n\n')
#        Beep(500, 500)
        
        if self.order_type == 'market':
            if msg[1] == 'BUY':
                r = self.client.buy(price=msg[2], size=self.size, 
                                    product_id=self.product)
                self.orderId = r['id']
            elif msg[1] == 'CLOSE':
                r = self.client.sell(price=msg[2], size=self.size, 
                                     product_id=self.product)
        
        if self.order_type == 'limit':
            if msg[1] == 'BUY':
                r = self.client.buy(price=self.client.get_product_ticker(self.product)['bid'], 
                                    type='limit', 
                                    size=self.size,
                                    product_id=self.product)
                self.orderId = r['id']
            elif msg[1] == 'CLOSE':
                r = self.client.sell(price=self.client.get_product_ticker(self.product)['ask'], 
                                    type='limit', 
                                    size=self.size,
                                    product_id=self.product)
        
