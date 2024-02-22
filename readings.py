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
        self.text = self.strip_html_tags(text)
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

    def __init__(self, spacing: int = 1):
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
        self._day = day
        response = requests.get(
            f"https://api.aelf.org/v1/messes/{day:%Y-%m-%d}/france")

        if response.status_code >= 300:
            raise RuntimeError(
                f"Request failed with status code {response.status_code}")
        self._data = response.json()

    @classmethod
    def _format_single_reading(cls, reading: dict):
        """Yields the format blocks for a single reading"""
        if reading["type"] == "psaume":
            return cls._format_psalm(reading)
        else:
            return cls._format_normal_reading(reading)

    @classmethod
    def _format_psalm(cls, reading: dict):
        
        # Psalm ref
        if matches := re.match("^(?:Ps )?(\d+)", reading["ref"]):
            yield Chunk(f"Psaume {matches.group(1)}", Formatting.BOLD)
        else:
            yield Chunk(reading["ref"], Formatting.BOLD)

        yield SpacingChunk()
        yield Chunk("R/ " + reading["refrain_psalmique"], Formatting.ITALIC)
        yield SpacingChunk(2)

        for sentence in reading["contenu"].split("\n"):
            yield Chunk(sentence)
            yield SpacingChunk()

    @classmethod
    def _format_normal_reading(cls, reading: dict):
        yield Chunk(reading["intro_lue"], Formatting.BOLD)
        yield SpacingChunk(1)
        yield Chunk(reading["ref"], Formatting.ITALIC)
        yield SpacingChunk(2)

        for sentence in reading["contenu"].split("\n"):
            stripped_sentence = sentence.strip()

            if stripped_sentence and stripped_sentence not in \
                {"– Acclamons la Parole de Dieu.", 
                 "– Parole du Seigneur."}:
                yield Chunk(stripped_sentence + ' ')

    def get_chunks(self):
        """Yields the chunks to be displayed"""

        for x in self._header():
            yield x
        yield SpacingChunk(2)

        for reading in self._data["messes"][0]["lectures"]:
            for c in self._format_single_reading(reading):
                yield c
            yield SpacingChunk(2)

    def _header(self):
        # Date
        info = self._data["informations"]

        num = str(self._day.day) if self._day.day > 1 else "1er"
        month = ["janvier", "février", "mars", "avril", "mai", "juin", 
                 "juillet", "août", "septembre", "octobre", "novembre",
                 "décembre"][self._day.month - 1]

        jour = ["lundi", "mardi", "mercredi", "jeudi", "vendredi",
                "samedi", "dimanche"][self._day.weekday()]

        yield Chunk(f"{self._get_colour_emoji(info['couleur'])} "
                    f"{jour.capitalize()} {num} {month} {self._day.year}")

        if jour != "dimanche" and info["fete"] != "Solennit\u00e9"\
            and info["semaine"]:
            yield SpacingChunk()
            yield Chunk(info["semaine"])

        if info["jour_liturgique_nom"] != "de la f\u00e9rie":
            yield SpacingChunk()
            yield Chunk(info["jour_liturgique_nom"])

    def _get_colour_emoji(self, colour_ref):
        return {
            "rouge": "🔴",
            "vert": "🟢",
            "blanc": "⚪",
            "violet": "🟣"
        }[colour_ref]
