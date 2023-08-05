import unittest
import json
from TradeGates.TradeGate import TradeGate
import logging


class BinanceMarketInfoTest(unittest.TestCase):
    def setUp(self):
        with open('./config.json') as f:
            config = json.load(f)

        self.tradeGate = TradeGate(config['Binance'], 'Binance', sandbox=True)
        loglevel = logging.INFO
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger(__name__)

    @unittest.skip
    def testTradingFees(self):
        # self.log.info('\nTrading Fees: {}'.format(self.tradeGate.getTradingFees()))
        self.assertIsNotNone(self.tradeGate.getTradingFees())

    def testAveragePrice(self):
        # self.log.info('\BTCUSDT Average Price: {}'.format(self.tradeGate.getSymbolAveragePrice('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolAveragePrice('BTCUSDT'))

    def testLatestTrades(self):
        # self.log.info('\nLatest Trades For BTCUSDT: {}'.format(self.tradeGate.getSymbolLatestTrades('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolLatestTrades('BTCUSDT'))

    def testTickerPrice(self):
        # self.log.info('\n"BTCUSDT" Ticker Price: {}'.format(self.tradeGate.getSymbolTickerPrice('BTCUSDT')))
        self.assertIsNotNone(self.tradeGate.getSymbolTickerPrice('BTCUSDT'))
    
    def testKlines(self):
        # self.log.info('\n"BTCUSDT" Ticker Price: {}'.format(self.tradeGate.getSymbolKlines('BTCUSDT', '1m', limit=10)))
        # data = self.tradeGate.getSymbolKlines('BTCUSDT', '15m', limit=10, futures=False, doClean=True, convertDateTime=True)
        # for candle in data:
        #     self.log.info(candle)
        self.assertIsNotNone(self.tradeGate.getSymbolKlines('BTCUSDT', '15m', limit=10))
        self.assertIsNotNone(self.tradeGate.getSymbolKlines('BTCUSDT', '15m', limit=10, futures=True))

    def testExchangeTime(self):
        self.assertIsNotNone(self.tradeGate.getExchangeTime())


if __name__ == '__main__':
    unittest.main()