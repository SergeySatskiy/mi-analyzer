love:
	g++ -shared -g -O0 -fPIC -Wall -o libmi.so -ldl -rdynamic mi.cpp
	g++ -shared -g -O0 -fPIC -Wall -o libtest.so -lpthread test/test.cpp
	g++ -Wall -g -O0 -odrv test/drv.cpp -L./ -ltest

clean:
	rm -rf *.so drv mi.log
