#!/bin/bash
pip3 freeze > requirements.frz
grep import *.py |cut -d: -f 2 |cut -d ' ' -f 2| cut -d . -f 1| sort -u > imports.txt

for r in `cat requirements.frz|cut -d = -f 1`; 
do 
    grep $r imports.txt ; 
done|while read -r line ; 
do 
    grep $line requirements.frz ; 
done >requirements.new

rm requirements.frz
rm imports.txt
cat requirements.txt requirements.new|sort > requirements
rm requirements.new
mv requirements.txt requirements.old
mv requirements requirements.txt
