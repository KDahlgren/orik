
# orik
A provenance tree generator for recursive datalog with negation (and Dedalus).

# Installation

After cloning the repository, run "python setup.py" from the top directory. <br>
If c4 compiles to 100%, then you're good to go!

# QA
Run the quality assurance tests to make sure the iapyx workflow works on your system.
<br>
To run tests in bulk, use the following command sequence :
```
cd qa/
python unittests_driver.py
```
To run tests individually, use commands of the format :
```
python -m unittest Test_derivation.Test_derivation.example1
```

# Examples
```
cd examples/elastic_v2/
bash run.sh
```
If the execution doesn't puke, you're good to go! <br>
P.S. : you can ignore these messages if they pop up:
```
rm: ./IR.db: No such file or directory
rm: ./tmp.txt: No such file or directory
```

# Code Attribution

The code in src/derivation/ is based on the code in the equivalent directories in https://github.com/KDahlgren/pyLDFI . (This is a self-citation.)
