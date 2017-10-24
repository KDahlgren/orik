# orik
A provenance tree generator for recursive datalog with negation (and Dedalus).

# Code Attribution


The code in src/dedt/, src/derivation/, src/evaluators, src/drivers/, and src/utils/ is based on the code in the equivalent directories in https://github.com/KDahlgren/pyLDFI . (These are self-citations.)

# Building with cmake

```
git submodule update --init --recursive

# install c4 dependencies
dnf install cmake gcc apr-devel apr-util-devel flex bison sqlite-devel

# install other deps
dnf install sympy

cmake .
make
```
