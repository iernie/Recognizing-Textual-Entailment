#!/bin/bash

python $1 rte2_dev_data/RTE2_dev.preprocessed.xml $2 > tmprun
python eval_rte.py rte2_dev_data/RTE2_dev.xml tmprun
rm tmprun
