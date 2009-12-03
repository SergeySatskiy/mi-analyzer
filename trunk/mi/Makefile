help:
	@echo "The following targets are supported:"
	@echo "make love - building test examples"
	@echo "make clean - removing executables etc."
	@echo "make test - running tests"

love:
	g++ -shared -g -O2 -fPIC -Wall -o libmi.so -ldl -rdynamic mi.cpp
	g++ -shared -g -O0 -fPIC -Wall -o libtest-ok.so  -lpthread  test/test-lib-fun-ok.cpp
	g++ -shared -g -O0 -fPIC -Wall -o libtest-bad.so -lpthread  test/test-lib-fun-bad.cpp
	g++ -Wall -g -O0 -otest-lib-ok  test/test-lib-ok.cpp  -L./ -ltest-ok
	g++ -Wall -g -O0 -otest-lib-bad test/test-lib-bad.cpp -L./ -ltest-bad
	g++ -Wall -g -O0 -otest-bad-1 test/test-bad-1.cpp -lpthread
	g++ -Wall -g -O0 -otest-bad-2 test/test-bad-2.cpp -lpthread
	g++ -Wall -g -O0 -otest-bad-3 test/test-bad-3.cpp -lpthread

clean:
	rm -rf *.so test-lib-* mi.log test-bad-* *.pyc

test:
	@echo "Not implemented yet"
