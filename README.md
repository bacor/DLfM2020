Studying Large Plainchant Corpora Using chant21
===============================================

This repository contains all code for the two case studies in the paper 
['Studying Large Plainchant Corpora Using chant21'](https://doi.org/10.1145/3424911.3425514)
([pdf](paper/dlfm2020.pdf))
presented at the
[Digital Libraries for Musicology 2020](https://dlfm.web.ox.ac.uk/) conference.
In that paper we also present the 
[CantusCorpus](https://github.com/bacor/cantuscorpus), 
[GregobaseCorpus](https://github.com/bacor/gregobasecorpus) 
and the Python package [Chant21](https://github.com/bacor/chant21).

----

<img src="figures/teaser/teaser.jpg?raw=true" width="500" title="Two case studies: melodic contour and differentia-antiphon connections">

**Main findings.**
The first case study we discuss in the paper shows that melodic contours of 
phrases in the GregoBaseCorpus are on average arch shaped, confirming the 
so-called *melodic arch hypothesis*. The second case
study addresses a particular problem in chant scholarship: the connection between
differentiae at the end of psalms, and the opening of the repeated antiphon.
Our analyses of the CantusCorpus suggest that this relation differs across 
modes, and is fairly predictable, but not as predictable as the differentiae 
themselves.

---

Repository structure 
--------------------

- `data/phrase-contours`: contains all phrase contours used in the first case
study, including all random baselines, and the 3000 contour subsets. 
The contours are semi-normalized: we normalized the duration to 1, and then 
sampled pitches at 50 time points, but have not yet normalized the pitch to 
mean 0. So the pitch values are simply midi pitches.
All contours can be found in CSV files with the following columns:

  - `contour_id` a unique identifier for the contour
  - `song_id` the filename/identifier of the chant from which the contour was extracted
  - `phrase_num` which phrase in the chant
  - `phrase_length` the length of the phrase in number of notes
  - `phrase_duration` the duration of the phrase in quarternotes
  - `0...49` (midi) pitch values sampled at 50 equally spaces positions in the phrase.
- `notebooks/`: contains all the notebooks used to generate the figures
- `figures/`: the figures in the paper. The graphs were always generated using
Jupyter notebooks, but finalized in Affinity Designer.
- `src/`: contains the code for generating the data (contours and connections).
- `tests/`: some unittests of the code in the `src` directory.
- `datasets/`: This directory should contain the corpora used. We have not 
included the corpora as they can be easily downloaded: here are the links to [CantusCorpus v0.1](https://github.com/bacor/cantuscorpus/releases/tag/v0.1)
and [GregoBaseCorpus v0.4](https://github.com/bacor/gregobasecorpus/releases/tag/v0.4).
After downloading the datasets, place them in a directory named `datasets`.
It should now have the following structure:

  ```
  - datasets/
    - gregobasecorpus
      - gabc
        - 00001.gabc
        - 00002.gabc
        - ..
    - cantuscorpus
      - csv
        - chant.csv
        - feast.csv
        - ..
  ```

Python setup
------------

You can find the Python version used in `.python-version` and all dependencies 
are listed in `requirements.txt`. If you use `pyenv` and `venv` to manage 
python versions and virtual environments, do the following:

```bash
# Install the right python version
pyenv install | cat .python-version

# Create a virtual environment
python -m venv env

# Activate the environment
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

You should then be able to run the Jupyter notebooks: 

```bash
cd notebooks
jupyter lab
```

We have tested all this: installing and running all code from scratch worked as expected.

Generating the data
-------------------

We have already included the data used in the case studies, but for completeness 
sake, we also document here how to reproduce those datasets from scratch.
Please make sure that you have downloaded the corpora and placed them in the
directory `datasets/`, as described above. 

The script `src/generate_contours.py` is used to generate the contours used in 
case study 1; the script `src/generate-differentiae.py` generates the 
differentia-antiphon connections for case study 2. Run them from the root 
directory as follows

```bash
$ source env/bin/activate
$ python -m src.generate_contours.py
$ python -m src.generate_differentiae.py
```

This regenerates the `data/` directory and its contents.

Citation
--------

Bas Cornelissen, Willem Zuidema, and John Ashley Burgoyne. 2020. 
Studying Large Plainchant Corpora Using chant21. 
In *7th International Conference on Digital Libraries for Musicology.* 
ACM, New York, NY, USA, 5 pages.
[https://doi.org/10.1145/3424911.3425514](https://doi.org/10.1145/3424911.3425514)