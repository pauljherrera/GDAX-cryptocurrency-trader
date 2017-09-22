# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:23:10 2017

@author: Paúl Herrera
"""

import sys
import gdax

from core.data_feeder import RealTimeFeeder
from core.strategy import DeviationStrategy
from core.trader import Trader    


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
    period = int(get_arg(2, 10))
    entry_std = float(get_arg(3, 1))
    exit_std = float(get_arg(4, 1))
    stop_loss = float(get_arg(5, 5))
    size = float(get_arg(6, 0.01))
      
    # Initializing objects.
    client = gdax.AuthenticatedClient(key, secret, passphrase)
    strategy = DeviationStrategy(period=period, entry_std=entry_std, 
                                 exit_std=exit_std, stop_loss=stop_loss)
    feeder = RealTimeFeeder(strategy)
    trader = Trader(client, product=product, size=0.01)
    strategy.trader = trader
    
    # Backtest.
    feeder.start()
    print('Connected and waiting for data')
    
    
    
    
