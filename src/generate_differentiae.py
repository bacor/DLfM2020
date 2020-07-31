# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2020 Bas Cornelissen
# License: MIT
# -------------------------------------------------------------------
"""Code for generating the differentia-antiphon connections: CSV files stored in
the data/differentiae directory.

Usage: `python -m src.generate_differentiae.py`
"""
import os
import logging
import pandas as pd
import chant21
from music21 import converter
from .helpers import relpath
from .helpers import md5checksum
from .cantus_filters import *

_CUR_DIR = os.path.dirname(__file__)
_ROOT_DIR = os.path.abspath(os.path.join(_CUR_DIR, os.path.pardir))
_DATA_DIR = os.path.join(_ROOT_DIR, 'data')
_DATASETS_DIR = os.path.join(_ROOT_DIR, 'datasets')
_LOGGING_OPTIONS = dict(
    filemode='w',
    format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    level=logging.INFO)

@log_filter
def filter_chants_not_ending_on_euouae(chants, logger=None):
    """Exclude all chants that don't end on variants of EUOUAE"""
    euouae = 'S?e ?u ?o ?u ?a ?e$'
    ends_on_euouae = chants.full_text_manuscript.str.contains(euouae, case=False)
    return chants[ends_on_euouae == True]

def filter_antiphons(chants):
    opts = dict(logger=lambda msg: logging.info(f' . {msg}'))
    chants = filter_chants_without_volpiano(chants, **opts)
    chants = filter_chants_without_notes(chants, **opts)
    chants = filter_chants_without_simple_mode(
        chants, include_transposed=False, **opts)
    chants = filter_chants_without_full_text(chants, **opts)
    chants = filter_chants_where_incipit_is_full_text(chants, **opts)
    chants = filter_chants_by_genre(chants, include=['genre_a'], **opts)
    chants = filter_chants_not_ending_on_euouae(chants, **opts)

    chants = filter_chants_not_starting_with_G_clef(chants, **opts)
    chants = filter_chants_with_F_clef(chants, **opts)
    chants = filter_chants_with_nonvolpiano_chars(chants, **opts)
    chants = filter_chants_without_word_boundary(chants, **opts)
    return chants

def extract_connections(antiphons, force_source=False, min_length=3,
                        max_length=15):
    """
    Extract differentia-antiphon connections from a dataframe with antiphons.
    The volpiano and full_text_manuscript columns from the dataframe are 
    converted to music21. Then the last ``max_length`` notes of the differentia
    and the first ``max_length`` notes of the antiphon are concatenated,
    possibly filling the beginning with Nones, so that the antiphon always 
    starts at the 15th note. If the antiphon or differentia has fewer than 3 
    notes, they are ignored.
    """
    entries = []
    for idx, data in antiphons.iterrows():
        input_str = f'{data.volpiano}/{data.full_text_manuscript}'
        try:
            ch = converter.parse(input_str, format='cantus', 
                                 forceSource=force_source)
        except Exception as e:
            logging.error(f'{idx} could not be parsed: {e}')
            continue

        # Differentia: the final section as a list of midi pitches
        differentia = [n.pitch.midi for n in ch[-1].flat.notes[:max_length]]
        if len(differentia) < min_length: 
            logging.warning(
                f'Skipping {idx}; differentiae has length {len(differentia)}, '
                f'which is shorter than min_length={min_length}'
            )
            continue
        if len(differentia) < max_length:
            empty_prefix = [None] * (max_length - len(differentia))
            differentia = empty_prefix + differentia
        
        # Antiphon opening as a list of midi pitches
        opening = [n.pitch.midi for n in ch[0].flat.notes[:max_length]]
        if len(opening) < min_length: 
            logging.warning(
                f'Skipping {idx}; antiphon opening has length {len(opening)}, '
                f'which is shorter than min_length={min_length}'
            )
            continue
        if len(opening) < max_length:
            empty_prefix = [None] * (max_length - len(opening))
            opening = empty_prefix + opening
        
        entry = [idx, data['mode'], data['siglum']]
        entry.extend(differentia)
        entry.extend(opening)
        entries.append(entry)
    
    columns = ['id', 'mode', 'siglum']
    columns.extend(range(-max_length, 0))
    columns.extend(range(0, max_length))
    df = pd.DataFrame(entries, columns=columns).set_index('id').sort_index()
    return df

def main():
    output_dir = os.path.join(_DATA_DIR, 'differentiae')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_fn = os.path.join(output_dir, 'generation.log')
    logging.basicConfig(filename=log_fn, **_LOGGING_OPTIONS)
    logging.info('Start generating the differentia-antiphon connections.')
    
    chants_fn = os.path.join(_DATASETS_DIR, 'cantuscorpus', 'csv', 'chant.csv')
    chants = pd.read_csv(chants_fn, index_col=0)
    antiphons = filter_antiphons(chants)
    
    connections = extract_connections(antiphons)
    connections_fn = os.path.join(output_dir, 'connections.csv')
    connections.to_csv(connections_fn)
    logging.info(f'Stored connections to {relpath(connections_fn)}')
    logging.info(f'md5 checksum: {md5checksum(connections_fn)}')

if __name__ == '__main__':
    main()
