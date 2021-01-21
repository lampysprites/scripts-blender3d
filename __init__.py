from .panel_3d import *
from .flatten_edge import *
from .axis_align import *


bl_info = {
    "name": "Shurushki",
    "author": "twitter.com/lampysprites",
    "description": "Blender shortcuts and scripts",
    "blender": (2, 83, 0),
    "version": (1, 0, 0),
    "location": "View3D > Sidebar > Shuruski",
    "warning": "",
    "category": "User"
}


classes = (
    SHKI_PT_Panel3D,
    SHKI_OT_FlattenEdge,
    SHKI_OT_AxisAlign
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
