
import bpy
import mathutils

import sys
import inspect
import xml.etree.ElementTree as ET

from . model import load_model

from bpy_extras.io_utils import ImportHelper, ExportHelper

global_id_map = {}
global_id_map_reverse = {}

def menu_func_import(self, context):
	self.layout.operator(ImportLevel.bl_idname, text="Switchball Level (.vnl)")

def menu_func_export(self, context):
	self.layout.operator(ExportLevel.bl_idname, text="Switchball Level (.vnl)")

def set_property(object, name, value):

	cls = TYPE.lookup(object["type"])

	while True:

		if name in cls.__annotations__: break

		try: cls = cls.SUPER
		except:

			print(f"WARNING: Unknown property \"{ name }\"")
			return

	match cls.__annotations__[name].function:

		case bpy.props.PointerProperty:

			if type(value) == int:

				global_id_map[value] = ( object, name )
				return

		case bpy.props.EnumProperty:

			value = str(value).lower()

	attr = getattr(object, cls.__name__)
	setattr(attr, name, value)

class _SBTOOL_PANEL(bpy.types.Panel):

	bl_idname = "OBJECT_PT_sbtool"
	bl_label  = "Switchball Properties"
	bl_space_type  = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context     = "object"

	def draw(self, context):

		self.layout.row().label(text = "Switchball Properties")

class PANEL:

	bl_space_type  = "PROPERTIES"
	bl_parent_id   = "OBJECT_PT_sbtool"
	bl_region_type = "WINDOW"
	bl_context     = "object"

	@classmethod
	def poll(cls, context):

		try: type = context.active_object["type"]
		except: return False

		derived = TYPE.lookup(type)
		return derived.issubclass(cls.my_data)

	def draw(self, context):

		for i in self.my_data.__annotations__:

			value = getattr(context.active_object, self.my_data.__name__)
			self.layout.row().prop(value, i)

class PARAM:

	def __init__(self, name: str, value, description = None, min = None, max = None):

		self.name  = name
		self.value = value

		self.description = description

		self.min = min
		self.max = max

	def new(param):

		name      = param.get("name")
		value     = param.get("value")
		data_type = param.get("data_type")

		match data_type:

			case "bool":  value = (value == "true")
			case "int":   value = int(value)
			case "float": value = float(value)

			case "string": pass
			case _:

				raise ValueError(f"Unknown parameter type \"{ self.data_type }\"")

		return PARAM(name, value)

	def export(self):

		pass

class ImportLevel(bpy.types.Operator, ImportHelper):

	bl_idname = "sbtool.import"
	bl_label  = "Import Level"

	filename_ext = ".vnl"

	def execute(self, context):

		try: root = ET.parse(self.filepath).getroot()
		except ET.ParseError:

			self.report({ "ERROR" }, "Could not parse level")
			return { "CANCELLED" }

		cls = TYPE.lookup("LEVEL")
		level = cls.new(type = "LEVEL")
		cls.from_xml(level, root)

		for id, entry in global_id_map.items():

			try: target = global_id_map_reverse[id]
			except:

				print("Could not find object ID", id)
				continue

			set_property(entry[0], entry[1], target)

		return { "FINISHED" }

class ExportLevel(bpy.types.Operator, ExportHelper):

	bl_idname = "sbtool.export"
	bl_label  = "Export Level"

	filename_ext = ".vnl"

	def execute(self, context):

		global_id_map.clear()
		global_id_map_reverse.clear()
		id = 1

		for i in bpy.data.objects:

			try: type = i["type"]
			except: continue

			if type == "LEVEL": continue
			global_id_map_reverse[id] = i
			global_id_map[i] = id
			id += 1

		level = bpy.data.objects["SKYBOX"]
		cls   = TYPE.lookup(level["type"])

		root = ET.Element("level")
		cls.to_xml(root, level)

		for i in bpy.data.objects:

			if i.parent: continue

			try: type = i["type"]
			except: continue

			if type == "LEVEL": continue
			newroot = ET.SubElement(root, "object")

			cls = TYPE.lookup(type)
			cls.to_xml(newroot, i)

		tree = ET.ElementTree(root)
		ET.indent(tree, space='\t')

		with open(self.filepath, "w") as file:
			tree.write(file, encoding = "unicode")

		return { "FINISHED" }

