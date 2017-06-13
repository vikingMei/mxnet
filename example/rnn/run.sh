#!/usr/bin/env bash
#
# Usage: 
# Author: weixing.mei(auimoviki@gmail.com)

function usage() {
    echo "USAGE: $0 [-d] [-g] [train|test]"
    echo ""
    echo "PARAMETER: "
    echo "  -d: debug mod, start with python pdb"
    echo "  -g: enable gpu or not"
    echo "  -e epoch"
    echo "  train: run in train mode, default"
    echo "  test:  run in test mode"

    exit 0
}

args=`getopt -o 'e:dg' -- "$@"`
if [[ $? != 0 ]]; then
    usage
fi

eval set -- "${args}"

DEBUG=""
GPU=""
EPOCH="--load-epoch 1"
while true;
do
    case $1 in 
        -e|--epoch) EPOCH="--load-epoch $2"; shift 2;;
	-d|--debug) DEBUG="-m pdb"; shift 1;;
        -g|--gpu)   GPU="--gpus 1"; shift 1;;
	--) shift; break;;
	*)  usage;;
    esac
done

mod='train'
if [[ $# -gt 0 ]]; then
    mod=$1
fi

if [[ ${mod} = 'test' ]]; then
    MOD='--test --batch-size 10'
elif [[ ${mod} = 'train' ]]; then
    MOD='--num-epochs 30 --batch-size 40'
else
    echo "invalid mod: [${mod}], only 'test' or 'train'(default) support"
    exit 0
fi

echo "GPU: ${GPU}"
echo "MOD: ${MOD}"
echo "DEBUG: ${DEBUG}"
echo "EPOCH: ${EPOCH}"

SRC=./cudnn_lstm_nce.py
python ${DEBUG} ${SRC} ${EPOCH} ${GPU} ${MOD} \
    --num-label 5 \
    --lr 0.3 \
    --train-data ./data/ptb.train.txt \
    --valid-data ./data/ptb.valid.txt \
    --test-data  ./data/ptb.test.txt \
    --model-prefix ./model/lstm \

#dot -Tpdf -o plot.pdf ./plot.gv