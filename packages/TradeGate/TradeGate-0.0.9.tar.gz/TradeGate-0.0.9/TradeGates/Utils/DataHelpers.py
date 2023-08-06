import time


class OrderData():
    def __init__(self, symbol, side, orderType):
        self.symbol = symbol
        self.side = side
        self.orderType = orderType

        self.timeInForce = None
        self.quantity = None
        self.quoteOrderQty = None
        self.price = None
        self.newClientOrderId = None
        self.stopPrice = None
        self.icebergQty = None
        self.newOrderRespType = None
        self.recvWindow = None
        self.timestamp = None

    def setTimeInForce(self, timeInForce):
        self.timeInForce = timeInForce

    def setQuantity(self, quantity):
        self.quantity = quantity

    def setQuoteOrderQty(self, quoteOrderQty):
        self.quoteOrderQty = quoteOrderQty
    
    def setPrice(self, price):
        self.price = price
    
    def setNewClientOrderId(self, newClientOrderId):
        self.newClientOrderId = newClientOrderId

    def setStopPrice(self, stopPrice):
        self.stopPrice = stopPrice

    def setIcebergQty(self, icebergQty):
        self.icebergQty = icebergQty
    
    def setNewOrderRespType(self, newOrderRespType):
        self.newOrderRespType = newOrderRespType

    def setRecvWindow(self, recvWindow):
        self.recvWindow = recvWindow
    
    def setTimestamp(self):
        self.timestamp = time.time()
        
class futuresOrderData():
    def __init__(self, symbol, side, orderType):
        self.symbol = symbol
        self.side = side
        self.orderType = orderType

        self.positionSide = None
        self.timeInForce = None
        self.quantity = None
        self.reduceOnly = None
        self.price = None
        self.newClientOrderId = None
        self.stopPrice = None
        self.closePosition = None
        self.activationPrice = None
        self.callbackRate = None
        self.workingType = None
        self.priceProtect = None
        self.newOrderRespType = None
        self.recvWindow = None

    def setPositionSide(self, positionSide):
        self.positionSide = positionSide

    def setTimeInForce(self, timeInForce):
        self.timeInForce = timeInForce

    def setQuantity(self, quantity):
        self.quantity = quantity

    def setReduceOnly(self, reduceOnly):
        self.reduceOnly = reduceOnly
    
    def setPrice(self, price):
        self.price = price
    
    def setNewClientOrderId(self, newClientOrderId):
        self.newClientOrderId = newClientOrderId

    def setStopPrice(self, stopPrice):
        self.stopPrice = stopPrice

    def setClosePosition(self, closePosition):
        self.closePosition = closePosition

    def setActivationPrice(self, activationPrice):
        self.activationPrice = activationPrice

    def setCallbackRate(self, callbackRate):
        self.callbackRate = callbackRate

    def setWorkingType(self, workingType):
        self.workingType = workingType

    def setPriceProtect(self, priceProtect):
        self.priceProtect = priceProtect
    
    def setNewOrderRespType(self, newOrderRespType):
        self.newOrderRespType = newOrderRespType

    def setRecvWindow(self, recvWindow):
        self.recvWindow = recvWindow
        