#!/bin/bash

regNumber=$1

numbers=$(python3 motquery.py -l $1 | grep number)
manufacturerNumber=$(echo $numbers | awk '{print $3}')
modelNumber=$(echo $numbers | awk '{print $6}')

tmpFile="/tmp/results_$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1).tmp"
echo "Querying..."
python3 motquery.py -M $manufacturerNumber -m $modelNumber > $tmpFile
less $tmpFile
rm $tmpFile
echo "Done."

