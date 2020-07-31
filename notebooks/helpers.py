# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Author: Bas Cornelissen
# Copyright © 2020 Bas Cornelissen
# -------------------------------------------------------------------
import matplotlib.pyplot as plt

_ALL_DATASETS = [
    'liber-antiphons', 'liber-hymns', 'liber-alleluias', 'liber-introits', 
    'liber-communions', 'liber-responsories', 'liber-offertories', 
    'liber-graduals', 'liber-kyries', 'liber-tracts'
]

def cm2inch(*args):
    return list(map(lambda x: x/2.54, args))

def title(text):
    plt.title(text, ha='left', x=0)

def show_num_contours(num_contours, ax, y=1.06):
    plt.text(1, y, f'N={num_contours}', transform=ax.transAxes, 
         va='bottom', ha='right', size=6, fontstyle='italic', color='0.6')

def load_datasets(dataset_ids=_ALL_DATASETS, include_random=True, 
    dir='../data/phrase-contours'):
    import pandas as pd
    import sys
    sys.path.append('../')
    from src.contours import normalized_contours

    dfs = {}
    contours = {}
    for dataset_id in dataset_ids:
        dfs[dataset_id] = pd.read_csv(f'{dir}/{dataset_id}-phrase-contours-subset.csv', index_col=0)
        dfs[f'{dataset_id}-random'] = pd.read_csv(f'{dir}/{dataset_id}-random-contours-subset.csv', index_col=0)
        contours[dataset_id] = normalized_contours(dfs[dataset_id])
        contours[f'{dataset_id}-random'] = normalized_contours(dfs[f'{dataset_id}-random'])
    return dfs, contours
