To invest with the Deviation Strategy on GDAX, run the file gdax_cmd.py from the terminal using the following parameters:

$python gdax_cmd.py [Currency] [Period] [Entry Standard Deviation] [Exit Standard Deviation] [Stop Loss] [Size of the trades]

For example, to buy 0.5 Bitcoins every time the price is under 2 standard deviations of the last 100 ticks, and exit again when the  the price is 1 standard deviation above, placing a Stop Loss in a 20$ level under the entry price, you can type:

$python gdax_cmd.py BTC-USD 100 2 1 20 0.5
