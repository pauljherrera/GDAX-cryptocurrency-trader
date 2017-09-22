# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:42:36 2017

@author: Paúl Herrera
"""

import numpy as np
import pandas as pd
import datetime as dt


class Strategy():
    """
    Abstract Base Class for strategies.
    """
    def __init__(self, trader=None):
        self.subscribers = []
        self.account_state = 'CLOSE'
        self.ask = [0]
        self.bid = [0]
        self.trader = trader
    
    def calculate(self):
        raise NotImplementedError
    
    
class DeviationStrategy(Strategy):
    """
    Trading strategy that enters and exits the market when the price
    deviates X standard deviations from the Y period mean. 
    """
    def __init__(self, period=20, entry_std=2, exit_std=1, stop_loss=10):
        super().__init__()
        self.period = period
        self.entryStd = entry_std
        self.exitStd = exit_std
        self.stop_loss = stop_loss
        self.lastAskTimestamp = dt.datetime(1975,1,1)
        self.lastBidTimestamp = dt.datetime(1975,1,1)

    def calculate(self, _time, tick, _type):
        """
        Main method. It has the core logic of the strategy.
        """        
        try:
            _time = dt.datetime.strptime(_time, "%Y-%m-%dT%H:%M:%S.%fZ")\
                          .replace(microsecond=0)
        except ValueError:
            _time = pd.to_datetime(_time)            
           
        # Updating data and entry logic.
        if (_type == 'ASK') \
        and (tick != self.ask[-1]) \
        and (_time >= self.lastAskTimestamp + dt.timedelta(seconds=1)):
            
            print(_time, tick, _type)
            # Updating ask data.
            self.ask.append(tick)
            self.lastAskTimestamp = _time
            # Entry logic.
            if (self.account_state == 'CLOSE') \
            and (len(self.ask) >= self.period + 1):
                mean = np.mean(self.ask[-self.period:])
                std = np.std(self.ask[-self.period:])
                lowStd = mean - self.entryStd * std
                print('Ask Std Dev: {} - {}'.format(lowStd, tick))
                
                if tick < lowStd:
                    self.trader.send_limit_order('BUY', tick)
                    self.account_state = 'BUY'
                    # Setting Stop Loss.
                    self.current_stop_loss = tick - self.stop_loss
            
            
        elif (_type == 'BID') \
        and (tick != self.bid[-1]) \
        and (_time >= self.lastBidTimestamp + dt.timedelta(seconds=1)):
            
            print(_time, tick, _type)
            # Updating bid data.
            self.bid.append(tick)
            self.lastBidTimestamp = _time
            # Exit logic.
            if (self.account_state == 'BUY') \
            and (len(self.bid) >= self.period + 1):
                mean = np.mean(self.bid[-self.period:])
                std = np.std(self.bid[-self.period:])
                highStd = mean + self.exitStd * std
                print('Bid Std Dev: {} - {}'.format(highStd, tick))
                
                # Profitable exit.
                if tick > highStd:
                    self.trader.send_limit_order('CLOSE', tick)
                    self.account_state = 'CLOSE'
                    
                # Stop Loss exit
                if (tick < self.current_stop_loss):
                    self.trader.send_market_order('CLOSE', tick)
                    self.account_state = 'CLOSE'
                    print("Stop Loss hit")              
    
        
        
        