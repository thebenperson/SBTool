CC := gcc
CF := -O3
LF := -s

all: bin/sbtool

bin/sbtool: src/main.c src/fin.c
	$(CC) $(CF) $^ $(LF) -o $@

.PHONY: clean
clean:
	-rm bin/sbtool 2> /dev/null
