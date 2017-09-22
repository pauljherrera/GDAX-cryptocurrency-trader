# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:56:48 2017

@author: forex
"""

import pandas as pd

import threading

from time import sleep
# from winsound import Beep


                    
    
class Trader:
    """
    Trades in real time through the gdax API.
    It takes a client object as first initialization parameter, so a
    'sandbox' client could be passed.
    """
    def __init__(self, client, product='BTC-USD', 
                 size=0.01, monitor=True):
        self.client = client
        self.product = product
        self.size = size
        self.pending_limit_order_flag = False
        self.last_order_id = None
        if monitor:
            thread = threading.Thread(target=self.monitor_pending_orders, args=())
            thread.daemon = True                            
            thread.start()
        
    
    def check_pending_orders(self):
        """
        Checks if the last order is still pending. If the last limit order 
        status turns to 'done', the method toggles the pending_limit_order_flag.
        """
        if self.last_order_id and self.pending_limit_order_flag:
            try:
                status = self.client.get_order(self.last_order_id)['status']
                if status == 'done':
                    self.pending_limit_order_flag = False
            except:
                pass

            
    def monitor_pending_orders(self, time=30):
        while True:
            print("Monitoring pending orders.")
            if self.pending_limit_order_flag == True:
                self.check_pending_orders()
            sleep(time)
        
    def send_market_order(self, _type, price):
        """
        Sends a market order. It receives a price parameter to avoid
        calling to the API for the current price of the asset.
        _type: str. "BUY"/"CLOSE"
        price: str. 
        """
        print('\n\n')
        print(_type, price)
        print('\n\n')
        
        if _type == 'BUY':
            self.client.buy(price=price, size=self.size, 
                            product_id=self.product)
        elif _type == 'CLOSE':
            self.client.sell(price=price, size=self.size, 
                             product_id=self.product)
                
                
    def send_limit_order(self, _type, price):
        print('\n\n')
        print(_type, price)
        print('\n\n')                
        
        # Places a buy order if there's no pending limit order.
        if (_type == 'BUY'):
            if (self.pending_limit_order_flag == False):
                price = str(round(float(self.client.get_product_ticker('BTC-USD')['ask']) - 0.01, 2))
                r = self.client.buy(price=price, type='limit', 
                                    size=self.size, product_id=self.product)
                print(r)
                self.last_order_id = r['id']
                self.pending_limit_order_flag = True
            else:
                self.client.cancel_order(self.last_order_id)
                self.pending_limit_order_flag = False
                print("Cancelling an unfilled order")
            
        # Places a sell order if there's no pending limit order.   
        elif (_type == 'CLOSE'):
            if (self.pending_limit_order_flag == False):
                price = str(round(float(self.client.get_product_ticker('BTC-USD')['bid']) + 0.01, 2))
                r = self.client.sell(price=price, type='limit', 
                                     size=self.size, product_id=self.product)
                self.last_order_id = r['id']
                self.pending_limit_order_flag = True
            else:
                self.client.cancel_order(self.last_order_id)
                self.pending_limit_order_flag = False
                print("Cancelling an unfilled order")



