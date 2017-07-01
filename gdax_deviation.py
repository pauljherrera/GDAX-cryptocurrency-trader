# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:23:10 2017

@author: Paúl Herrera
"""

import gdax
import pandas as pd

from data_feeder import HistoricalDataFeeder, RealTimeFeeder
from strategy import DeviationStrategy
from trader import PaperTrader, RealTimeTrader    


if __name__ == '__main__':
    # Settig variables.
    key = ''
    secret = ''
    passphrase = ''
    product = 'BTC-USD'
    startDate = '2017-06-19'
    endDate = '2017-06-26'
  
    # Setting client and data.
    data = pd.read_csv('BTC-USD_20170619-20170626.csv', index_col=0)
    
    # Initializing objects.
    client = gdax.AuthenticatedClient(key, secret, passphrase)
    strategy = DeviationStrategy(period=10, entryStd=1, exitStd=1)
    feeder = RealTimeFeeder(strategy)
    trader = PaperTrader()
    strategy.subscribe(trader)
    
    # Backtest.
    feeder.start()
    
    
    
    
