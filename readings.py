import datetime as dt
import re

import requests


class Readings:
    """A class that fetches (and formats) the readings"""

    def __init__(self):
        self._readings = None

    def fetch(self, day=None):
        """Fetches the readings for the corresponding day"""
        if day is None:
            day = dt.datetime.now().date()
        response = requests.get(
            f"https://api.aelf.org/v1/messes/{day:%Y-%m-%d}/france")

        if response.status_code >= 300:
            raise RuntimeError(
                f"Request failed with status code {response.status_code}")
        self._data = response.json()

    @classmethod
    def _format_single_reading(cls, reading):
        """Reading formated as a dict. Just append the stuff together"""

        strings_to_append = [reading.get("intro_lue"), 
                             reading.get("ref"), reading.get("contenu")]

        return "\n".join([cls.strip_html_tags(x) 
                          for x in strings_to_append if x is not None])

    @staticmethod
    def strip_html_tags(s):
        return re.sub('<[^<]+?>', '', s)

    def __str__(self):
        if self._data is None:
            raise RuntimeError("Readings not fetched yet")

        return "\n\n\n".join([
            self._format_single_reading(x) for x in
            self._data["messes"][0]["lectures"]
        ])
