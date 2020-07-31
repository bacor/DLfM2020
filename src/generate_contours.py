# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2020 Bas Cornelissen
# License: MIT
# -------------------------------------------------------------------
"""Code for generating the phrase contour datasets: CSV files stored in
the data/ directory.

Usage:  `python generate_contours.py [--genre]`
"""
import os
import glob
import logging
import hashlib
import pandas as pd
from .helpers import md5checksum
from .helpers import relpath
from .contours import extract_phrase_contours
from .contours import extract_random_contours

_CUR_DIR = os.path.dirname(__file__)
_ROOT_DIR = os.path.abspath(os.path.join(_CUR_DIR, os.path.pardir))
_OUTPUT_DIR = os.path.join(_ROOT_DIR, 'data', 'phrase-contours')
if not os.path.exists(_OUTPUT_DIR):
    os.makedirs(_OUTPUT_DIR)
_DATASETS_DIR = os.path.join(_ROOT_DIR, 'datasets')
_LOGGING_OPTIONS = dict(
    filemode='w',
    format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    level=logging.INFO)

    

def sample_subset(df, min_phrase_length: int = 4, num_contours: int = 3000,
    random_state: float = 0):
    # Filter out duplicate contours
    logging.info(f'Sampling a subset of contours')

    orig_size = len(df)
    unique_index = df.iloc[:, 4:].drop_duplicates().index
    logging.info(f'>  Removed {orig_size - len(unique_index)} duplicates; {len(unique_index)} contours left.')
    subset = df.loc[unique_index,]
    subset.loc[unique_index, :]

    # Remove short phrases
    is_long_enough = subset['phrase_length'] >= min_phrase_length
    logging.info(f'>  Found {sum(is_long_enough)} contours of length >= {min_phrase_length}')
    subset = subset[is_long_enough]

    # Return a random sample if possible
    if sum(is_long_enough) >= num_contours:
        logging.info(f'>  Sampling {num_contours} phrases (random_state={random_state}).')
        subset = subset.sample(num_contours, random_state=random_state)
    else:
        logging.info(f'>  Fewer than {num_contours} contours remain; returning {sum(is_long_enough)} contours.')
    subset.sort_index(inplace=True)
    return subset

def generate_contour_data(dataset_id: str, filepaths: list, 
    num_samples: int = 50, dataset_dir: str = _DATASETS_DIR):

    # Extract phrase contours
    phrase_contours = extract_phrase_contours(filepaths, 
        contour_id_tmpl=dataset_id+'-{i:0>5}',
        num_samples=num_samples)

    # Store csv file and log a checksum
    phrases_contours_fn = os.path.join(_OUTPUT_DIR, f'{dataset_id}-phrase-contours.csv')
    phrase_contours.to_csv(phrases_contours_fn)
    md5 = md5checksum(phrases_contours_fn)
    logging.info(f'Stored phrase contours to {relpath(phrases_contours_fn)}')
    logging.info(f'md5 checksum: {md5}')

    # Store a subset of phrases
    subset = sample_subset(phrase_contours)
    subset_fn = os.path.join(_OUTPUT_DIR, f'{dataset_id}-phrase-contours-subset.csv')
    subset.to_csv(subset_fn)
    md5 = md5checksum(subset_fn)
    logging.info(f'Stored a subset of phrase contours to {relpath(subset_fn)}')
    logging.info(f'md5 checksum: {md5}')

    # Extract random phrases
    mean_phrase_length = phrase_contours['phrase_length'].mean()
    logging.info(f'Extracting random contours with mean length lamb={mean_phrase_length:.2f}...' )
    random_contours = extract_random_contours(filepaths, 
        lam=mean_phrase_length,
        contour_id_tmpl=dataset_id+'-rand-{i:0>5}',
        num_samples=num_samples)
    mean_random_length = random_contours['phrase_length'].mean()
    logging.info(f'Mean length of random phrases: {mean_random_length:.2f}...' )

    # Store random phrases
    random_contours_fn = os.path.join(_OUTPUT_DIR, f'{dataset_id}-random-contours.csv')
    random_contours.to_csv(random_contours_fn)
    md5 = md5checksum(random_contours_fn)
    logging.info(f'Stored random contours to {relpath(random_contours_fn)}')
    logging.info(f'md5 checksum: {md5}')

    # Store a subset of random phrases
    random_subset = sample_subset(random_contours)
    random_subset_fn = os.path.join(_OUTPUT_DIR, f'{dataset_id}-random-contours-subset.csv')
    random_subset.to_csv(random_subset_fn)
    md5 = md5checksum(random_subset_fn)
    logging.info(f'Stored a subset of phrase contours to {relpath(random_subset_fn)}')
    logging.info(f'md5 checksum: {md5}')