class TYPE:

	def bases(object):

		cls = TYPE.lookup(object["type"])
		bases = []

		while True:

			if issubclass(cls, bpy.types.PropertyGroup):
				bases.append(cls)

			try: cls = cls.SUPER
			except: break

		return bases

	def lookup(type):

		try:    class_type = globals()[type]
		except: class_type = None

		if class_type is not None:
			return class_type

		if type in (

			"CAMERA_LOOKAT",
			"FLUID_CONTACT",
			"LEVEL_FINISH_POINT"

		): return EMPTY

		if type in (

			"BALANCE_LARGE",
			"BALANCE_STAND",
			"BALL_HOLDER",
			"BAR_HOLDER",
			"BAR_MEDIUM",
			"BAR_SMALL",
			"BOARD_ONE_FIT",
			"BRIDGE_2X2",
			"BRIDGE_2X4",
			"BRIDGE_BEND_2X2",
			"BRIDGE_BEND_3X3",
			"BRIDGE_BEND_4X4",
			"BRIDGE_BENT_SLOPE_LEFT_3X3",
			"BRIDGE_BENT_SLOPE_LEFT_4X4",
			"BRIDGE_BENT_SLOPE_RIGHT_3X3",
			"BRIDGE_BENT_SLOPE_RIGHT_4X4",
			"BRIDGE_END",
			"BRIDGE_HALFPIPE",
			"BRIDGE_SLOPE_18",
			"BRIDGE_SLOPE_18_END",
			"BRIDGE_SLOPE_18_START",
			"BRIDGE_SLOPE_26",
			"BRIDGE_SLOPE_26_END",
			"BRIDGE_SLOPE_26_START",
			"BRIDGE_SLOPE_45",
			"BRIDGE_SLOPE_45_END",
			"BRIDGE_SLOPE_45_START",
			"BRIDGE_STAIRS",
			"CANNON_BARREL",
			"CANNON_LID",
			"CANNON_STAND",
			"CHECKPOINT",
			"EDGE",
			"EDGE_CORNER_LARGE",
			"EDGE_CORNER_LARGE_MIRROR",
			"EDGE_CORNER_MEDIUM",
			"EDGE_CORNER_MEDIUM_MIRROR",
			"EDGE_CORNER_SMALL",
			"EDGE_CORNER_SMALL_MIRROR",
			"EDGE_ONE",
			"EDGE_TWO",
			"ENGINE_LARGE",
			"ENGINE_SMALL",
			"FAN_PROPELLER",
			"FLOORFAN_PROPELLER",
			"GYROCOPTER_PROPELLER",
			"LAMP_QUAD",
			"LAMP_SMALL",
			"MAST",
			"NAIL_LARGE",
			"NAIL_MEDIUM",
			"PIPE",
			"PIPE_BEND",
			"PIPE_BEND_SHORT",
			"PIPE_GLASS",
			"PIPE_GLASS_BEND",
			"PIPE_GLASS_BEND_SHORT",
			"PIPE_GLASS_START",
			"PIPE_START",
			"PLATFORM_4X12",
			"PLATFORM_4X4",
			"PLATFORM_4X8",
			"PLATFORM_6X12",
			"PLATFORM_6X6",
			"PLATFORM_6X8",
			"PLATFORM_8X12",
			"PLATFORM_8X8",
			"POLE",
			"POLE_KNOB",
			"POLE_POST",
			"POWERBALL",
			"PUSHPOLE",
			"PUSHPROPELLER",
			"RAIL",
			"RAIL_BEND",
			"RAIL_END",
			"RAIL_SLOPE",
			"SWINGBOARD",
			"SWINGPOLE",
			"SWITCH_BUTTON",
			"WALL",
			"WATERCANNON_FOOT",
			"WATERCANNON_LID",
			"WATERCANNON_STAND",
			"WATERCANNON_TANK",
			"WATERTANK_TAP",
			"WATERWHEEL",

			# props

			"BALOON",
			"BARREL_LARGE",
			"BARREL_MEDIUM",
			"BARREL_SMALL",
			"BOARD_CURVED",
			"BOARD_QUAD_FIT",
			"CANNONBALL_LARGE",
			"MAGNET_IN_ROPE",
			"NAIL_SMALL",
			"STONEBALL_LARGE",
			"STONEBALL_MEDIUM",
			"STONEBALL_SMALL",
			"TRENCH",
			"TRENCH_BEND",
			"TRENCH_SLOPE_DOWN",
			"TRENCH_SLOPE_UP",
			"WATERWHEEL_GEARWHEEL",
			"WIRE",

			# fluid models

			"BOARD_LARGE",
			"BOARD_MEDIUM",
			"BOARD_SMALL",
			"CANNONBALL_MEDIUM",
			"PLANK_LARGE",
			"PLANK_LOG",
			"PLANK_MEDIUM",
			"PLANK_SMALL",
			"WOODCRATE_LARGE",
			"WOODCRATE_MEDIUM",
			"WOODCRATE_SMALL",

			"TNTCRATE_SMALL",
			"TNTCRATE_LARGE",
			"MARBLEBALL",

			# fluid cloth models

			"CANNONBALL_SMALL",
			"MELTER",
			"METALCRATE_LARGE",
			"METALCRATE_MEDIUM",
			"METALCRATE_SMALL"

		): return MODEL

		if type in (

			"FLOORFAN",
			"MAGNET",
			"PUMP",
			"PUSHPOLE_STAND"

		): return SINK

		if type in (

			"FAN",
			"PUSHPROPELLER_STAND",
			"SWINGBOARD_STAND",
			"SWINGPOLE_STAND"

		): return SINK_ANGULAR

		if type in (

			"HOVER_SMALL",
			"HOVER_LARGE"

		): return HOVER

		raise ValueError(f"Unknown object type \"{ type }\"")

	@classmethod
	def issubclass(cls, base):

		if cls == base: return True

		try: return cls.SUPER.issubclass(base)
		except: return False

	@classmethod
	def new(cls, options = None, **kwargs):

		return cls.SUPER.new(options = cls, **kwargs)

	@classmethod
	def next_new(cls, options = None, **kwargs):

		return cls.SUPER.new(options = cls, **kwargs)

	@classmethod
	def from_xml(cls, object, root):

		cls.SUPER.from_xml(object, root)

	@classmethod
	def next_from_xml(cls, object, root):

		cls.SUPER.from_xml(object, root)

	@classmethod
	def to_xml(cls, root, object):

		cls.SUPER.to_xml(root, object)

	@classmethod
	def next_to_xml(cls, root, object):

		cls.SUPER.to_xml(root, object)

	#@classmethod
	#def new(cls, **kwargs):

