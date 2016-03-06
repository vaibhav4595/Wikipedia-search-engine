#!/bin/bash

python code/indexer.py $1 $2
python code/champion_lists.py
python code/searcher.py
