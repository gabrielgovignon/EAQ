import abc

import requests


class Connector(abc.ABC):

    def __init__(self, config):
        self.config = config
    
    @abc.abstractmethod
    def send(self, what: str):
        pass


class TelegramConnector(Connector):

    MAX_MSG_SIZE = 4096

    def send(self, what: str):
        for start in range(0, len(what), self.MAX_MSG_SIZE):
            self._send(what[start: start+self.MAX_MSG_SIZE])
    
    def _send(self, what: str):
        """Raw sends a message with no regard for length"""
        result = requests.post(
            f"https://api.telegram.org/bot{self.config['telegram']['api_key']}/sendMessage", 
            json={"chat_id": self.config["telegram"]["chat_id"], "text": what}).json()

        if not result["ok"]:
            raise RuntimeError("Telegram api send failure: `" + 
                            result["description"] + "`")
