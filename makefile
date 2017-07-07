all: bin/sbtool

bin/sbtool: bin/main.o bin/fin.o
	gcc $^ -o $@

bin/main.o: src/main.c
	gcc -c $^ -o $@

bin/fin.o: src/fin.c
	gcc -c $^ -o $@
