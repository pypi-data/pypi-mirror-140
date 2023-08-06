# Authors: Abhiket Gaurav, Artan Zandian, Macy Chan, Manju Abhinandana Kumar
# January 2022


from pylyrics2.extract_lyrics import extract_lyrics
from pylyrics2.clean_text import clean_text
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


def plot_cloud(
    song, file_path, max_font_size=30, max_words=120, background_color="black"
):
    """
    Creates a wordcloud of most occuring words in a string or list of strings

    Parameters
    ----------
    song: dictionary
        with artist as dictionary key and song_title as value. Both key and value are strings.
    file_path: str
        The location to save the file without file format
    max_font_size: int, optional
        maximum font size
    max_words: int, optional
        maximum number of words to be included in wordcloud
    background_color: str, optional
        background color

    Returns
    -------
    image
        A wordcloud image supported by matplotlib

    Example
    -------
    >>> from pylyrics2 import plot_cloud
    >>> plot_cloud(song, file_path, max_font_size=30, max_words=100, background_color='black')

    """
    try:
        # check input types
        if type(song) != dict:
            raise TypeError("song should be a variable of type dictionary.")
        if not (type(file_path) == str and type(background_color) == str):
            raise TypeError(
                "Both file_path and background_color should be of type string."
            )
        if not (type(max_font_size) == int and type(max_words) == int):
            raise TypeError(
                "Both max_font_size and max_words should be of type integer."
            )

        text = ""
        # Create a string of all song lyrics
        for artist, song_title in song.items():
            raw_lyrics = extract_lyrics(song_title, artist)
            clean_lyrics = clean_text(text=raw_lyrics)
            text += " " + clean_lyrics  # Adding space for the end of lyrics

        # plot the wordcloud
        wordcloud = WordCloud(
            max_font_size=max_font_size,
            max_words=max_words,
            background_color=background_color,
        ).generate(text)

        plt.imshow(wordcloud, interpolation="antialiased")
        plt.axis("off")

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # plt.savefig( file_path + ".png")
        plt.savefig((file_path + ".png"))

    except Exception as exp:
        print(exp)
        raise
