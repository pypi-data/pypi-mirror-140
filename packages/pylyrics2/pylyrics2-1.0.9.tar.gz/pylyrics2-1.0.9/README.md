# pylyrics2  

[![ci-cd](https://github.com/UBC-MDS/pylyrics/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/pylyrics/actions/workflows/ci-cd.yml)
[![Documentation Status](https://readthedocs.org/projects/pylyrics/badge/?version=latest)](https://pylyrics.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/UBC-MDS/pylyrics2/branch/master/graph/badge.svg?token=pjbS2ZPk2h)](https://codecov.io/gh/UBC-MDS/pylyrics2)

A Python package to extract and analyze lyrics

- Authors: Abhiket Gaurav, Artan Zandian, Macy Chan, Manju Abhinandana Kumar

<br>

### Overview

This package allows users to extract and analyze lyrics effortlessly. With pylyrics2 users can download songs attribute datasets from Kaggle, extract lyrics and generate a word cloud.

<br>

### Functions

---
<br>

| Function Name | Input | Output | Description |
|-----------|------------|---------------|------------------|
| download_data | `dataset`, `file_path`, `columns` | Pandas Dataframe | Downloads dataset from `kaggle dataset` and extract `columns` from csv file |
| extract_lyrics | `song_title`, `artist` | String | Extracts song lyrics of a song `song_title` by `artist` |
| clean_text | `text`, `bool_contra_dict` | String |  Cleans up the `lyrics` by removing special characters, html tags, #tags, contraction words and convert everything to lower case |
| plot_cloud | `song`, `file_path`, `max_font_size`, `max_words`, `background_color` | Image | Creates a word cloud image of most occuring words of a song/songs by an artist |

<br>

### Our Package in the Python Ecosystem

---
There exist similar packages Python. However, this package is more holistic, in the sense that it downloads the lyrics through APIs, cleans the text, and then makes the word cloud. There are packages which does one of these steps. This package takes care of all the steps. Of the many other similar packages, the following are examples that come close: [PyLyrics](https://pypi.org/project/PyLyrics/), [Cloud-Lyrics](https://github.com/lorenza12/Cloud-Lyrics) and [deezer.io](https://deezer.io/a-new-way-to-look-at-an-artist-from-lyrics-to-wordclouds-christmas-special-56a854cb4e77#.op1gx82h4)

<br>

### Installation

---

```bash
pip install pylyrics2

```

<br>

### Features

---
The `pylyrics2` packages contains the following four functions:  

1. `download_data()` The download data function downloads dataset from Kaggle, extracts the given columns from csv file and creates a dataframe.

2. `extract_lyrics()` The extract lyrics function, extracts the lyrics from API for a song title and artist and saves it as a dataframe with columns song title, artist and lyrics.

3. `clean_text()` The lyrics extracted from `extract_lyrics()` are not clean. It removes special characters, html tags, #tags, contraction words and convert everything to lower case to get a cleaned paragraph.

4. `plot_cloud()` The plot cloud function creates a word cloud of most occurring words in a song/songs by an artist.

<br>

### Dependencies

---

- python = ^3.9
- pandas = ^1.2.3
- kaggle = ^1.5.12
- wordcloud = ^1.8.1
- matplotlib = ^3.5.1
- beautifulsoup4 = ^4.10.0

<br>

### Usage

The `pylyrics2` package is a visual way to find prominent word used in a lyrics. Given a song title and artist's name, this package will show the word that is used most in that lyrics (or a group of lyrics)

#### Downloading and Selecting

The first function in our package is the `download_data()`. Here you will input your `kaggle dataset` and the columns to be extracted into a Pandas DataFrame with `columns` argument.

To use the Kaggle API, sign up for a Kaggle account at [Kaggle](https:/www.kaggle.com). Then go to the 'Account' tab of your user profile (https://www.kaggle.com/<username\>/account) and select 'Create API Token'. This will trigger the download of kaggle.json, a file containing your API credentials. Place this file in the location `~/.kaggle/kaggle.json`. The function will automatically read your Kaggle credentials from the above path.
  
```python
from pylyrics2 import download_data as dd
# Example dataset: Spotify Song Attributes  
dataset = "geomack/spotifyclassification"
file_path = "data/spotify_attributes"
columns = ["song_title", "artist"]
# Extract columns 
dd.download_data(dataset, "data/spotify_attributes", ["song_title", "artist"])
```

#### Extracting Lyrics

The `extract_lyrics()` function gets the `song_title` and `artist` name, checks validity and avialability of the combination, and extracts the lyrics for that song in a raw string format with header, footer etc which needs to be cleaned in order to create a human-readable text.  

```python
from pylyrics2 import extract_lyrics as el
# extracting lyrics 
raw_lyrics = el.extract_lyrics("22", "Taylor Swift")
```

#### Cleaning

Our `clean_text()` function is straightforward. It turns the raw lyrics into a human-readable text.

```python
from pylyrics2 import clean_text as ct
# Clean the extracted raw lyrics (text)
clean_lyrics = ct.clean_text(raw_lyrics)
```

#### Creating WordCloud

WordCloud is an artistic rendering of the most frequent words in a text document. A higher occurrence for a word is translated into a larger text size.  
At this stage, we have helper functions to facilitate the extraction and cleaning of lyrics. The `plot_cloud()` function accepts a **dictionary** with `artist` as dictionary key and `song_title` as values. It will then extract the lyrics for all songs in the dictionary and saves a WordCould of the most occurring terms in the `file_path` provided by the user. The WordClould parameters to be set are self-explanatory: `max_font_size`, `max_word` and `background_color`.

```python
from pylyrics2 import plot_cloud as pc
# plotting and saving WordCloud
song = { "Taylor Swift": "all too well", "Adele" : "Hello" }
file_path = "data/wordcloud"
pc.plot_cloud(song, file_path, max_font_size=30, max_words=100, background_color='black')
```

<br>

### Documentation

---
The official documentation is hosted on Read the Docs: [here](https://pylyrics.readthedocs.io/en/latest/)

<br>

## Contributors

---
The names of core development team is listed below.

|           Name          |   GitHub Handle   |
|:-----------------------:|:-----------------:|
|      Abhiket Gaurav     |      abhiket      |
|      Artan Zandian      |     artanzand     |
|        Macy Chan        |      macychan     |
| Manju Abhinandana Kumar | manju-abhinandana |

We welcome and recognize all contributions. Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

### License

`pylyrics2` was created by Group 2. It is licensed under the terms of the MIT license.

### Credits

`pylyrics2` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
