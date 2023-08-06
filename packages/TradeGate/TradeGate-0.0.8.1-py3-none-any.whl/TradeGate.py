import json
from Exchanges import BinanceExchange
from Utils import DataHelpers


class TradeGate():
    def __init__(self, configDict, spot=False, sandbox=False):
        exchangeName = configDict['exchangeName']
        exchangeClass = self.getCorrectExchange(exchangeName)
        if sandbox:
            self.apiKey = configDict['credentials']['test']['spot']['key']
            self.apiSecret = configDict['credentials']['test']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['test'], sandbox=True)
        else:
            self.apiKey = configDict['credentials']['main']['spot']['key']
            self.apiSecret = configDict['credentials']['main']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['test'], sandbox=False)

    def getBalance(self, asset='', futures=False):
        return self.exchange.getBalance(asset, futures)

    def getSymbolTradeHistory(self, symbol):
        return self.exchange.SymbolTradeHistory(symbol)

    @staticmethod
    def getCorrectExchange(exchangeName):
        if exchangeName == 'Binance':
            return BinanceExchange.BinanceExchange

    def createAndTestOrder(self, symbol, side, orderType, quantity=None, price=None, timeInForce=None, stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None,
                            newClientOrderId=None):
        currOrder = DataHelpers.OrderData(symbol.upper(), side.upper(), orderType.upper())

        if not quantity is None:
            currOrder.setQuantity(quantity)

        if not price is None:
            currOrder.setPrice(price)

        if not timeInForce is None:
            currOrder.setTimeInForce(timeInForce)

        if not stopPrice is None:
            currOrder.setStopPrice(stopPrice)

        if not icebergQty is None:
            currOrder.setIcebergQty(icebergQty)

        if not newOrderRespType is None:
            currOrder.setNewOrderRespType(newOrderRespType)
        
        if not recvWindow is None:
            currOrder.setRecvWindow(recvWindow)

        if not newClientOrderId is None:
            currOrder.setNewClientOrderId(newClientOrderId)

        if not self.exchange.isOrderDataValid(currOrder):
            raise Exception('Incomplete data provided.')

        self.exchange.testOrder(currOrder)

        return currOrder

    def makeOrder(self, orderData):
        return self.exchange.makeOrder(orderData)

    def getSymbolOrders(self, symbol):
        return self.exchange.getSymbolOrders(symbol)

    def getOpenOrders(self, symbol=None):
        return self.exchange.getOpenOrders(symbol)

    def getOrder(self, symbol, orderId=None, localOrderId=None):
        return self.exchange.getOrder(symbol, orderId, localOrderId)

    def cancelAllSymbolOpenOrders(self, symbol):
        return self.exchange.cancelAllSymbolOpenOrders(symbol)

    def cancelSymbolOpenOrder(self, symbol, orderId=None, localOrderId=None):
        return self.exchange.cancelSymbolOpenOrder(symbol, orderId, localOrderId)

    def getTradingFees(self):
        return self.exchange.getTradingFees()

    def getSymbolAveragePrice(self, symbol):
        return self.exchange.getSymbolAveragePrice(symbol)
        
    def getSymbolLatestTrades(self, symbol, limit=None):
        return self.exchange.getSymbolLatestTrades(symbol, limit)

    def getSymbolTickerPrice(self, symbol):
        return self.exchange.getSymbolTickerPrice(symbol)

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=None, futures=False, BLVTNAV=False, convertDateTime=False, doClean=False):
        return self.exchange.getSymbolKlines(symbol, interval, startTime, endTime, limit, futures, BLVTNAV, convertDateTime, doClean)

    def getExchangeTime(self):
        return self.exchange.getExchangeTime()

    def getSymbolFuturesOrders(self, symbol):
        return self.exchange.getSymbolFuturesOrders(symbol)

    def getFuturesBalance(self):
        return self.exchange.getFuturesBalance()

    def createAndTestFuturesOrder(self, symbol, side, orderType, positionSide=None, timeInForce=None, quantity=None, reduceOnly=False, price=None, newClientOrderId=None,
                                    stopPrice=None, closePosition=False, activationPrice=None, callbackRate=None, workingType=None, priceProtect=False, newOrderRespType=None,
                                    recvWindow=None):
        currOrder = DataHelpers.futuresOrderData(symbol.upper(), side.upper(), orderType.upper())

        if not positionSide is None:
            currOrder.setPositionSide(positionSide)
        
        if not timeInForce is None:
            currOrder.setTimeInForce(timeInForce)

        if not quantity is None:
            currOrder.setQuantity(quantity)

        if not reduceOnly is None:
            currOrder.setReduceOnly(reduceOnly)

        if not price is None:
            currOrder.setPrice(price)

        if not newClientOrderId is None:
            currOrder.setNewClientOrderId(newClientOrderId)

        if not stopPrice is None:
            currOrder.setStopPrice(stopPrice)

        if not closePosition is None:
            currOrder.setClosePosition(closePosition)

        if not activationPrice is None:
            currOrder.setActivationPrice(activationPrice)

        if not callbackRate is None:
            currOrder.setCallbackRate(callbackRate)

        if not workingType is None:
            currOrder.setWorkingType(workingType)

        if not priceProtect is None:
            currOrder.setPriceProtect(priceProtect)

        if not newOrderRespType is None:
            currOrder.setNewOrderRespType(newOrderRespType)
        
        if not recvWindow is None:
            currOrder.setRecvWindow(recvWindow)

        if not self.exchange.isFuturesOrderDataValid(currOrder):
            raise Exception('Incomplete data provided.')

        return currOrder

    def makeFuturesOrder(self, futuresOrderData):
        return self.exchange.makeFuturesOrder(futuresOrderData)

    def cancelAllSymbolFuturesOpenOrders(self, symbol):
        return self.exchange.cancelAllSymbolFuturesOpenOrders(symbol)

    def cancelFuturesOrder(self, symbol, orderId=None, localOrderId=None):
        return self.exchange.cancelFuturesOrder(symbol, orderId, localOrderId)

    def getAllFuturesOpenOrders(self, symbol=None):
        return self.exchange.getAllFuturesOpenOrders(symbol)

    def getFuturesOrder(self, symbol, orderId=None, localOrderId=None):
        return self.exchange.getFuturesOrder(symbol, orderId, localOrderId)

    def cancellAllSymbolFuturesOrders(self, symbol, countdownTime):
        return self.exchange.cancellAllSymbolFuturesOrders(symbol, countdownTime)

    def getAllOpenFuturesOrders(self, symbol=None):
        return self.exchange.getAllOpenFuturesOrders(symbol)

    def changeInitialLeverage(self, symbol, leverage):
        return self.exchange.changeInitialLeverage(symbol, leverage)

    def changeMarginType(self, symbol, marginType):
        return self.exchange.changeMarginType(symbol, marginType)

    def changePositionMargin(self, symbol, amount, marginType):
        return self.exchange.changePositionMargin(symbol, amount, marginType)

    def getPosition(self):
        return self.exchange.getPosition()

    def spotBestBidAsks(self, symbol=None):
        return self.exchange.spotBestBidAsks(symbol)

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        return self.exchange.getSymbolOrderBook(symbol, limit, futures)

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        return self.exchange.getSymbolRecentTrades(symbol, limit, futures)