import datetime as dt
from time import sleep
import logging
import json
import os

from connector import TelegramConnector

class PassionSnippet:
    BASE_PATH = "passion"
    def __init__(self, filename, when):
        self.filename = os.path.join(self.BASE_PATH, filename)
        self.when = when
    
    def read(self):
        with open(self.filename, "r") as f:
            return f.read()

if __name__ == "__main__":
    
    today = dt.datetime.now()
    tomorrow = dt.datetime.now() + dt.timedelta(days=1)
    # build queue
    queue = [
        PassionSnippet("1-arrest.txt", today.replace(hour=22, minute=17)),
        PassionSnippet("2-peter1.txt", today.replace(hour=23, minute=23)),
        PassionSnippet("3-hanne.txt", today.replace(hour=23, minute=48)),
        PassionSnippet("4-peter2.txt", tomorrow.replace(hour=6, minute=33)),
        PassionSnippet("5-pilate1.txt", tomorrow.replace(hour=7, minute=43)),
        PassionSnippet("6-flagellation.txt", tomorrow.replace(hour=9, minute=51)),
        PassionSnippet("7-pilate2.txt", tomorrow.replace(hour=11, minute=54)),
        PassionSnippet("8-inri.txt", tomorrow.replace(hour=12, minute=48)),
        PassionSnippet("9-clothes.txt", tomorrow.replace(hour=13, minute=11)),
        PassionSnippet("10-mary.txt", tomorrow.replace(hour=14, minute=28)),
        PassionSnippet("11-passing.txt", tomorrow.replace(hour=15, minute=2)),
        PassionSnippet("12-soldiers.txt", tomorrow.replace(hour=17, minute=18)),
        PassionSnippet("13-joseph.txt", tomorrow.replace(hour=18, minute=57))
    ]

    with open("config.json") as f:
        config = json.load(f)
    connector = TelegramConnector(config)

    for reading in queue:
        print(f"Waiting until {reading.when.isoformat()}")
        while dt.datetime.now() < reading.when:
            sleep(30)

        print(f"Delivering reading")

        connector._send(reading.read())
