# Trade Gate
[![Run Unit Tests](https://github.com/RastinS/tradeGate/actions/workflows/main.yml/badge.svg?branch=master&event=push)](https://github.com/RastinS/tradeGate/actions/workflows/main.yml)
[![PyPI version](https://img.shields.io/pypi/v/TradeGate.svg)](https://pypi.python.org/pypi/TradeGate)
[![Python version](https://img.shields.io/pypi/pyversions/TradeGate)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An algorithmic trading library to use as a gateway to different exchanges.

## How to install
Use this github repository and running ```python setup.py install```, or using pip:
```bash
pip install TradeGate
```

## How to use
Use with a config file in json format. Your config file should look like this:
```json
{
    "Binance": 
    {
        "exchangeName": "Binance",
        "credentials": 
        {
            "main": 
            {
                "futures": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                },
                "spot": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                }
            },
            "test": 
            {
                "futures": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                },
                "spot": 
                {
                    "key": "API-KEY",
                    "secret": "API-SECRET"
                }
            }
        }
    }
}

```
You should read this config file as json and give the desired exchange's informations to the main class initializer. Use ```sandbox``` argument to connect to the testnets of exchanges (if it exsits). This is shown below:
```python
from TradeGate import TradeGate
import json

with open('/Users/rustinsoraki/Documents/Projects/tradeGate/config.json') as f:
    config = json.load(f)
    
gate = TradeGate(config['Binance'], sandbox=True)

print(gate.getSymbolTickerPrice('BTCUSDT'))
```
