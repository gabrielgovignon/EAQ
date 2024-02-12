import json
import sys
import datetime as dt

import readings
import connector

if __name__ == "__main__":
    connectors = [connector.TelegramConnector]

    # Fetch config

    with open("config.json") as f:
        config = json.load(f)

    # Fetch readings
    readings_client = readings.Readings()
    date = dt.datetime.now().date() if len(sys.argv) <= 1 \
        else dt.date.fromisoformat(sys.argv[1])
    readings_client.fetch(date)

    # Send readings over to connectors
    for c in connectors:
        connector_obj = c(config)
        connector_obj.send(readings_client)
