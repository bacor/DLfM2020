# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2020 Bas Cornelissen
# License: MIT
# -------------------------------------------------------------------
"""Functions for working with contours"""
import os
import numpy as np
import scipy.interpolate
import typing
import music21
from music21 import converter
import pandas as pd
import logging

from .random_segments import extract_random_segments_from_file

def interpolate_stream(stream: music21.stream.Stream, num_samples: int = 50, 
    dtype: typing.Any = int) -> np.array:
    """Returns an array of pitches interpolating a music21 Stream.
    The function computes the pitch at a given number equally spaced
    points in time. 
    
    Rests are ignored: we assume the note before a rest is extended 
    to fill the rest. If a phrase starts with a rest, this is discarded
    so the phrase starts on the first onset.
    
    Parameters
    ----------
    stream : music21.stream.Stream
        The stream (melody) to interpolate
    num_samples : int, optional
        The number of points at which the pitch is computed, by default 50
    dtype : typing.Any, optional
        The datatype of the array, defaults to int. (Only for microtonal
        music you would want to use floats)
    
    Returns
    -------
    np.array
        An array of length `num_samples` of pitches
    """
    duration = stream.quarterLength
    notes = stream.recurse().notes
    offsets = [float(n.offset) for n in notes]
    pitches = [n.pitch.ps for n in notes]
    
    # Deal with phrases starting with a rest
    if offsets[0] > 0:
        duration = duration - offsets[0]
        offsets = [x - offsets[0] for x in offsets]
    
    # Ensure the final note has the proper duration
    offsets.append(duration)
    pitches.append(pitches[-1])

    # Interpolate to previous note
    f = scipy.interpolate.interp1d(offsets, pitches, kind='previous')
    xs = np.linspace(0, duration, num_samples)
    ys = f(xs).astype(dtype)
    return ys

def normalized_contours(df: pd.DataFrame):
    """Extract a Numpy array of normalized pitch contours from a dataframe
    with pitch contours"""
    start_index = list(df.columns).index('0')
    pitches = df.iloc[:, start_index:].values
    means = pitches.mean(axis=1)
    normalized_pitches = pitches - means[:, np.newaxis]
    return normalized_pitches

def extract_phrases_from_file(filename: str) -> list:
    chant = converter.parse(filename)
    return chant.phrases

def extract_phrase_contours(filepaths: list, num_samples: int = 50,
    contour_id_tmpl: str = '{i:0>3}',
    extractor = extract_phrases_from_file,
    extractor_kwargs: dict = {}) -> pd.DataFrame:
    """Extract all phrase contours from an iterable of files.
    The song ids are extracted from the filenames automatically.
    
    Parameters
    ----------
    filepaths : list
        An iterable of file paths
    num_samples : int, optional
        The number of points at which the pitch is computed, by default 50
    contour_id_tmpl : str, optional
        A template string for the contour ids, for example: `nova{i:0>3}`.
        Defaults to `'{i:0>3}'`
    
    Returns
    -------
    pd.DataFrame
        A Dataframe with song ids, phrase numbers and the contours
    """
    contours = []
    song_ids = []
    phrase_numbers = []
    phrase_lengths = []
    phrase_durations = []
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        song_id = os.path.splitext(filename)[0]
        tmp_contours = []
        tmp_song_ids = []
        tmp_phrase_numbers = []
        tmp_phrase_lengths = []
        tmp_phrase_durations = []
        try:
            phrases = extractor(filepath, **extractor_kwargs)
            for i, phrase in enumerate(phrases):
                ys = interpolate_stream(phrase, num_samples=num_samples)
                tmp_contours.append(ys)
                tmp_song_ids.append(song_id)
                tmp_phrase_numbers.append(i)
                tmp_phrase_lengths.append(len(phrase.flat.notes))
                tmp_phrase_durations.append(float(phrase.quarterLength))
            
            # Only add phrases if all phrases could be extracted
            contours.extend(tmp_contours)
            song_ids.extend(tmp_song_ids)
            phrase_numbers.extend(tmp_phrase_numbers)
            phrase_lengths.extend(tmp_phrase_lengths)
            phrase_durations.extend(tmp_phrase_durations)
            logging.info(f'Extracted {len(phrases):0>2} contours from {filename}')
        except Exception as e:
            logging.warn(f'Skipping {song_id}: {e}')
    
    # Package the contours in a DataFrame
    df = pd.DataFrame(contours)
    df['song_id'] = song_ids
    df['phrase_num'] = phrase_numbers
    df['phrase_duration'] = phrase_durations
    df['phrase_length'] = phrase_lengths
    contour_ids = [contour_id_tmpl.format(i=i) for i in range(1, len(df)+1)]
    df['contour_id'] = contour_ids
    column_order = [
        'contour_id', 
        'song_id', 
        'phrase_num', 
        'phrase_length', 
        'phrase_duration']
    column_order += list(range(0, num_samples))
    return df[column_order].set_index('contour_id')

def extract_random_contours(filepaths: list, lam: float,
    num_samples: int = 50, contour_id_tmpl: str = '{i:0>3}', 
    random_seed: float = 0):
    np.random.seed(random_seed)
    return extract_phrase_contours(filepaths=filepaths, num_samples=num_samples,
        contour_id_tmpl=contour_id_tmpl, extractor=extract_random_segments_from_file,
        extractor_kwargs=dict(lam=lam))