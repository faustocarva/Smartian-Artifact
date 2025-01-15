#!/bin/bash

# Define the base directory where you want to start searching
BASE_DIR="/var/git/Smartian-Artifact/benchmarks/B2/seed"

# Define the new prefix for the directories
NEW_PREFIX="seeds"

# Find directories matching the pattern and loop through them
find "$BASE_DIR" -type d -name "seeds_with_args_and_ctor" | while read dir; do
    mv $dir "$(dirname "$dir")/seeds"
done