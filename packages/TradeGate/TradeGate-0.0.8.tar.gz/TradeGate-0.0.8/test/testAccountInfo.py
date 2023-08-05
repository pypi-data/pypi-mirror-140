import unittest
import json
from TradeGates.TradeGate import TradeGate
import logging


class BinanceAccountInfoTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], 'Binance', sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    def testFullBalance(self):
        # self.log.info('\nFull Balance: {}'.format(self.tradeGate.getBalance()))
        self.assertIsNotNone(self.tradeGate.getBalance(), 'Assert fetching balance is not none')

    def testSingleCoinBalance(self):
        # self.log.info('\nCoin Balance: {}'.format(self.tradeGate.getBalance('BTC')))
        self.assertIsNotNone(self.tradeGate.getBalance('BTC'), 'Assert fetching single coin balance is not none')

    def testTradeHistory(self):
        # self.log.info('\nHistory: {}'.format(self.tradeGate.getSymbolTradeHistory('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolTradeHistory('BTCUSDT'), 'Assert trade history not none')


if __name__ == '__main__':
    unittest.main()