# Authors: Abhiket Gaurav, Artan Zandian, Macy Chan, Manju Abhinandana Kumar
# January 2022

import os
import pandas as pd
import kaggle


def download_data(dataset, file_path, columns):
    """
    Downloads dataset from kaggle to filepath and creates a dataframe with input columns

    Parameters
    ----------
    dataset: str
        kaggle dataset name to download
    file_path: str
        location to save the file
    columns: list
        list of columns to create a dataframe

    Returns
    -------
    df:
        A dataframe with the given column names

    Example
    -------
    from pylyrics2 import download_data
    download_data("geomack/spotifyclassification", "data/spotify_attributes", ["song_title", "artist"])
    spotify_df = download_data("geomack/spotifyclassification", "data/spotify_attributes", ["song_title", "artist"])
    """
    try:

        if not (type(dataset)) == str:
            raise TypeError("Dataset should be of type string.")
        if not (type(file_path)) == str:
            raise TypeError("File_path should be of type string.")
        if not (type(columns)) == list:
            raise TypeError("The column names should be of type list")
        if not (len(columns)) == 2:
            raise TypeError("Two columns should be retrieved")

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            dataset,
            path=file_path,
            unzip=True,
        )

        df = pd.read_csv((file_path + "/" + str(os.listdir(file_path).pop())))

        if set(columns).issubset(df.columns):
            df = df[columns]
        else:
            raise ValueError("Incorrect column names, please check again")

        return df

    except (TypeError, ValueError) as req:
        print(req)
        raise
