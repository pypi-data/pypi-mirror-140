# Authors: Abhiket Gaurav, Artan Zandian, Macy Chan, Manju Abhinandana Kumar
# January 2022
import re
from xmlrpc.client import Boolean


def clean_text(text, bool_contra_dict=True):
    """Cleans the text by removing special characters, html_tags, #tags, contaction words and convert everything to lower case.

    Parameters
    ----------
    text : str
        Text to clean.
    bool_contra_dict : Boolean
        A flag to clear contraction words

    Returns
    -------
    text
        Cleaned text.

    Examples
    --------
    >>> clean_text("Early optimization is the root of all evil!", False)
    'early optimization is the root of all evil'
    """
    try:
        # check input types
        if type(text) != str:
            raise TypeError("Text should be a variable of type string.")

        # check for blank string
        if len(text.strip()) == 0:
            raise ValueError("Blank text input")

        # check for blank string
        if type(bool_contra_dict) != Boolean:
            raise TypeError("bool_contra_dict should be a variable of type boolean.")

        if bool_contra_dict:
            contra_dict = {
                "'s": " is",
                "n't": " not",
                "'m": " am",
                "'ll": " will",
                "'d": " would",
                "'ve": " have",
                "'re": " are",
            }

            for key, value in contra_dict.items():
                if key in text:
                    text = text.replace(key, value)
                # lower case and remove special characters
        text = re.sub(r"[^a-zA-Z\s]", "", text, re.I | re.A)
        text = re.sub(r"https?:\/\/.\S+", "", text)
        text = re.sub(r"#", "", text)
        text = text.lower()
        return text

    except (TypeError, ValueError) as err:
        print(err)
        raise
