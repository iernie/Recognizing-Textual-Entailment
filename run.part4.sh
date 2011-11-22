#!/bin/bash
python part4.py rte2_dev_data/RTE2_dev.preprocessed.xml > learningdata.tab
python part4.py rte_blind_data/preprocessed-blind-test-data.xml > testdata.tab
python classification.py cross
python classification.py learningdata.tab > dev_afiouni_lilleboe.txt
python classification.py testdata.tab > test_afiouni_lilleboe.txt
