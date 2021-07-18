import json
from notiChan import notiChan
from strategy import exchangeCompare

if __name__ == "__main__":
    
    config = json.load(open("config.json"))
    iStrategy = exchangeCompare(config["tokenList"], config["exchangeList"])
    notifyBot = notiChan(config["teleToken"], config["teleChatID"], iStrategy)
    notifyBot.start()