def generate_gregobase_contour_data(genre, num_samples: int = 50,
    dataset_dir: str = _DATASETS_DIR):
    """Generate a phrase contour dataset from the GregoBase Corpus.
    We extract all chants of a certain genre in the Liber Usualis.
    
    Parameters
    ----------
    genre : [type]
        The liturgical genre, can be one of: `antiphons`, `hymns`, `alleluias`,
        `introits`, `communions`, `responsories`, `offertories`, `graduals`, 
        `kyries`, and `tracts`
    num_samples : int, optional
        The number of points at which the pitch is computed, by default 50
    dataset_dir : str, optional
        The directory in which to find the datasets, defaults to `datasets/`
    """    
    genres = {
        'antiphons': 'an',
        'hymns': 'hy',
        'alleluias': 'al',
        'introits': 'in',
        'communions': 'co',
        'responsories': 're',
        'offertories': 'of',
        'graduals': 'gr',
        'kyries': 'ky',
        'tracts': 'tr'
    }
    genre_key = genres[genre]
    dataset_id = f'liber-{genre}'
    log_fn = os.path.join(_OUTPUT_DIR, f'{dataset_id}.log')
    logging.basicConfig(filename=log_fn, **_LOGGING_OPTIONS)
    logging.info(f'Generating contour dataset: {dataset_id}')
    logging.info(f'Contours of {genre} from the Liber Usualis')

    # Load GregoBase Corpus
    csv_dir = os.path.join(_DATASETS_DIR, 'gregobasecorpus', 'csv')
    chants = pd.read_csv(os.path.join(csv_dir, 'chants.csv'), index_col=0)
    sources = pd.read_csv(os.path.join(csv_dir, 'sources.csv'), index_col=0)
    chant_sources = pd.read_csv(os.path.join(csv_dir, 'chant_sources.csv'))

    # Select the right subset
    liber_usualis = chant_sources.query('source==3').chant_id
    logging.info(f'Number of chants in the liber usualis: {len(liber_usualis)}')
    right_genre = chants.query(f"office_part == '{genre_key}'").index
    logging.info(f'Number of {genre}: {len(right_genre)}')
    subset = right_genre.intersection(liber_usualis)
    logging.info(f'Number of {genre} in the Liber Usualis: {len(subset)}')

    # Extract all contours
    pattern = os.path.join(_DATASETS_DIR, 'gregobasecorpus', 'gabc', '{idx:0>5}.gabc')
    filepaths = sorted([pattern.format(idx=idx) for idx in subset])
    
    generate_contour_data(dataset_id=dataset_id, filepaths=filepaths,
        dataset_dir=dataset_dir, num_samples=num_samples)

def main():
    """CLI for the generation of contours
    Usage:  `python generate_contours.py [genre]`
    """
    import argparse
    parser = argparse.ArgumentParser(description='Extract the contour data from a dataset')
    parser.add_argument('--genre', type=str, default='all', help=(
        'Genre of the dataset to generate, `antiphons`, `responsories`, '
        '`kyries`, etc. Use `--genre=all` (default) to generate datasets for all genres'
    ))
    args = parser.parse_args()
    if args.genre == 'all':
        genres = [
            'antiphons', 'hymns', 'alleluias', 'introits', 'communions',
            'responsories', 'offertories', 'graduals', 'kyries', 'tracts'
        ]
        for genre in genres:
            generate_gregobase_contour_data(genre)
    else:
        generate_gregobase_contour_data(args.genre)

if __name__ == '__main__':
    main()
    # generate_gregobase_contour_data('antiphons')