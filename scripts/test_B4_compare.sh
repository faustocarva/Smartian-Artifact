#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B4-smartian-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B4-smartian-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B4-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B4-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B4-compare

# With both data-flow analyses enabled.
# for i in $(seq $1); do
#      python $SCRIPTDIR/run_experiment.py B4 smartian 3600
# done
# mkdir -p $OUTDIR/result-B4-compare/dfa
# mv $OUTDIR/B4-smartian-* $OUTDIR/result-B4-compare/dfa


# With both data-flow analyses enabled.
# for i in $(seq $1); do
#      python $SCRIPTDIR/run_experiment.py B4 smartian 3600 "--withbuggain"
# done
# mkdir -p $OUTDIR/result-B4-compare/dfa_buggain
# mv $OUTDIR/B4-smartian-* $OUTDIR/result-B4-compare/dfa_buggain


for i in $(seq $1); do
   python $SCRIPTDIR/run_experiment.py B4 smartian 3600 "--uselllmseeds --withbuggain --nosdfa --noddfa"
done
mkdir -p $OUTDIR/result-B4-compare/llmseeds_buggain
mv $OUTDIR/B4-smartian-* $OUTDIR/result-B4-compare/llmseeds_buggain
