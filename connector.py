import abc

import requests

import readings

class Connector(abc.ABC):

    MAX_MSG_SIZE = float('inf')

    def __init__(self, config):
        self.config = config
    
    @abc.abstractmethod
    def send(self, what: readings.Readings):
        pass

    def send(self, what: readings.Readings):

        current_batch = []
        current_batch_length = 0

        for element in what.get_chunks():
            current_str = element.as_telegram()
            l = len(current_str)

            if l > self.MAX_MSG_SIZE:
                raise NotImplemented("Sending chunks longer than one message"
                                     "is not supported")

            if l + current_batch_length > self.MAX_MSG_SIZE:
                self._send("".join(current_batch))
                current_batch, current_batch_length = [], 0

            current_batch.append(current_str)
            current_batch_length += l

        if current_batch:
            self._send("".join(current_batch))


class TestConnector(Connector):
    def _send(self, what):
        print("\n" + "=" * 30)
        print(what)

class TelegramConnector(Connector):

    MAX_MSG_SIZE = 4096

    def _send(self, what: str):
        """Raw sends a message with no regard for length"""
        result = requests.post(
            f"https://api.telegram.org/bot{self.config['telegram']['api_key']}/sendMessage", 
            json={"chat_id": self.config["telegram"]["chat_id"],
                   "text": what,
                   "parse_mode": "HTML"}).json()

        if not result["ok"]:
            raise RuntimeError("Telegram api send failure: `" + 
                            result["description"] + "`")
