import pathlib
import struct
import sys

import fin

batch_magic = "THIS IS A BATCH FILE"

def extract(dir, input):

	path = pathlib.Path(dir)
	if not path.exists():

		print(f"Directory \"{ dir }\" does not exist", file = sys.stderr)
		return

	input = open(input, "rb")

	magic = input.read(len(batch_magic)).decode("ascii")
	if magic != batch_magic:

		print("Input is not a BATCH file", file = sys.stderr)
		return

	input.seek(12, 1)

	num_entries = struct.unpack("<I", input.read(4))[0]

	for i in range(num_entries):
		extract_entry(path, input)

def extract_entry(dir, input):

	offset, size, path_size = struct.unpack("<3I", input.read(12))
	path = input.read(path_size).decode("utf-8")

	position = input.tell()
	input.seek(offset)

	path = dir.joinpath(path)
	path.parent.mkdir(exist_ok = True, parents = True)

	output = path.open(mode = "wb")

	vnz = input.read(3)
	if vnz == b"VNZ":

		compressed_size, uncompressed_size = struct.unpack("<2I", input.read(8))
		if compressed_size != size:

			print("Size mismatch", file = sys.stderr)
			return

		print(path, uncompressed_size)

		data = bytearray(input.read(size))
		decrypt(data)

		actual = fin.decompress(output, data, uncompressed_size)

	else:

		print(path, size)
		input.seek(-3, 1)

		data = bytearray(input.read(size))
		decrypt(data)

		output.write(data)

	input.seek(position)

def decrypt(data):

	last = 0

	for i in range(len(data)):

		byte = data[i]
		data[i] = (((byte ^ 0x02) & 0xFF) - last) & 0xFF
		last = byte