class OBJECT(TYPE, bpy.types.PropertyGroup):

	def new(object, type, **kwargs):

		# set object type
		object["type"] = type

		# add object to scene
		bpy.context.collection.objects.link(object)
		return object

	# must be called after derived class constructor
	def from_xml(object, root):

		# parse properties tag

		properties = root.find("properties")
		if properties:

			for param in properties.findall("param"):

				param = PARAM.new(param)
				set_property(object, param.name, param.value)

		# add children of root tag

		for i in root.findall("object"):

			type = i.get("type")
			cls  = TYPE.lookup(type)

			child = cls.new(type = type)
			cls.from_xml(object = child, root = i)

			if root.tag == "object":
				child.parent = object

	def to_xml(root, object):

		bases = TYPE.bases(object)
		properties = ET.SubElement(root, "properties")

		for jj in bases:

			for name in jj.__annotations__:

				pp = getattr(object, jj.__name__)
				if not pp.is_property_set(name): continue

				value = getattr(pp, name)
				if value is None: continue

				data_type = type(value).__name__
				match data_type:

					case "bool":

						value = "true" if value else "false"

					case "Object":

						data_type = "int"
						value = str(global_id_map[value])

					case "str":

						data_type = "string"

					case _:

						value = str(value)

				param = ET.SubElement(properties, "param")

				param.set("name", name)
				param.set("value", value)
				param.set("data_type", data_type)

		if len(properties) == 0:
			root.remove(properties)

		for i in object.children:

			newrooot = ET.SubElement(root, "object")
			cls = TYPE.lookup(i["type"])
			cls.to_xml(newrooot, i)

		return object

