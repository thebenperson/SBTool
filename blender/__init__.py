bl_info = {
	"name": "Switchball Level Editor",
	"author": "Ben Stockett",
	"version": (1, 0),
	"blender": (2, 80, 0),
	"location": "View3D > Add > Mesh > New Object",
	"description": "Switchball Level Editor",
	"doc_url": "https://github.com/thebenperson/sbtool",
	"category": "3D View"
}

import bpy
import os

from . model import load_model

from . level import import_register, import_unregister, TYPE

object_list = (

	"CAMERA_LOOKAT",
	"FLUID_CONTACT",
	"LEVEL_FINISH_POINT"

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

	"MELTER",
	"TNTCRATE_SMALL",
	"TNTCRATE_LARGE",
	"MARBLEBALL",

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

	# fluid cloth models

	"CANNONBALL_SMALL",
	"METALCRATE_LARGE",
	"METALCRATE_MEDIUM",
	"METALCRATE_SMALL"

	"FLOORFAN",
	"MAGNET",
	"PUMP",
	"PUSHPOLE_STAND"

	"FAN",
	"PUSHPROPELLER_STAND",
	"SWINGBOARD_STAND",
	"SWINGPOLE_STAND"

	"HOVER_SMALL",
	"HOVER_LARGE",

	"ACHIEVEMENT_TRIGGER",
	"TUTORIAL_TRIGGER",
	"POINT_LIGHT",
	"WAYPOINT",
	"GYROCOPTER",
	"CLOTH_FITPOINT",
	"OBJECT_SPAWNPOINT",
	"PLAYER_SPAWNPOINT",
	"CANNON_FOOT",
	"WATERCANNON_BARREL",
	"CAMERA_POSITION",
	"CAMERA_WAYPOINT",
	"CAMERA_ZONEPOINT",
	"MORPH",
	"GENERATOR",
	"RACE_PROGRESS_POINT",
	"ROPE_FITPOINT",
	"SWITCH_TOGGLE",
	"SWITCH_TRIGGER",
	"SWITCH_TIMER",
	"WATERWHEEL_STAND",
	"WATERTANK",
	"FLUID_EMITTER",
	"FLUID_DRAIN"

)

class SBTool_AddonPreferences(bpy.types.AddonPreferences):

	bl_idname = __package__

	install_path: bpy.props.StringProperty(

		description = "Switchball base install Path",
		subtype     = "DIR_PATH"

	)

	def draw(self, context):

		layout = self.layout
		row = layout.row()

		row.prop(self, "install_path", text="Switchball install path")

class SBTool(bpy.types.Panel):

	"""Switchball Level Editor"""

	bl_label       = "Switchball Level Editor"
	bl_idname      = "SCENE_PT_layout"
	bl_space_type  = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context     = "scene"

	def draw(self, context):

		layout = self.layout
		scene  = context.scene

		row = layout.row()
		row.label(text="Select an object")

		row = layout.row()
		row.operator("model_list.refresh", text="Refresh")

		row = layout.row()
		row.template_list("ModelList", "", scene, "model_list", scene, "model_list_index")

class ListItem(bpy.types.PropertyGroup):

	name: bpy.props.StringProperty()

class ModelList(bpy.types.UIList):

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

		layout.label(text=item.name)
		ops = layout.operator("model_list.click", text="+")
		ops.name = item.name

class ModelListRefresh(bpy.types.Operator):

	bl_idname = "model_list.refresh"
	bl_label  = "Refresh Model List"

	def execute(self, context):

		for i in object_list:

			item = context.scene.model_list.add()
			item.name = i

		return { "FINISHED" }

class ModelListClick(bpy.types.Operator):

	bl_idname = "model_list.click"
	bl_label  = "Add Model"

	name: bpy.props.StringProperty()

	def execute(self, context):

		cls = TYPE.lookup(self.name)
		cls.new(type = self.name)

		return { "FINISHED" }

classes = (

	SBTool_AddonPreferences,
	SBTool,
	ModelList,
	ModelListRefresh,
	ModelListClick,
	ListItem

)

def register():

	for i in classes:

		bpy.utils.register_class(i)

	bpy.types.Scene.model_list = bpy.props.CollectionProperty(type=ListItem)
	bpy.types.Scene.model_list_index = bpy.props.IntProperty(default=0)

	import_register()

def unregister():

	for i in classes:

		bpy.utils.unregister_class(i)

	import_unregister()

if __name__ == "__main__":

	register()

