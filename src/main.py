import sys

import batch

usage = f"Usage: { sys.argv[0] } [ c | x ] input output"

if len(sys.argv) != 4:

	print(usage)
	sys.exit()

stdin = sys.stdin.buffer

match sys.argv[1]:

	case 'c': batch.create(sys.argv[3], sys.argv[2])
	case 'x': batch.extract(sys.argv[3], sys.argv[2])

	case _:

		print(usage)