class OBJECT_WORLD(TYPE, bpy.types.PropertyGroup):

	SUPER = OBJECT

	dynamic: bpy.props.EnumProperty(

		items = (

			("default", "Default", "Default Value"),
			("false", "False", "Disabled"),
			("true", "True", "Enabled")

		),

		name        = "dynamic",
		description = "Enable Physics",
		default     = "default"

	)

	respawn: bpy.props.BoolProperty(

		name        = "respawn",
		description = "Respawn on Delete",
		default     = False

	)

	def from_xml(object, root):

		id = int(root.get("id"))
		global_id_map_reverse[id] = object

		# (X, Y, Z, W) position vector
		pos = list(float(root.get("pos_" + xyz)) for xyz in "xzy")
		pos.append(1)

		# (X, Y, Z, W) basis vectors

		basis_x = list(float(root.get("right_" + xyz)) for xyz in "xzy")
		basis_x.append(1)

		basis_z = list(float(root.get("up_" + xyz)) for xyz in "xzy")
		basis_z.append(1)

		basis_y = list(float(root.get("forward_" + xyz)) for xyz in "xzy")
		basis_y.append(1)

		matrix = mathutils.Matrix([ basis_x, basis_y, basis_z, pos ])
		matrix.transpose()

		object.matrix_basis = matrix
		__class__.next_from_xml(object, root)

	def to_xml(root, object):

		root.set("type", object["type"])
		root.set("id", str(global_id_map[object]))

		basis = object.matrix_basis

		basis_x = basis.col[0][0:3]
		basis_x = (basis_x[0], basis_x[2], basis_x[1])

		basis_y = basis.col[2][0:3]
		basis_y = (basis_y[0], basis_y[2], basis_y[1])

		basis_z = basis.col[1][0:3]
		basis_z = (basis_z[0], basis_z[2], basis_z[1])

		pos = basis.col[3][0:3]
		pos = (pos[0], pos[2], pos[1])

		for i in range(3):
			root.set("right_" + "xyz"[i], str(basis_x[i]))

		for i in range(3):
			root.set("up_" + "xyz"[i], str(basis_y[i]))

		for i in range(3):
			root.set("forward_" + "xyz"[i], str(basis_z[i]))

		for i in range(3):
			root.set("pos_" + "xyz"[i], str(pos[i]))

		__class__.next_to_xml(root, object)

class OBJECT_WORLD_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Object Properties"
	bl_idname = "OBJECT_PT_OBJECT_WORLD"

	my_data = OBJECT_WORLD

class EMPTY(TYPE):

	SUPER = OBJECT_WORLD

	def new(type, options = None, **kwargs):

		object = bpy.data.objects.new(type, None)

		try: object.empty_display_type = options.empty_type
		except: pass

		try: object.empty_display_size = options.empty_size
		except: pass

		return __class__.next_new(object = object, type = type, **kwargs)

class LEVEL(TYPE, bpy.types.PropertyGroup):

	SUPER = OBJECT

	world_type: bpy.props.EnumProperty(

		items = (

			( "sky_world", "Sky World", "Sky World" ),
			( "ice_world", "Ice World", "Ice World" ),
			#( "desert_world", "Desert World", "Desert World" ),
			( "cave_world", "Cave World", "Cave World" ),
			( "cloud_world", "Cloud World", "Cloud World" ),
			( "lava_world", "Lava World", "Lava World" )

		),

		name        = "world_type",
		description = "World Type"

	)

	def new(**kwargs):

		object = load_model("SKYBOX")
		object.scale *= 200

		return __class__.next_new(object = object, **kwargs)

class LEVEL_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Level Properties"
	bl_idname = "OBJECT_PT_LEVEL"

	my_data = LEVEL

class MODEL(TYPE, bpy.types.PropertyGroup):

	SUPER = OBJECT_WORLD

	cloth_collision: bpy.props.BoolProperty(

		name = "cloth_collision",
		description = "Enable Cloth Collision",
		default = False

	)

	fluid_collision: bpy.props.BoolProperty(

		name = "fluid_collision",
		description = "Enable Fluid Collision",
		default = False

	)

	keep_position: bpy.props.BoolProperty(

		name = "keep_position",
		description = "Keep Position",
		default = False

	)

	def new(type, **kwargs):

		object = load_model(type)
		return __class__.next_new(object = object, type = type, **kwargs)

