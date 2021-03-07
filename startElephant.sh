#!/bin/bash
# /root/startElephant.sh
d=$(date +%Y-%m-%d-%s)
echo "$d" >> ~/"$d".log
python3 /root/Elephant.py
exit 0
