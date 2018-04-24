# based on https://github.com/KDahlgren/pyLDFI/blob/master/Makefile

all: deps

deps: get-submodules c4 iapyx

clean:
	rm -rf lib/c4/build
	rm -rf lib/iapyx

cleanc4:
	rm -rf lib/c4/build

cleaniapyx:
	rm -rf lib/iapyx

c4: lib/c4/build/src/libc4/libc4.dylib

lib/c4/build/src/libc4/libc4.dylib:
	@which cmake > /dev/null
	cd lib/c4 && mkdir -p build
	cd lib/c4/build && cmake ..
	( cd lib/c4/build && make ) 2>&1 | tee c4_out.txt;
	rm c4_out.txt

iapyx:
	cd lib/iapyx ; python setup.py ;

get-submodules:
	git submodule init
	git submodule update
