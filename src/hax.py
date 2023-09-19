def extract(dir, input):

	path = pathlib.Path(dir)
	if not path.exists():

		print(f"Directory \"{ dir }\" does not exist", file = sys.stderr)
		return

	input = open(input, "rb")

	num_entries = struct.unpack("<I", input.read(4))[0]

	for i in range(num_entries):
		extract_entry(path, input)
