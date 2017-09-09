# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:23:10 2017

@author: Paúl Herrera
"""

import sys
import gdax

from core.data_feeder import HistoricalDataFeeder, RealTimeFeeder
from core.strategy import DeviationStrategy
from core.trader import PaperTrader, RealTimeTrader    


def get_arg(index, default):
    try:
        return sys.argv[index]
    except IndexError:
        return default


if __name__ == '__main__':
    # Settig variables.
    key = '71ecfc8e4e610dd4111b5b268ead6ca5'
    secret = '4c/r3Ak/pT0+Llqr54Myx8lPjuVlKXf0TM3eQSqXCIeXjgJn92atSA+is+CARSjBYzr0Gyx7k53ALH5LRGERmA=='
    passphrase = 'bz4w6b9z7f'
    product = get_arg(1, 'BTC-USD')
#    startDate = '2017-06-19'
#    endDate = '2017-06-26'
    period = int(get_arg(2, 10))
    entry_std = float(get_arg(3, 0.5))
    exit_std = float(get_arg(4, 0.5))
    stop_loss = float(get_arg(5, 20))
    size = float(get_arg(6, 0.01))
  
    # Setting client and data.
#    data = pd.read_csv('BTC-USD_20170619-20170626.csv', index_col=0)
    
    # Initializing objects.
    client = gdax.AuthenticatedClient(key, secret, passphrase)
    strategy = DeviationStrategy(period=period, entry_std=entry_std, exit_std=exit_std)
    feeder = RealTimeFeeder(strategy)
    trader = RealTimeTrader(client, size=0.01, orders_type='limit')
    
    # Subscriptions.
    strategy.subscribe(trader)
    
    # Backtest.
    feeder.start()
    print('Connected and waiting for data')
    
    
    
    
