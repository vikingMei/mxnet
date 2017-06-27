#!/usr/bin/env bash
#
# Usage: 
# Author: Summer Qing(qingyun.wu@aispeech.com)

source .bashrc
python  ./src/cudnn_lstm_nce.py --test \
    --model-prefix=./output/model/lstm --gpus 0 \
    --batch-size 1 \
    --load-epoch "$@"