class MODEL_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Model Properties"
	bl_idname = "OBJECT_PT_MODEL"

	my_data = MODEL

class ACHIEVEMENT_TRIGGER(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "CUBE"

	achievement_name: bpy.props.StringProperty(

		name = "achievement_name",
		description = "Achievement Name"

	)

class ACHIEVEMENT_TRIGGER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Achievement Trigger Properties"
	bl_idname = "OBJECT_PT_ACHIEVEMENT_TRIGGER"

	my_data = ACHIEVEMENT_TRIGGER

class TUTORIAL_TRIGGER(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "CUBE"

	tutorial_name: bpy.props.StringProperty(

		name = "tutorial_name",
		description = "Tutorial Name"

	)

class TUTORIAL_TRIGGER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Tutorial Trigger Properties"
	bl_idname = "OBJECT_PT_TUTORIAL_TRIGGER"

	my_data = TUTORIAL_TRIGGER

class POINT_LIGHT(TYPE):

	SUPER = OBJECT_WORLD

	def new(type, **kwargs):

		light = bpy.data.lights.new(type, "POINT")
		light.energy = 30

		#color = tuple(self.properties[i].value for i in ("red", "green", "blue"))
		#light.color = color if color > (0, 0, 0) else (1, 1, 1)

		object = bpy.data.objects.new(type, light)
		return __class__.next_new(object = object, type = type, **kwargs)

class WAYPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "SPHERE"

	next_waypoint_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "next_waypoint_id",
		description = "Next Waypoint"

	)

class WAYPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Waypoint Properties"
	bl_idname = "OBJECT_PT_WAYPOINT"

	my_data = WAYPOINT

class GYROCOPTER(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	first_waypoint_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "first_waypoint_id",
		description = "Waypoint to follow"

	)

class GYROCOPTER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Gyrocopter Properties"
	bl_idname = "OBJECT_PT_GYROCOPTER"

	my_data = GYROCOPTER

class CLOTH_FITPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY

	empty_type = "SPHERE"
	empty_size = 0.2

	first_fitpoint: bpy.props.BoolProperty(

		name = "first_fitpoint",
		description = "Is the first fitpoint",
		default = True

	)

	next_fitpoint_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "next_fitpoint_id",
		description = "Next Fitpoint"

	)

	behaviour: bpy.props.EnumProperty(

		items = (

			( "hanging", "Hanging", "Make the cloth hang" ),
			( "stretched", "Stretched", "Stretch the cloth" ),
			( "bouncy", "Bouncy", "Make the cloth bouncy" )

		),

		name        = "behaviour",
		description = "Cloth Behavior"

	)

	mesh: bpy.props.StringProperty(

		default = "cloth.x",
		name    = "Mesh to draw cloth along"

	)

class CLOTH_FITPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Cloth Fitpoint Properties"
	bl_idname = "OBJECT_PT_CLOTH_FITPOINT"

	my_data = CLOTH_FITPOINT

class SINK(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	active_on_startup: bpy.props.BoolProperty(

		name = "active_on_startup",
		description = "Active on startup",
		default = False

	)

	mechanic: bpy.props.BoolProperty(

		name = "mechanic",
		description = "Moves",
		default = False

	)

class SINK_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Sink Properties"
	bl_idname = "OBJECT_PT_SINK"

	my_data = SINK

class SINK_ANGULAR(TYPE, bpy.types.PropertyGroup):

	SUPER = SINK

	rotation_direction: bpy.props.EnumProperty(

		items = (

			( "cw", "Clockwise", "Rotate clockwise" ),
			( "ccw", "Counter Clockwise", "Rotate counter clockwise" )

		),

		name        = "rotation_direction",
		description = "Rotation Direction"

	)

	rotation_speed: bpy.props.EnumProperty(

		items = (

			( "none", "None", "Disable rotation" ),
			( "slow", "Slow", "Rotate slowly" ),
			( "medium", "Medium", "Rotate medium speed" ),
			( "fast", "Fast", "Rotate fast" )

		),

		name        = "rotation_speed",
		description = "Rotation Speed"

	)

class SINK_ANGULAR_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Angular Sink Properties"
	bl_idname = "OBJECT_PT_SINK_ANGULAR"

	my_data = SINK_ANGULAR

class HOVER(TYPE, bpy.types.PropertyGroup):

	SUPER = SINK

	first_waypoint: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "first_waypoint",
		description = "Waypoint to follow"

	)

	behaviour: bpy.props.EnumProperty(

		items = (

			( "stationary", "Stationary", "Hover in place" ),
			#( "steerable", "Steerable", "Steerable" ),
			( "idle", "Idle", "Hover in place" ),
			( "elevator", "Elevator", "Go up and down" ),
			( "patrol", "Patrol", "Follow waypoints" )

		),

		name        = "behaviour",
		description = "Behavior"

	)

