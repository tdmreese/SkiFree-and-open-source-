# Setup

## Install 
Install miniconda then run
```
conda env create -f backend/environment.yml
```

Then activate the environment with 
```
conda activate skifree-env
```

Install the package (cd into the skifree repo first)
```
pip install -e backend
```

## Activating the python environment
```
conda activate skifree-env
```

## Running
```
python backend/skifree/server.py
```

## Tests
From the repo folder 
```
pytest backend
```