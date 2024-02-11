import json

import readings
import connector

if __name__ == "__main__":
    connectors = [connector.TelegramConnector]

    # Fetch config

    with open("config.json") as f:
        config = json.load(f)

    # Fetch readings
    readings_client = readings.Readings()
    readings_client.fetch()

    # Send readings over to connectors
    for c in connectors:
        connector_obj = c(config)
        connector_obj.send(readings_client)
