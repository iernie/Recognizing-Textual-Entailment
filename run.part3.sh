#!/bin/bash

python feature_extraction.py rte2_dev_data/RTE2_dev.preprocessed.xml rte2_dev_data/RTE2_dev.xml > learningdata.tab 
python classification.py cross
python classification.py learningdata.tab > part3.txt
python eval_rte.py rte2_dev_data/RTE2_dev.xml part3.txt
