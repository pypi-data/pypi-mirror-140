import unittest
import json
from TradeGates.TradeGate import TradeGate
from Utils.DataHelpers import OrderData
import logging


class BinanceOrderingTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], 'Binance', sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    def testNewTestOrder(self):
        try:
            res = self.tradeGate.createAndTestOrder('BTCUSDT', 'SELL', 'LIMIT', timeInForce='GTC', quantity=0.002, price=49500)
        except Exception as e:
            self.fail('Problem in order data')

    def testNewTestOrderBadOrderType(self):
        try:
            res = self.tradeGate.createAndTestOrder('BTCUSDT', 'SELL', 'LINIT', timeInForce='GTC', quantity=0.002, price=49500)
        except Exception as e:
            return
        
        self.fail('Problem in validating order data')

    def testNewOrder(self):
        try:
            verifiedOrder = self.tradeGate.createAndTestOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000, timeInForce='GTC')
        except Exception as e:
            self.fail('Problem in order data: {}'.format(str(e)))

        try:
            result = self.tradeGate.makeOrder(verifiedOrder)
            # self.log.info('\nOrder status: {}'.format(result))
        except Exception as e:
            self.fail('Problem in making order: {}'.format(str(e)))

    def testGetOrders(self):
        # self.log.info('\nOrders: {}'.format(self.tradeGate.getSymbolOrders('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolOrders('BTCUSDT'), 'Problem in getting list of all orders')

    def testGetOpenOrders(self):
        # self.log.info('\nOrders: {}'.format(self.tradeGate.getOpenOrders('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getOpenOrders(), 'Problem in getting list of open orders without symbol.')
        self.assertIsNotNone(self.tradeGate.getOpenOrders('BTCUSDT'), 'Problem in getting list of open orders with symbol.')

    def testGetOrder(self):
        try:
            verifiedOrder = self.tradeGate.createAndTestOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000, timeInForce='GTC')
            result = self.tradeGate.makeOrder(verifiedOrder)
        except Exception as e:
            self.fail('Problem in making order: {}'.format(str(e)))
        
        order = self.tradeGate.getOrder('BTCUSDT', orderId=result['orderId'])
        self.assertEqual(order['clientOrderId'], result['clientOrderId'])

        order = self.tradeGate.getOrder('BTCUSDT', localOrderId=result['clientOrderId'])
        self.assertEqual(order['orderId'], result['orderId'])

        self.tradeGate.cancelSymbolOpenOrder('BTCUSDT', orderId=result['orderId'])

    def testCancelingAllOpenOrders(self):
        self.testNewOrder()
        result = self.tradeGate.cancelAllSymbolOpenOrders('BTCUSDT')
        # self.log.info('\n{}'.format(result))

        openOrders = self.tradeGate.getOpenOrders('BTCUSDT')
        self.assertEqual(len(openOrders), 0, 'Problem in canceling all Open Orders')

    def testCancelingOrder(self):
        try:
            verifiedOrder = self.tradeGate.createAndTestOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000, timeInForce='GTC')
            result = self.tradeGate.makeOrder(verifiedOrder)
        except Exception as e:
            self.fail('Problem in making order: {}'.format(str(e)))
        result = self.tradeGate.cancelSymbolOpenOrder(symbol='BTCUSDT', orderId=result['orderId'])
        self.assertEqual(result['status'], 'CANCELED', 'Problem in canceling specified Open Orders')

        try:
            verifiedOrder = self.tradeGate.createAndTestOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000, timeInForce='GTC')
            result = self.tradeGate.makeOrder(verifiedOrder)
        except Exception as e:
            self.fail('Problem in making order: {}'.format(str(e)))
        result = self.tradeGate.cancelSymbolOpenOrder(symbol='BTCUSDT', localOrderId=result['clientOrderId'])
        self.assertEqual(result['status'], 'CANCELED', 'Problem in canceling specified Open Orders')


if __name__ == '__main__':
    unittest.main()