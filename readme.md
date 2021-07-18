# notiChan

# Using Telegram Bot To Check For Arbitrage Opportunities

Some time back, a friend and I were discussing arbitrage opportunities in DEXes due to the nature of how it works. I went on to create some simple scripts to test those hypotheses and integrated them into a Telegram Bot to notify when the conditions were met.

Recently, I talked to another friend about it and he was asking me to share it. Finally, managed to take some time out to clean it up and post it.

# What does this do?

The bot queries and compares the price information from different exchanges. It will send a telegram message if the price differential is above 5%. 

This is a simple version 1 that allows anyone to easily build on top of it. Scroll down for further elaboration.

# Setting up

### Dependencies:

[CoinGecko API Wrapper](https://github.com/man-c/pycoingecko), [Telegram Bot Library](https://github.com/python-telegram-bot/python-telegram-bot)

### Configurations:

The configurations you will need are;

- tokenList - List of tokens to track
- exchangeList - List of exchanges to compare
- teleChatID - List of telegram chats to broadcast the message into. You can find your chat ID by looking at the URL when you use Telegram Web
- teleToken - The token for the Telegram bot, which is generated from [Botfather](https://core.telegram.org/bots/)

The config should look something like this;

```json
{
    "tokenList": ["chainlink", "ethereum"],
    "exchangeList": ["binance", "uniswap"],
    "teleChatID": 000012345,
    "teleToken": "telegram bot token"
}
```

### To run:

Enter the folder and call [main.py](http://main.py)

```powershell
python main.py
```

# How does it work?

There are 3 components to the implementation;

- config.json - Configuration file
- [notiChan.py](http://notichan.py) - Telegram bot implementation
- [strategy.py](http://strategy.py) - Hypotheses/Strategy to test/apply

The goal is to decouple each component as much as possible such that they can be run independently and easily interchangeable.

### config.json

Elaborated above

### [notiChan.py](http://notichan.py)

A simple telegram bot that executes a strategy input and sends a notification (telegram message) if there is a positive response. [Strategy Design Pattern](https://en.wikipedia.org/wiki/Strategy_pattern#:~:text=In%20computer%20programming%2C%20the%20strategy,family%20of%20algorithms%20to%20use.) is used to implement this. 

```python
from telegram import Bot
import time

class notiChan():

    def __init__(self, teleToken, broadcastIDs, iStrategy):
        
        self.iStrategy = iStrategy
        
        self.bot = Bot(teleToken)
        self.broadcastIDs = broadcastIDs
        
        if type(broadcastIDs) != list:
            self.broadcastIDs = [broadcastIDs]
            
    def start(self):
        
        while True:
            
            for notify, msg in self.iStrategy.run():
                if notify:
                    for chatID in self.broadcastIDs:
                        self.bot.send_message(chatID, msg)
                        
            time.sleep(30)
```

As shown in the code notiChan's responsibility is solely to run the given strategy, and sends a message if requested to. Anyone can implement their own iStrategy and change the behavior of the bot - as long as the run() method is applied. 

Note that the cycle is set to every 30secs, this can be changed to suit your needs. 

### [strategy.py](http://strategy.py)

This is where the main action is happening. 

```python
class exchangeCompare():
    
    def __init__(self, coinList, exchangeList):
        
        self.cg = CoinGeckoAPI()
        self.coinList = coinList
        self.exchangeList = exchangeList
        
    def checkPrice(self, coinID, exchangeID):
        
        result = self.cg.get_exchanges_tickers_by_id(id=exchangeID, coin_ids=coinID, vs_currencies='usd')
        
        for pair in result["tickers"]:
            if "USDT" == pair["target"]:
                return pair["last"]
        
    def checkSpread(self, coinID, exchangeList):
        
        priceList = {}
        for exchange in exchangeList:
            price = self.checkPrice(coinID, exchange)
            priceList[price] = exchange
            
        lowestPrice = min(priceList.keys())
        lowestExchange = priceList[lowestPrice]
        
        highestPrice = max(priceList.keys())
        highestExchange = priceList[highestPrice]
        
        spread = highestPrice - lowestPrice
        
        result = {
            "token": coinID,
            "spread": spread,
            "pSpread": spread/lowestPrice,
            "high": {
                "price": highestPrice,
                "exchange": highestExchange
            },
            "low": {
                "price": lowestPrice,
                "exchange": lowestExchange
            }
        }
        
        return result
    
    def run(self):
        
        for token in self.coinList:
            
            result = self.checkSpread(token, self.exchangeList)
            if result["pSpread"] > 0.05:
                
                msg = f"""Spread greater than 5% for {result["token"]}, pairs;\nExchange: {result["high"]["exchange"]}\nPrice: {result["high"]["price"]}\nExchange: {result["low"]["exchange"]}\nPrice: {result["low"]["price"]}"""
                yield 1, msg
        
        yield 0, ""
```

This iStrategy queries information using the coin gecko API and calculates the largest spread for the target token. If the spread is above a certain threshold (in this case 5%), return an alert message. The message should show up in the Telegram chat like this;

![notiChan%201a56a6976dfa4f7ba1d039f3b927a628/Untitled.png](notiChan%201a56a6976dfa4f7ba1d039f3b927a628/Untitled.png)