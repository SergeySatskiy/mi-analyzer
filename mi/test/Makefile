help:
	@echo "The following targets are supported:"
	@echo "make love - building test examples"
	@echo "make clean - removing executables etc."

love:
	g++ -Wall -g -O0 -o test-ok-elf test-ok-elf.cpp -lpthread
	g++ -shared -fPIC -Wall -g -O0 test-lib-fun-ok.cpp -o libtest-lib-fun-ok.so -lpthread
	g++ -Wall -g -O0 -c test-ok-lib.cpp
	g++ -g -o test-ok-lib test-ok-lib.o -L./ -ltest-lib-fun-ok
	g++ -Wall -g -O0 -o test-bad-left-locked-elf test-bad-left-locked-elf.cpp -lpthread
	g++ -Wall -g -O0 -o test-bad-unlocking-not-locked-elf test-bad-unlocking-not-locked-elf.cpp -lpthread
	g++ -Wall -g -O0 -o test-bad-unlock-order-elf test-bad-unlock-order-elf.cpp -lpthread
	g++ -Wall -g -O0 -o test-bad-lock-order-elf test-bad-lock-order-elf.cpp -lpthread
	g++ -shared -fPIC -Wall -g -O0 test-lib-fun-bad.cpp -o libtest-lib-fun-bad.so -lpthread
	g++ -Wall -g -O0 -c test-bad-lib.cpp
	g++ -g -o test-bad-lib test-bad-lib.o -L./ -ltest-lib-fun-bad
	g++ -g -o test-failed-op test-failed-op.cpp -lpthread
	g++ -g -o test-ok-recursive-elf test-ok-recursive-elf.cpp -lpthread
	g++ -g -o test-ok-condition-vars-elf test-ok-condition-vars-elf.cpp -lpthread
	g++ -g -o test-bad-lock-one-unlock-other-elf test-bad-lock-one-unlock-other-elf.cpp -lpthread

clean:
	rm -rf *.so *-elf test-ok-lib *.o test-bad-lib test-failed-op
