from .panel_3d import *
from .flatten_edge import *
from .axis_align import *
from .pixel_copy import *
from .sample_render import *
from .explore import *
from .uv_from_grid import *
from .check_weights import *
from .copy_weights import *
from .replace_bone import *
from .flip_groups import *


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
    SHKI_PT_PanelMesh,
    SHKI_PT_PanelSkin,
    SHKI_PT_PanelUV,
    SHKI_PT_PanelRender,
    
    SHKI_OT_FlattenEdge,
    SHKI_OT_AxisAlign,
    SHKI_OT_PixelCopy,
    SHKI_OT_SampleRender,
    SHKI_OT_Explore,
    SHKI_OT_UVFromGrid,
    SHKI_OT_CheckWeights,
    SHKI_OT_CopyWeights,
    SHKI_OT_ReplaceBone,
    SHKI_OT_FlipGroups
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