class HOVER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Hover Properties"
	bl_idname = "OBJECT_PT_HOVER"

	my_data = HOVER

class OBJECT_SPAWNPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY

	mesh_to_spawn: bpy.props.StringProperty(

		name = "mesh_to_spawn",
		description = "Mesh to spawn"

	)

	respawn_time: bpy.props.IntProperty(

		name = "respawn_time",
		description = "Respawn timer",
		default = 1,
		min = 1,
		subtype = "TIME_ABSOLUTE"

	)

class OBJECT_SPAWNPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Object Spawnpoint Properties"
	bl_idname = "OBJECT_PT_OBJECT_SPAWNPOINT"

	my_data = OBJECT_SPAWNPOINT

class PLAYER_SPAWNPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "SPHERE"

	checkpoint_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "checkpoint_id",
		description = "Checkpoint"

	)

	airball_can_spawn: bpy.props.BoolProperty(

		name = "airball_can_spawn",
		description = "Airball can spawn",
		default = False

	)

	default_ball: bpy.props.EnumProperty(

		items = (

			( "marbleball", "Marbleball", "Marbleball" ),
			( "steelball", "Metalball", "Metalball" ),
			( "airball", "Airball", "Airball" ),
			( "powerball", "Powerball", "Powerball" )

		),

		name        = "default_ball",
		description = "Default Ball"

	)

	first_spawnpoint: bpy.props.BoolProperty(

		name = "first_spawnpoint",
		description = "First spawn point",
		default = True

	)

	marbleball_can_spawn: bpy.props.BoolProperty(

		name = "marbleball_can_spawn",
		description = "Marbleball can spawn",
		default = False

	)

	order_number: bpy.props.IntProperty(

		name = "order_number",
		description = "Order Number",
		default = 1,
		min = 1

	)

	powerball_can_spawn: bpy.props.BoolProperty(

		name = "powerball_can_spawn",
		description = "Powerball can spawn",
		default = False

	)

	steelball_can_spawn: bpy.props.BoolProperty(

		name = "steelball_can_spawn",
		description = "Steelball can spawn",
		default = False

	)

class PLAYER_SPAWNPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Player Spawnpoint Properties"
	bl_idname = "OBJECT_PT_PLAYER_SPAWNPOINT"

	my_data = PLAYER_SPAWNPOINT

class CANNON_FOOT(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	behaviour: bpy.props.EnumProperty(

		items = (

			( "idle", "Idle", "Open" ),
			( "locked", "Locked", "Closed" ),
			( "auto_fire", "Auto Fire", "Auto Fire" ),
			( "locked", "Locked", "Closed" )

		),

		name        = "behaviour",
		description = "Cannon Behavior"

	)

class CANNON_FOOT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Cannon Properties"
	bl_idname = "OBJECT_PT_CANNON_FOOT"

	my_data = CANNON_FOOT

class WATERCANNON_BARREL(TYPE):

	SUPER = CANNON_FOOT

class CAMERA_POSITION(TYPE, bpy.types.PropertyGroup):

	SUPER = OBJECT_WORLD

	attached_to_zone_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "attached_to_zone_id",
		description = "Zone"

	)

	def new(type, **kwargs):

		camera = bpy.data.cameras.new(type)
		object = bpy.data.objects.new(type, camera)

		return __class__.next_new(object = object, type = type, **kwargs)

