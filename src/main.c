/*
 *
 * 	SBTool (Switchball Tool)
 * 	https://github.com/TheBenPerson/SBTool
 *
 * 	Copyright (C) 2017 - 2018 Ben Stockett <thebenstockett@gmail.com>
 *
 * 	Permission is hereby granted, free of charge, to any person obtaining a copy
 * 	of this software and associated documentation files (the "Software"), to deal
 * 	in the Software without restriction, including without limitation the rights
 * 	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * 	copies of the Software, and to permit persons to whom the Software is
 * 	furnished to do so, subject to the following conditions:
 *
 * 	The above copyright notice and this permission notice shall be included in all
 * 	copies or substantial portions of the Software.
 *
 * 	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * 	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * 	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * 	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * 	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * 	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * 	SOFTWARE.
 *
 */

#include <errno.h>
#include <fcntl.h>
#include <ftw.h>
#include <getopt.h>
#include <libgen.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

// windows implementation does not follow posix :(

#ifdef _WIN32
#define mkdir(path, mode) mkdir(path)
#endif

typedef struct __attribute__((packed)) {

	uint32_t offset;
	uint32_t size;
	uint32_t pLen;

} Entry;

const char* usage =
"Usage: sbtool [Options]\n\n"
"Extract and modify Switchball game data\n\n"

"Options:\n\t"
	"-h, --help\t\t\t\t"					"display this message and exit\n\t"
	"-l, --list <file>\t\t\t"				"list files in archive\n\t"
	"-e, --extract <archive>\t\t\t"			"extract files from archive\n\t"
	"-c, --create <name> <directory>\t\t"	"create archive";

FILE *file;

extern void decompress(uint8_t *buf, FILE *out, uint32_t size);
extern uint32_t compress(uint8_t *in, uint8_t *out, uint32_t size);

static int list(int argc, char* argv[]);
static int extract(int argc, char* argv[]);
static int create(int argc, char* argv[]);

static bool checkSig();

int main(int argc, char* argv[]) {

	struct option options[] = {

		{"help", no_argument, NULL, 'h'},
		{"list", no_argument, NULL, 'l'},
		{"extract", required_argument, NULL, 'e'},
		{"create", required_argument, NULL, 'c'},
		{0, 0, 0, 0}

	};

	for (;;) {

		int index;
		char c = getopt_long(argc, argv, "hlecr", options, &index);
		if (c == -1) break;

		switch (c) {

			case 'l': return list(argc, argv);
			case 'e': return extract(argc, argv);
			case 'c': return create(argc, argv);

		}

	}

	puts(usage);
	return 0;

}

int list(int argc, char* argv[]) {

	if (argc != 3) {

		fputs("Error: invalid arguments\n", stderr);
		puts(usage);
		return 1;

	}

	file = fopen(argv[2], "r");
	if (!file) {

		perror("Error opening file");
		return 1;

	}

	if (!checkSig()) return 1;

	fseek(file, 32, SEEK_SET);

	uint32_t entries;
	fread(&entries, 4, 1, file);

	for (size_t i = 0; i < entries; i++) {

		Entry entry;

		fread(&entry, sizeof(entry), 1, file);

		char *path = malloc(entry.pLen + 1);
		fread(path, entry.pLen, 1, file);
		path[entry.pLen] = '\0';

		puts(path);
		free(path);

	}

	fclose(file);

	return 0;

}

int extract(int argc, char* argv[]) {

	if ((argc < 3) || (argc > 4)) {

		fputs("Error: invalid arguments\n", stderr);
		puts(usage);
		return 1;

	}

	file = fopen(argv[2], "r");
	if (!file) {

		perror("Error opening file");
		return 1;

	}

	if (!checkSig()) return 1;

	fseek(file, 32, SEEK_SET);

	uint32_t entries;
	fread(&entries, 4, 1, file);

	for (size_t i = 0; i < entries; i++) {

		Entry entry;
		fread(&entry, sizeof(entry), 1, file);

		char *path = malloc(entry.pLen + 1);
		fread(path, entry.pLen, 1, file);
		path[entry.pLen] = '\0';

		for (;;) {

			char *r = strchr(path, '\\');
			if (!r) break;

			*r = '/';

		}

		puts(path);
		long pos = ftell(file);

		fseek(file, entry.offset, SEEK_SET);
		char sig[4];
		fread(sig, 3, 1, file);
		sig[3] = '\0';

		uint32_t size;
		uint8_t *buf;
		bool compressed = !strcmp(sig, "VNZ");

		if (compressed) {

			fseek(file, entry.offset + 7, SEEK_SET);
			fread(&size, 4, 1, file);

			buf = malloc(size);

		} else {

			buf = malloc(entry.size);
			fseek(file, -3, SEEK_CUR);

		}

		fread(buf, entry.size, 1, file);

		uint8_t c;
		uint8_t d = 0;

		for (size_t i = 0; i < entry.size; i++) {

			c = buf[i];
			buf[i] = (c ^ 0x2) - d;
			d = c;

		}

		mode_t mode =  S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH;

		char *s = dirname(path);
		char *p = s;

		for (;;) {

			char *c = strchr(s, '/');

			if (c) *c = '\0';
			mkdir(p, mode);
			if (c) *c = '/';
			else {

				*strchr(s, '\0') = '/';
				break;

			}

			s = c + 1;

		}

		if (compressed) {

			FILE *out = fopen(path, "w");
			if (!out) perror("Error opening file");
			else {

				decompress(buf, out, size);
				fclose(out);

			}

		} else {

			int fd = creat(path, mode);
			if (fd == -1) perror("Error opening file");
			else {

				write(fd, buf, entry.size);
				close(fd);

			}

		}

		free(buf);

		fseek(file, pos, SEEK_SET);
		free(path);

	}

	fclose(file);

	return 0;

}

