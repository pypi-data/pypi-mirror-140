import unittest
import json
from TradeGates.TradeGate import TradeGate
import logging


class BinanceMarketInfoTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    @unittest.skip
    def testTradingFees(self):
        # self.log.info('\nTrading Fees: {}'.format(self.tradeGate.getTradingFees()))
        self.assertIsNotNone(self.tradeGate.getTradingFees(), 'Problem in fetching trading fees.')

    def testAveragePrice(self):
        # self.log.info('\BTCUSDT Average Price: {}'.format(self.tradeGate.getSymbolAveragePrice('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolAveragePrice('BTCUSDT'), 'Problem in fetching symbol average price.')

    def testLatestTrades(self):
        # self.log.info('\nLatest Trades For BTCUSDT: {}'.format(self.tradeGate.getSymbolLatestTrades('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolLatestTrades('BTCUSDT'), 'Problem in fetching latest trades.')

    def testTickerPrice(self):
        # self.log.info('\n"BTCUSDT" Ticker Price: {}'.format(self.tradeGate.getSymbolTickerPrice('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolTickerPrice('BTCUSDT'), 'Problem in fetching symbol\'s ticker price')
    
    def testKlines(self):
        # self.log.info('\n"BTCUSDT" Ticker Price: {}'.format(self.tradeGate.getSymbolKlines('BTCUSDT', '1m', limit=10)))
        data = self.tradeGate.getSymbolKlines('BTCUSDT', '15m', limit=100, futures=True, doClean=True, convertDateTime=True)
        self.log.info('\n')
        for candle in data:
            self.log.info(candle)
        self.log.info('\n')
        self.assertIsNotNone(data, 'Problem in fetching spot market candle data.')
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 100, 'Length of spot market candle data is incorrect.')
        self.assertIsNotNone(self.tradeGate.getSymbolKlines('BTCUSDT', '15m', limit=100, futures=True), 'Problem in fetching futures candle data.')

    def testExchangeTime(self):
        self.assertIsNotNone(self.tradeGate.getExchangeTime(), 'Problem in fetching exchange time. Probably connectivity issues.')


if __name__ == '__main__':
    unittest.main()