class CAMERA_POSITION_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Camera Position Properties"
	bl_idname = "OBJECT_PT_CAMERA_POSITION"

	my_data = CAMERA_POSITION

class CAMERA_WAYPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY

	lookat_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "lookat_id",
		description = "Look at"

	)

	first_waypoint: bpy.props.BoolProperty(

		name = "first_waypoint",
		description = "First Waypoint",
		default = False

	)

class CAMERA_WAYPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Camera Waypoint Properties"
	bl_idname = "OBJECT_PT_CAMERA_WAYPOINT"

	my_data = CAMERA_WAYPOINT

class CAMERA_ZONEPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY

	empty_type = "CUBE"
	empty_size = 0.1

	change_to_camera_mode: bpy.props.EnumProperty(

		items = (

			( "stationary", "Stationary", "Stationary camera mode" ),
			( "isometric", "Isometric", "Metalball camera mode" ),
			( "chase", "Chase", "Follow the ball" )

		),

		name        = "change_to_camera_mode",
		description = "Camera mode"

	)

	first_zone: bpy.props.BoolProperty(

		name = "first_zone",
		description = "First Zone",
		default = False

	)

	isometric_angle: bpy.props.EnumProperty(

		items = (

			( "n", "North", "Point north" ),
			( "ne", "Northeast", "Point northeast" ),
			( "e", "East", "Point east" ),
			( "se", "Southeast", "Point southeast" ),
			( "s", "South", "Point south" ),
			( "sw", "Southwest", "Point southwest" ),
			( "w", "West", "Point west" ),
			( "nw", "Northwest", "Point northwest" )

		),

		name        = "isometric_angle",
		description = "Isometric Angle"

	)

	zoom: bpy.props.EnumProperty(

		items = (

			( "close", "Close", "Close zoom" ),
			( "normal", "Normal", "Normal zoom" ),
			( "far", "Far", "Far zoom" )

		),

		name        = "zoom",
		description = "Camera zoom"

	)

class CAMERA_ZONEPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Camera Zonepoint Properties"
	bl_idname = "OBJECT_PT_CAMERA_ZONEPOINT"

	my_data = CAMERA_ZONEPOINT

class MORPH(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	morph_to: bpy.props.EnumProperty(

		items = (

			( "marbleball", "Marbleball", "Marbleball" ),
			( "steelball", "Steelball", "Steelball" ),
			( "airball", "Airball", "Airball" ),
			( "powerball", "Powerball", "Powerball" )

		),

		name        = "morph_to",
		description = "Morph to"

	)

class MORPH_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Morph Properties"
	bl_idname = "OBJECT_PT_MORPH"

	my_data = MORPH

class GENERATOR(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	generate_to: bpy.props.EnumProperty(

		items = (

			( "boost", "Boost", "Boost" ),
			( "jump", "Jump", "Jump" ),
			( "magnetic", "Magnet", "Magnet" )

		),

		name        = "generate_to",
		description = "Generate to"

	)

class GENERATOR_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Generator Properties"
	bl_idname = "OBJECT_PT_GENERATOR"

	my_data = GENERATOR

class RACE_PROGRESS_POINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "CUBE"

	order_number: bpy.props.IntProperty(

		name = "order_number",
		description = "Order Number",
		default = 1,
		min = 1

	)

class RACE_PROGRESS_POINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Race Progress Point Properties"
	bl_idname = "OBJECT_PT_RACE_PROGRESS_POINT"

	my_data = RACE_PROGRESS_POINT

class ROPE_FITPOINT(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY

	empty_type = "SPHERE"
	empty_size = 0.2

	first_fitpoint: bpy.props.BoolProperty(

		name = "First Fitpoint",
		description = "First Fitpoint",
		default = True

	)

	next_fitpoint_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "Next Fitpoint"

	)

	attached_to_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "Attached to"

	)

	mesh: bpy.props.StringProperty(

		default = "rope_medium_medium.x",
		name    = "Mesh to draw along rope"

	)

	slack: bpy.props.EnumProperty(

		items = tuple([("medium", "Medium", "Medium slack")]),

		default     = "medium",
		description = "Rope slack"

	)

	num_links: bpy.props.IntProperty(

		name        = "num_links",
		description = "Number of links"

	)

class ROPE_FITPOINT_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Rope Properties"
	bl_idname = "OBJECT_PT_ROPE_FITPOINT"

	my_data = ROPE_FITPOINT

class SWITCH_TOGGLE(TYPE, bpy.types.PropertyGroup):

	SUPER = SINK

	object_to_toggle: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "object_to_toggle",
		description = "Object to toggle"

	)

