#!/usr/bin/env bash


cmd="time python ../../src/drivers/orik.py -c 0 -n a,b,c --EOT 4 -f ./simplog.ded --evaluator c4 --settings ./settings.ini"

rm ./IR.db

$cmd

rm ./IR.db
