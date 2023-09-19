import struct
import sys

# predictive compression algorithm
# the next byte is defined by the hash of the last two bytes

table = bytearray(0x8000)

def decompress(output, input, size):

	# assume space is the most common value

	for i in range(len(table)):
		table[i] = 0x20

	index_input  = 0
	index_output = 0

	b0 = 0
	b1 = 0

	while True:

		mask = input[index_input]
		index_input += 1

		if index_input >= len(input):
			return index_output

		for i in range(8):

			index = (b0 << 7) ^ b1
			b0 = b1

			if mask & (1 << i):

				b1 = table[index]

			else:

				if index_input >= len(input):
					return index_output

				b1 = input[index_input]
				index_input += 1

				table[index] = b1

			output.write(bytes([ b1 ]))

			index_output += 1
			if index_output >= size:
				return index_output

