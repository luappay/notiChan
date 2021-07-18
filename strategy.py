from pycoingecko import CoinGeckoAPI

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