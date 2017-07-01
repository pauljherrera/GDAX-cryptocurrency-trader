# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 15:42:36 2017

@author: Paúl Herrera
"""

import numpy as np
import pandas as pd
import datetime as dt
import time


class Strategy():
    """
    Abstract Base Class for strategies.
    """
    def __init__(self):
        self.subscribers = []
        self.accountState = 'CLOSE'
        self.ask = [0]
        self.bid = [0]
    
    def calculate(self):
        raise NotImplementedError
    
    
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
        self.lastTimestamp = dt.datetime(1975,1,1)

    def calculate(self, _time, tick, _type):
        """
        Main method. It has the core logic of the strategy.
        """
        try:
            _time = dt.datetime.strptime(_time, "%Y-%m-%dT%H:%M:%S.%fZ")\
                          .replace(microsecond=0)
        except ValueError:
            _time = pd.to_datetime(_time)            
           
        
        # Updating data.
        if (_type == 'ASK') and (tick != self.ask[-1]):
            self.ask.append(tick)
        elif (_type == 'BID') and (tick != self.bid[-1]) \
        and (_time >= self.lastTimestamp + dt.timedelta(seconds=1)):
            self.bid.append(tick)
            self.lastTimestamp = _time
            
        # Mean calculations.
        if (len(self.bid) >= self.period + 1) and (_type == 'BID'):
            mean = np.mean(self.bid[-self.period:])
            std = np.std(self.bid[-self.period:])
            # Entry logic.
            if self.accountState == 'CLOSE':
                highStd = mean + self.entryStd * std
                lowStd = mean - self.entryStd * std
                if tick > highStd:
                    self.send_signal((_time, 'SELL', tick))
                elif tick < lowStd:
                    self.send_signal((_time, 'BUY', tick))
            # Exit logic.
            elif self.accountState != 'CLOSE':
                highStd = mean + self.exitStd * std
                lowStd = mean - self.exitStd * std
                if (tick > highStd) & (self.accountState == 'BUY'):
                    self.send_signal((_time, 'CLOSE', tick))
                elif (tick < lowStd) & (self.accountState == 'SELL'):
                    self.send_signal((_time, 'CLOSE', tick))
                    
    
    def send_signal(self, signal):
        for s in self.subscribers:
            s.notify(signal)
        self.accountState = signal[1]

                
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)