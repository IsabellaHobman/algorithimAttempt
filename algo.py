import os
from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
import time
apiKey = os.environ.get('binanceApi')
apiSecret = os.environ.get('binanceSecret')
client = Client(apiKey, apiSecret)
btc_price = {'error':False}
def usdToBtc(btcAmount, usdAmount): #checks how much btc you could get for money
    return (btcAmount / usdAmount) - (usdAmount * 0.001)
def btcToUsd(usdAmount, btcAmount): #checks how much usd you could get for an amount of btc
    return (btcAmount * usdAmount) - (btcAmount * 0.001)
def usdToEth(usdAmount, priceOfEth):
    return (usdAmount * 0.999) / priceOfEth
def ethToUsd(ethAmount, priceOfEth):
    return (ethAmount * 0.999) * priceOfEth
def isProfitable(beforeAmount, afterAmount): #calculates percent difference
    if beforeAmount > afterAmount: # quick assertion we can throw out.
        return False
    elif ((afterAmount - beforeAmount ) / beforeAmount) * 100.0 > 0.1: # if the difference between is more than 0.1%, after fees it is profitable.
        return True
    else:
        return False
currentAmountForEth = 400.0
previousAmount = 0
soldAt = 0
boughtAt = 0
currentAmountForBtc = 10
firstEthFlag = True
firstBtcFlag = True
buyEthMode = True
buyBtcMode = True
test = ""
class CurrentPrice:
    storedValue = None
    def fire(self):
        return self.storedValue
    def setValue(self, value):
        self.storedValue = value
currently = CurrentPrice()
def btc_trade_history(msg):
    if msg['e'] != 'error':

        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
        currently.setValue(msg['c'])
    else:
        btc_price['error'] = True
bsm = BinanceSocketManager(client)
conn_key = bsm.start_symbol_ticker_socket('ETHUSDT', btc_trade_history)
bsm.start()

while True:
    test = currently.fire()
    if test != None:
        time.sleep(1)
        priceTest = float(test)
        if firstEthFlag: # We can't have profit on our first trade, so we throw this.
            print("Trading % 4f USD for % 4f eth, with %4f tax" % (currentAmountForEth, usdToEth(currentAmountForEth, priceTest), (currentAmountForEth * 0.001))) #this prints out the amount we trade
            previousAmount = currentAmountForEth * 0.999
            currentAmountForEth = usdToEth(currentAmountForEth, priceTest) #then we trade it. Not expected to make it to production.
            boughtAt = priceTest
            buyEthMode = False # We no longer can sell fiat, so we move it to sell mode for eth
            firstEthFlag = False # Likewise, we disable the first flag
        elif buyEthMode and isProfitable(priceTest, soldAt): # Else, can we turn more fiat from the amount of eth we have?
            print("I think that %4f is more than %4f, given that the current price is %4f" % (usdToEth(currentAmountForEth, priceTest), previousAmount, priceTest))
            print("Trading % 4f USD for % 4f eth" % (currentAmountForEth, usdToEth(currentAmountForEth, priceTest)))
            previousAmount = currentAmountForEth
            currentAmountForEth = usdToEth(currentAmountForEth, priceTest)
            boughtAt= priceTest
            buyEthMode = False
        if not buyEthMode and isProfitable(boughtAt , priceTest):
            print("I think that %4f is more than %4f, given that the current price is %4f" % (ethToUsd(currentAmountForEth, priceTest), previousAmount, priceTest))
            print("Trading %4f eth for %4f USD" % (currentAmountForEth, ethToUsd(currentAmountForEth, priceTest)))
            previousAmount = currentAmountForEth
            soldAt = priceTest
            currentAmountForEth = ethToUsd(currentAmountForEth, priceTest)
            buyEthMode = True
