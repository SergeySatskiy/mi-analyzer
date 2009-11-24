love:
	g++ -shared -g -O0 -fPIC -Wall -o libmi.so -ldl -rdynamic mi.cpp
	g++ -shared -g -O0 -fPIC -Wall -o libtest.so -lpthread test/test.cpp
	g++ -Wall -g -O0 -otest-lib-ok test/test-lib-ok.cpp -L./ -ltest
	g++ -Wall -g -O0 -otest-bad-1 test/test-bad-1.cpp -lpthread
	g++ -Wall -g -O0 -otest-bad-2 test/test-bad-2.cpp -lpthread
	g++ -Wall -g -O0 -otest-bad-3 test/test-bad-3.cpp -lpthread

clean:
	rm -rf *.so test-lib-ok mi.log test-bad-*
