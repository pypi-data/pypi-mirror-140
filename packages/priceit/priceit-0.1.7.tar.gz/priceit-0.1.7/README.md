# PRICEIT

Author: David WANG

Version 0.1.7

- To extract realtime or history price data of stocks or crypto currencies. 
(Please note this package is based on free API (e.g. Yahoo Finance). There may be a little time lag (seconds or minutes) for some market.)
- To extract the latest full list of stock tickers in NASDAQ, NYSE and AMEX.
- To extract the financial statements.

## Installation:
```bash
pip install priceit
```

## Usage:
(1) To get realtime TSLA price

```python
from priceit import *

ticker = 'TSLA'
print(getprice(ticker))
```
Result:
```
['TSLA', 1049.61, 'Delayed Quote', '2022-01-14 16:00:04']
```
(Sample above is taken during weekend, when the market is close. So it shows 'Delayed Quote'. Try this when market is open, and you can get realtime quote (almost realtime). Please allow seconds or minutes time lag for certain market.)

(2) To get history daily price of BTC-USD from 2022-01-12 to 2022-01-14

```python
from priceit import *

ticker = 'BTC-USD'
startdate = '2022-01-12'
enddate = '2022-01-14'
print(histprice(ticker, startdate, enddate))
```
Result:
```
{'currency': 'USD', 'symbol': 'BTC-USD', 'exchangeName': 'CCC', 'data': {'timestamp': ['2022-01-12', '2022-01-13', '2022-01-14'], 'volume': [33499938689, 47691135082, 23577403399], 'high': [44135.3671875, 44278.421875, 43346.6875], 'low': [42528.98828125, 42447.04296875, 41982.6171875], 'close': [43949.1015625, 42591.5703125, 43099.69921875], 'open': [42742.1796875, 43946.7421875, 42598.87109375], 'adjclose': [43949.1015625, 42591.5703125, 43099.69921875]}}
```

(3) To get full list of stock ticker in NASDAQ, NYSE and AMEX

```python
from priceit import *

exchange = 'NASDAQ'
print(tickerlist(exchange))
```
Result:
```
{'symbol': ['AAPL', 'MSFT',...], 'name': ['Apple Inc. Common Stock', 'Microsoft Corporation Common Stock',...]}
```

(4) To get financial statements

```python
from priceit import *

p = priceit()
p.ticker = 'AAPL'
print(p.statements('Q'))  # 'Q' for quarter report; 'A' for annual report
```
Result:
```
{'income_statement': {},'balance_sheet': {}, 'cash_flow':{}}
```
## Notes:
- This project is being built up. More functions will be added.
- If to get realtime price, please limit your frequency of data extraction. 
- After getting the full list of stock tickers, you can save it in your local disk so as to save the network resources.

## About the Author
I am currently in Grade 11 (as of 1st half of 2022). I have great interests in AI trading and real world simulation with C++, Java and Python. I am summarizing my free data sources in this project. And hopefully this can save some of your time in data extraction. 