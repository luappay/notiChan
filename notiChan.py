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