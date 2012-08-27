help:
	@echo "The following targets are supported:"
	@echo "make all - building libmi.so"
	@echo "make clean - removing executables etc."
	@echo "make test - building test examples"

all:
	g++ -shared -O2 -fPIC -Wall -o libmi.so -ldl -rdynamic mi.cpp

clean:
	rm -rf *.so test-lib-* mi.log test-bad-* *.pyc
	make -C test clean

.PHONY : test
test:
	make -C test love