class SWITCH_TOGGLE_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Switch Properties"
	bl_idname = "OBJECT_PT_SWITCH_TOGGLE"

	my_data = SWITCH_TOGGLE

class SWITCH_TRIGGER(TYPE, bpy.types.PropertyGroup):

	SUPER = SINK

	object_to_activate: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "object_to_activate",
		description = "Object to activate"

	)

class SWITCH_TRIGGER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Switch Properties"
	bl_idname = "OBJECT_PT_SWITCH_TRIGGER"

	my_data = SWITCH_TRIGGER

class SWITCH_TIMER(TYPE, bpy.types.PropertyGroup):

	SUPER = SINK

	first_object_to_activate: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "first_object_to_activate",
		description = "First object to activate"

	)

	time: bpy.props.IntProperty(

		name = "respawn_time",
		description = "Timer",
		default = 1,
		min = 1,
		subtype = "TIME_ABSOLUTE"

	)

class SWITCH_TIMER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Switch Properties"
	bl_idname = "OBJECT_PT_SWITCH_TIMER"

	my_data = SWITCH_TIMER

class WATERWHEEL_STAND(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	trigger_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "trigger_id",
		description = "Trigger"

	)

class WATERWHEEL_STAND_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Waterwheel Properties"
	bl_idname = "OBJECT_PT_WATERWHEEL_STAND"

	my_data = WATERWHEEL_STAND

class WATERTANK(TYPE, bpy.types.PropertyGroup):

	SUPER = MODEL

	filled_with: bpy.props.EnumProperty(

		items = tuple([("water", "Water", "Fill with water")]),
		name = "filled_with",
		description = "Filled with"

	)

	open: bpy.props.BoolProperty(

		name = "open",
		description = "Is open",
		default = False

	)

class WATERTANK_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Watertank Properties"
	bl_idname = "OBJECT_PT_WATERTANK"

	my_data = WATERTANK

class FLUID_EMITTER(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "SPHERE"

	attached_to_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "attached_to_id",
		description = "Attached to"

	)

	particle_lifetime: bpy.props.IntProperty(

		name = "respawn_time",
		description = "Particle Lifetime",
		default = 1,
		min = 1,
		subtype = "TIME_ABSOLUTE"

	)

class FLUID_EMITTER_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Fluid Emitter Properties"
	bl_idname = "OBJECT_PT_FLUID_EMITTER"

	my_data = FLUID_EMITTER

class FLUID_DRAIN(TYPE, bpy.types.PropertyGroup):

	SUPER = EMPTY
	empty_type = "CUBE"

	attached_to_id: bpy.props.PointerProperty(

		type = bpy.types.Object,
		name = "attached_to_id",
		description = "Attached to"

	)

class FLUID_DRAIN_PANEL(PANEL, bpy.types.Panel):

	bl_label  = "Fluid Drain Properties"
	bl_idname = "OBJECT_PT_FLUID_DRAIN"

	my_data = FLUID_DRAIN

def import_register():

	bpy.utils.register_class(_SBTOOL_PANEL)

	for i in inspect.getmembers(sys.modules[__name__], inspect.isclass):

		if i[0][0] == '_': continue

		if not issubclass(i[1], bpy.types.bpy_struct): continue
		bpy.utils.register_class(i[1])

		if not issubclass(i[1], bpy.types.PropertyGroup): continue
		setattr(bpy.types.Object, i[0], bpy.props.PointerProperty(type = i[1]))

	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def import_unregister():

	for i in inspect.getmembers(sys.modules[__name__], inspect.isclass):

		if not issubclass(i[1], bpy.types.bpy_struct): continue
		bpy.utils.unregister_class(i[1])

	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

