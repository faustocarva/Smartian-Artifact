#!/bin/bash

SCRIPTDIR=$(dirname $0)
OUTDIR=$(realpath $SCRIPTDIR/../output)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <iterN>"
    exit
fi

if ls $OUTDIR/B2-* 1> /dev/null 2>&1; then
    echo "$OUTDIR/B2-* exists, please remove it."
    exit 1
fi

if ls $OUTDIR/result-B2-compare 1> /dev/null 2>&1; then
    echo "$OUTDIR/result-B2-compare exists, please remove it."
    exit 1
fi

mkdir -p $OUTDIR/result-B2-compare

for i in $(seq $1); do
    python $SCRIPTDIR/run_experiment.py B2 smartian 3600 "--uselllmseeds"
done
mkdir -p $OUTDIR/result-B2-compare/smartian_llm
mv $OUTDIR/B2-smartian-* $OUTDIR/result-B2-compare/smartian_llm/
