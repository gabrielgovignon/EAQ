import datetime as dt
import re
from enum import Enum
import abc

import requests


class Formatting(Enum):
    NONE = 0
    BOLD = 1
    ITALIC = 2


class ChunkBase(abc.ABC):
    @abc.abstractmethod
    def as_telegram(self):
        pass


class Chunk(ChunkBase):
    """Represents a line of a reading, stuff that should be atomic"""
    def __init__(self, text: str, format: Formatting = Formatting.NONE):
        self.text = self.strip_html_tags(text).replace("\n", "")
        self.format = format

    @staticmethod
    def strip_html_tags(s):
        return re.sub('<[^<]+?>', '', s)

    def as_telegram(self):
        if self.format == Formatting.BOLD:
            return f"<b>{self.text}</b>"
        elif self.format == Formatting.ITALIC:
            return f"<i>{self.text}</i>"
        else:
            return self.text

class SpacingChunk(ChunkBase):

    def __init__(self, spacing: int = 2):
        self.spacing = spacing

    def as_telegram(self):
        return "\n" * self.spacing


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
    def _format_single_reading(cls, reading: dict):
        """Yields the format blocks for a single reading"""

        yield Chunk(reading["ref"], Formatting.BOLD)
        yield SpacingChunk()

        if reading.get("refrain_psalmique"):
            yield Chunk(reading["refrain_psalmique"], Formatting.BOLD)
            yield SpacingChunk(1)
            yield Chunk(reading["ref_refrain"], Formatting.ITALIC)
            yield SpacingChunk(2)

        for sentence in reading["contenu"].split("\n"):
            yield Chunk(sentence)
            yield SpacingChunk(1)
    
    def get_chunks(self):
        """Yields the chuncks to be displayed"""
        for reading in self._data["messes"][0]["lectures"]:
            for c in self._format_single_reading(reading):
                yield c
            yield SpacingChunk(4)

