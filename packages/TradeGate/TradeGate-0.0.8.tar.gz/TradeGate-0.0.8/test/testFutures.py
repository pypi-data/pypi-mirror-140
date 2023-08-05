import unittest
import json
from TradeGates.TradeGate import TradeGate
import logging


class BinanceFuturesTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], 'Binance', sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    def testSymbolFuturesOrders(self):
        # self.log.info('\BTCUSDT Futures Orders: {}'.format(self.tradeGate.getAllFuturesOrders('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolFuturesOrders('BTCUSDT'))

    def testFuturesBalance(self):
        # self.log.info('\BTCUSDT Futures Balance: {}'.format(self.tradeGate.getFuturesBalance()))
        self.assertIsNotNone(self.tradeGate.getFuturesBalance())

    def testFuturesOrder(self):
        futuresOrderData = self.tradeGate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.002)

        result = self.tradeGate.makeFuturesOrder(futuresOrderData)
        self.log.info('\nFutures Order Result: {}'.format(result))

        self.assertIsNotNone(result, 'Problem in submiting futures order.')

    def testCancelingAllFututresOpenOrders(self):
        result = self.tradeGate.cancelAllSymbolFuturesOpenOrders('BTCUSDT')
        self.assertIsNotNone(result, 'Problem in canceling all futures orders')

    def testGetFuturesOpenOrders(self):
        # self.log.info('\nOrders: {}'.format(self.tradeGate.getOpenOrders('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getAllFuturesOpenOrders(), 'Problem in getting list of open orders without symbol.')
        self.assertIsNotNone(self.tradeGate.getAllFuturesOpenOrders('BTCUSDT'), 'Problem in getting list of open orders with symbol.')

    def testGetFutureOrder(self):
        futuresOrderData = self.tradeGate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.002)
        result = self.tradeGate.makeFuturesOrder(futuresOrderData)
        # self.log.info('\n\n{}'.format(result.orderId))
        order = self.tradeGate.getFuturesOrder('BTCUSDT', orderId=result.orderId)
        self.assertEqual(order.clientOrderId, result.clientOrderId)

        order = self.tradeGate.getFuturesOrder('BTCUSDT', localOrderId=result.clientOrderId)
        self.assertEqual(order.orderId, result.orderId)

    def testCancelingAllFuturesOpenOrders(self):
        futuresOrderData = self.tradeGate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'TAKE_PROFIT_MARKET', stopPrice=35000, quantity=0.002)
        result = self.tradeGate.makeFuturesOrder(futuresOrderData)

        result = self.tradeGate.cancellAllSymbolFuturesOrders('BTCUSDT', 1)

        openOrders = self.tradeGate.getAllFuturesOpenOrders('BTCUSDT')
        self.assertEqual(len(openOrders), 0, 'Problem in canceling all Open Orders')

    def testCancelingOrder(self):
        futuresOrderData = self.tradeGate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'TAKE_PROFIT_MARKET', stopPrice=35000, quantity=0.002)
        result = self.tradeGate.makeFuturesOrder(futuresOrderData)

        result = self.tradeGate.cancelFuturesOrder(symbol='BTCUSDT', localOrderId=result.clientOrderId)
        self.assertEqual(result.status, 'CANCELED', 'Problem in canceling specified Open Orders')

if __name__ == '__main__':
    unittest.main()