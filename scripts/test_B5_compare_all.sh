#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)
ROOT=$(realpath $SCRIPTDIR/..)
BENCHDIR=$(realpath $SCRIPTDIR/../benchmarks)
B5_DIR="$BENCHDIR/B5"
TEST_DIR="$BENCHDIR/B5_test_gpts"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

# Get list of directories in B5_test
TEST_DIRS=$(find $TEST_DIR -mindepth 1 -maxdepth 1 -type d)

# Check if results directory exists
if ls $OUTDIR/result-B5-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B5-compare exists, please remove it."
    exit 1
fi

# Create results directory
mkdir -p $OUTDIR/result-B5-compare

# Process each directory in B5_test
for test_dir in $TEST_DIRS; do
    # Get directory name
    dir_name=$(basename $test_dir)

    RELATIVE_PATH=$(realpath --relative-to="$BENCHDIR" "$test_dir")
    rm $B5_DIR
    ln -sf $RELATIVE_PATH $B5_DIR
    touch $BENCHDIR/x
    rm $BENCHDIR/x
    touch $BENCHDIR/x


    pushd $ROOT
    docker build .
    popd
    
    # Create results directory for this test
    mkdir -p $OUTDIR/result-B5-compare/$dir_name
    
    # Run experiment for the specified number of iterations
    for i in $(seq $1); do
        python $SCRIPTDIR/run_experiment.py B5 smartian 3600 "--uselllmseeds --nosdfa --noddfa --withbuggain"
    done
    # Check if output directories exist
    if ls $OUTDIR/B5-smartian-* 1> /dev/null 2>&1; then
       # Move results to the appropriate directory
       mv $OUTDIR/B5-smartian-* $OUTDIR/result-B5-compare/$dir_name/
    fi    
done
