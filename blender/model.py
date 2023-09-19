import bpy

import math
import struct
import sys

def load_texture(install_path, name):

	install_path += "/data/bod/"
	name = name.lower()

	if name.startswith("bridge_bent_slope_right"):

		name = name[0:17] + name[23:]

	elif name.startswith("bridge_bent_slope_left"):

		name = name[0:17] + name[22:]

	elif name == "platform_4x4": name = "platform_small"
	elif name in (

		"platform_4x8",
		"platform_4x12",
		"platform_6x6"

	): name = "platform_medium"
	elif name in (

		"platform_6x8",
		"platform_6x12",
		"platform_8x8",
		"platform_8x12",
		"platform_10x12",
		"platform_12x12"

	): name = "platform_large"

	try:

		texture = bpy.data.images.load(f"{ install_path }/common/render/texture/d_{ name }.dds", check_existing=True)
		return texture

	except: pass

	try:

		texture = bpy.data.images.load(f"{ install_path }/shared1/render/texture/d_{ name }.dds", check_existing=True)
		return texture

	except: pass

	try:

		texture = bpy.data.images.load(f"{ install_path }/shared2/render/texture/d_{ name }.dds", check_existing=True)
		return texture

	except: return None

def load_model(name):

	install_path = bpy.context.preferences.addons[__package__].preferences.install_path

	# try to use cached mesh first

	try: return bpy.data.objects.new(name, bpy.data.meshes[name])
	except: pass

	file = open(f"{ install_path }/data/bod/common/render/model/rm_{ name.lower() }.aem", "rb")

	signature = file.read(8)

	if signature != b"\x00\x00\x00\x000MEA":

		print(f"File \"{ path }\" is not a AEM file")
		sys.exit(0)

	file_size  = struct.unpack("<I", file.read(4))[0]
	dimensions = struct.unpack("<10f", file.read(40))

###############################################################################

	vertex_count  = struct.unpack("<I", file.read(4))[0]
	vertex_size   = struct.unpack("<I", file.read(4))[0]
	vertex_offset = struct.unpack("<I", file.read(4))[0]

###############################################################################

	zero = struct.unpack("<I", file.read(4))[0]

	vertex_order_size   = struct.unpack("<I", file.read(4))[0]
	vertex_order_offset = struct.unpack("<I", file.read(4))[0]

###############################################################################

	material_count  = struct.unpack("<I", file.read(4))[0]
	material_offset = struct.unpack("<I", file.read(4))[0]

	zero = struct.unpack("<I", file.read(4))[0]

	if material_count == 0: material_count = 1

###############################################################################

	verticies = []
	faces     = []
	uvs       = []
	colors    = []
	groups    = []

	for i in range(material_count):
		groups.append([])

	file.seek(vertex_offset);
	for i in range(vertex_count):

		vertex = struct.unpack(f"<5f", file.read(20))
		color  = struct.unpack(f"<4B", file.read(4))

		file.read(vertex_size - 28)

		material = struct.unpack(f"<I", file.read(4))[0]
		verticies.append((vertex[0], vertex[2], vertex[1]))

		uvs.append((vertex[3], 1 - vertex[4]))

		colors.append(color)
		groups[material].append(i)

		#out.write(f"{ vertex[0] } { vertex[1] } { vertex[2] } { vertex[3] } { vertex[4] } { color[0] } { color[1] } { color[2] } { color[3] } { material }\n")

	file.seek(vertex_order_offset);
	for i in range(vertex_order_size // 6):

		face = struct.unpack(f"<3H", file.read(6))
		faces.append((face[0], face[2], face[1]))

	#file.seek(material_offset);
	#for i in range(material_count):
#
#		face = struct.unpack(f"<3H", file.read(6))
#		out.write(f"0 0 0\n")
#
#	out.close()

###############################################################################

	mesh = bpy.data.meshes.new(name)  # add the new mesh
	mesh.from_pydata(verticies, [], faces)

	uv = mesh.uv_layers.new(name="uv")

	for i in mesh.loops:
		uv.data[i.index].uv = uvs[i.vertex_index]

	color_layer = mesh.vertex_colors.new()

	for i in mesh.loops:
		color_layer.data[i.index].color = colors[i.vertex_index];

	object = bpy.data.objects.new(name, mesh)

	for i in range(material_count):

		g = object.vertex_groups.new(name = f"Group { i + 1 }")
		g.add(groups[i], 1, "REPLACE")

	mat = bpy.data.materials.get(name)

	if mat is None:

		if name.endswith("_MIRROR"): name = name[0:-7]

		texture = load_texture(install_path, name)
		if texture == None:

			if name.endswith("_SMALL"):    name = name[0:-6]
			elif name.endswith("_MEDIUM"): name = name[0:-7]
			elif name.endswith("_LARGE"):  name = name[0:-6]

			texture = load_texture(install_path, name)

		if texture != None:

			mat = bpy.data.materials.new(name=name)
			mat.use_nodes = True

			output = mat.node_tree.nodes.get('Principled BSDF')

			color = mat.node_tree.nodes.new("ShaderNodeVertexColor")

			mix = mat.node_tree.nodes.new("ShaderNodeMixRGB")
			mix.blend_type = "MULTIPLY"
			mix.inputs[0].default_value = 1

			input = mat.node_tree.nodes.new("ShaderNodeTexImage")
			input.image = texture

			mat.node_tree.links.new(mix.inputs[1], color.outputs[0])
			mat.node_tree.links.new(mix.inputs[2], input.outputs[0])

			mat.node_tree.links.new(output.inputs[0], mix.outputs[0])

	object.data.materials.append(mat)
	return object
