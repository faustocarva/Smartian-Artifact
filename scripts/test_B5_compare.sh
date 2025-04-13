#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B5-smartian-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B5-smartian-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B5-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B5-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B5-compare

for i in $(seq $1); do
   python $SCRIPTDIR/run_experiment.py B5 smartian 3600 "--uselllmseeds --nosdfa --noddfa --withbuggain"
done
mkdir -p $OUTDIR/result-B5-compare/llmseeds_no_dynamic_buggain
mv $OUTDIR/B5-smartian-* $OUTDIR/result-B5-compare/llmseeds_no_dynamic_buggain

# # With full DFA 
# for i in $(seq $1); do
#     python $SCRIPTDIR/run_experiment.py B4 smartian 900 "--uselllmseeds --withbuggain"
# done
# mkdir -p $OUTDIR/result-B5-compare/llmseeds_dfa_withbuggain
# mv $OUTDIR/B4-smartian-* $OUTDIR/result-B5-compare/llmseeds_dfa_withbuggain


# random seeds
# for i in $(seq $1); do
#     python $SCRIPTDIR/run_experiment.py B4 smartian 1800 "--nosdfa --noddfa"
# done
# mkdir -p $OUTDIR/result-B5-compare/nodfa
# mv $OUTDIR/B4-smartian-* $OUTDIR/result-B5-compare/nodfa
