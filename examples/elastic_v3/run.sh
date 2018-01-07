#!/usr/bin/env bash


cmd="time python ../../src/drivers/orik.py -c 1 -n a,b,c,C,G --EOT 15 --EFF 0 -f ./elastic_v3.ded --evaluator c4 --settings ./settings.ini"

rm ./IR.db
$cmd
rm ./IR.db
