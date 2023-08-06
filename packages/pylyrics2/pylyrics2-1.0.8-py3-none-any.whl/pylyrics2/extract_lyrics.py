# Authors: Abhiket Gaurav, Artan Zandian, Macy Chan, Manju Abhinandana Kumar
# Date: 2022-01-14

import requests
from bs4 import BeautifulSoup
import re


def extract_lyrics(song_title, artist):
    """
    Extracting lyrics for a song

    Parameters
    ----------
    song_title : string
        Title of the song
    artist : string
        Artist of the song

    Returns
    ----------
    lyrics : string
        Return lyrics of song

    Example
    -------
    >>> extract_lyrics("22", "Taylor Swift")
    >>> "[Verse 1]\nIt feels like a perfect night\nTo dress u..."

    """
    try:

        if song_title == "" or artist == "":
            raise ValueError("Empty input")

        if not (type(song_title) == str and type(artist) == str):
            raise TypeError(
                "Invalid column type, song title and artist have to be strings"
            )

        lyrics = ""
        url = (
            "https://genius.com/"
            + artist.replace(" ", "-")
            + "-"
            + song_title.replace(" ", "-")
            + "-lyrics"
        )
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="lyrics-root")

        if not results:
            print("url: " + url)
            raise ValueError("Song not found")

        job_elements = results.find_all("span")
        for i in range(len(job_elements)):
            if job_elements[i].text != "":
                lyrics += job_elements[i].text
        lyrics = re.sub(r"(\w)([A-Z])", r"\1 \2", lyrics)
        lyrics = re.sub(r"(\w)([0-9])", r"\1 \2", lyrics)
        return lyrics

    except (ValueError, TypeError) as err:
        raise