FILE *data;
uint32_t entries = 0;

int createProc(const char *path, const struct stat* stat, int type, struct FTW* dummy) {

	if (type != FTW_F) return 0;

	int fd = open(path, O_RDONLY);
	if (fd == -1) {

		perror("Error opening file");
		puts(path);
		return 1;

	}

	char *name = strdup(path);

	for (;;) {

		char *c = strchr(name, '/');
		if (!c) break;

		*c = '\\';

	}

	puts(name);

	uint8_t *in = malloc(stat->st_size);
	read(fd, in, stat->st_size);
	close(fd);

	uint8_t *buf = malloc(stat->st_size);

	uint32_t size = compress(in, buf, stat->st_size);
	if (size) free(in);
	else free(buf);

	uint8_t c;
	uint8_t d = 0;

	if (size) {

		for (size_t i = 0; i < stat->st_size; i++) {

			c = buf[i];
			buf[i] = (c + d) ^ 2;
			d = buf[i];

		}

	} else {

		for (size_t i = 0; i < stat->st_size; i++) {

			c = in[i];
			in[i] = (c + d) ^ 2;
			d = in[i];

		}

	}

	if (size) {

		fwrite("VNZ", 3, 1, data);
		fwrite(&size, 4, 1, data);
		fwrite(&stat->st_size, 4, 1, data);

		fwrite(buf, size, 1, data);
		free(buf);

	} else {

		size = stat->st_size;
		fwrite(in, size, 1, data);
		free(in);

	}

	fseek(file, 4, SEEK_CUR); //offset
	fwrite(&size, 4, 1, file);

	size = strlen(name);
	fwrite(&size, 4, 1, file);
	fwrite(name, size, 1, file);
	free(name);

	entries++;
	return 0;

}

int create(int argc, char* argv[]) {

	if (argc != 4) return 1;

	file = fopen(argv[2], "w+");
	if (!file) {

		perror("Error opening file");
		return 0;

	}

	data = fopen("/tmp/data.tmp", "w+");
	if (!data) {

		perror("Error opening file");

		fclose(file);
		return 0;

	}

	fputs("THIS IS A BATCH FILE", file);
	for (size_t i = 0; i < 12; i++)
		fputc(0, file);

	fseek(file, 4, SEEK_CUR);

	ftw(argv[3], &createProc, 15);

	size_t offset = ftell(file);

	fflush(data);
	fseek(data, 0, SEEK_END);
	size_t size = ftell(data);
	fseek(data, 0, SEEK_SET);

	for (size_t i = 0; i < size; i++) {

		uint8_t b = fgetc(data);
		fputc(b, file);

	}

	fclose(data);
	unlink("/tmp/data.tmp");

	fseek(file, 32, SEEK_SET);
	fwrite(&entries, 4, 1, file);

	fseek(file, 36, SEEK_SET);

	for (size_t i = 0; i < entries; i++) {

		fwrite(&offset, 4, 1, file);

		long tmp = ftell(file);
		fseek(file, offset, SEEK_SET);

			char sig[4];
			fread(&sig, 3, 1, file);
			sig[3] = '\0';

			if (!strcmp(sig, "VNZ")) offset += 11;

		fseek(file, tmp, SEEK_SET);

		uint32_t size;
		fread(&size, 4, 1, file);
		offset += size;

		uint32_t len;
		fread(&len, 4, 1, file);
		fseek(file, len, SEEK_CUR);

	}

	fclose(file);

}

bool checkSig() {

	uint8_t *buf = malloc(21);
	fread(buf, 20, 1, file);
	buf[20] = '\0';

	char sig[] = "THIS IS A BATCH FILE";

	if (strcmp(buf, sig)) {

		free(buf);
		fclose(file);

		fputs("Error: not a batch file\n", stderr);
		return false;

	}

	free(buf);
	return true;

}
