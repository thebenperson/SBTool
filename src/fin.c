/*

SBTool (Switchball Tool)
https://github.com/TheBenPerson/SBTool

Copyright (C) 2017 Ben Stockett <thebenstockett@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This file was derived from a C version of the orignal assembly program,
which was written by Jussi Puttonen, 19.4.1991 at University of Turku, Finland
Algorithms suggested by Timo Raita and Jukka Teuhola

*/

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define INDEX(p1,p2) ((p1 << 7) ^ p2)

void decompress(uint8_t *buf, FILE *out, uint32_t size) {

	uint8_t pcTable[32768];

	uint8_t ci;
	uint8_t co;            // characters (in and out)
	uint8_t p1 = 0;
	uint8_t p2 = 0;      // previous 2 characters

	memset(pcTable, ' ', 32768); // space (ASCII 32) is the most used uint8_t

	uint32_t i = 0;
	uint32_t p = 0;

	for (;;) {

		// get mask (for 8 uint8_tacters)
		ci = buf[i++];

		// for each bit in the mask
		for (size_t ctr = 0; ctr < 8; ctr++) {

			if (ci & (1 << ctr)) {

				// predicted byte
				co = pcTable[INDEX(p1, p2)];

			} else {

				// not predicted byte
				co = buf[i++];
				pcTable[INDEX(p1,p2)] = co;

			}

			if (p >= size) return;
			p++;

			fputc(co, out);

			p1 = p2;
			p2 = co;

		}

	}

}

uint32_t compress(uint8_t *in, uint8_t *out, uint32_t size) {

	uint8_t pcTable[32768];

	uint8_t p1 = 0;
	uint8_t p2 = 0;      // previous 2 characters
	uint8_t buf[8];          // keeps characters temporarily
	uint32_t ctr=0;            // number of characters in mask
	uint32_t bctr=0;           // position in buf
	uint8_t mask=0; // mask to mark successful predictions

	memset(pcTable, 32, 32768); // space (ASCII 32) is the most used char

	uint32_t i = 0;
	uint32_t o = 0;

	while (i < size)  {

		uint8_t c = in[i++];

		// try to predict the next character
		if (pcTable[INDEX(p1, p2)] == c) {

			// correct prediction, mark bit for correct prediction
			mask ^= (1 << ctr);

		} else {

			// wrong prediction, but next time ...
			pcTable[INDEX(p1, p2)] = c;

			// buf keeps character temporarily in buffer
			buf[bctr++] = c;

		}

		// test if mask is full (8 characters read)
		if (++ctr == 8){

			// write mask
			if (o == size) return NULL;
			out[o++] = mask;

			// write kept characters
			for (size_t i = 0; i < bctr; i++) {

				if (o == size) return NULL;
				out[o++] = buf[i];

			}

			// reset variables
			ctr = 0;
			bctr = 0;
			mask = 0;

		}

		// shift characters
		p1 = p2;
		p2 = c;

	}

	//EOF, but there might be some left for output
	if (ctr) {

		// write mask
		if (o == size) return NULL;
		out[o++] = mask;

		// write kept characters
		for (size_t i = 0; i < bctr; i++) {

			if (o == size) return NULL;
			out[o++] = buf[i];

		}

	}

	return o;

}
