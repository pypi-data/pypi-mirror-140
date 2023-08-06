import unittest
import json
from TradeGates.TradeGate import TradeGate
import logging


class BinanceAccountInfoTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    def testFullBalance(self):
        # self.log.info('\nFull Balance: {}'.format(self.tradeGate.getBalance()))
        self.assertIsNotNone(self.tradeGate.getBalance(), 'Fetching balance is none.')

    def testSingleCoinBalance(self):
        # self.log.info('\nCoin Balance: {}'.format(self.tradeGate.getBalance('BTC')))
        self.assertIsNotNone(self.tradeGate.getBalance('BTC'), 'Fetching single coin balance is none.')

    def testTradeHistory(self):
        # self.log.info('\nHistory: {}'.format(self.tradeGate.getSymbolTradeHistory('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolTradeHistory('BTCUSDT'), 'Trade history is none.')


if __name__ == '__main__':
    unittest.main()