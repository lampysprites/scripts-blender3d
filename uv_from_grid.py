from bmesh.types import BMFace
import bpy
import bmesh
from mathutils import Vector
from .pixel_copy import list_images

class SHKI_OT_UVFromGrid(bpy.types.Operator):
    """Project UV in a way that a pixel of chosen texture aligns to the view grid"""
    bl_idname = "shurushki.uv_from_grid"
    bl_label = "UV From Grid"
    bl_options = {'REGISTER', 'UNDO'}


    p_checker: bpy.props.EnumProperty(name="Texture", items=list_images, description="Texture used as a size reference for the uvs")
    p_axis: bpy.props.EnumProperty(
        name = "Axis",
        description = "Axis to which to align the face",
        items = [
            ("ZPOS", "Z+", ""),
            ("ZNEG", "Z-", ""),
            ("XPOS", "X+", ""),
            ("XNEG", "X-", ""),
            ("YPOS", "Y+", ""),
            ("YNEG", "Y-", ""),
        ]
    )


    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.edit_object
        return obj is not None and obj.data is not None and obj.data.uv_layers is not None


    def execute(self, context):
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv = bm.loops.layers.uv["UVMap"]
        grid_scale = context.space_data.overlay.grid_scale
        selected_faces = [face for face in bm.faces if face.select and not face.hide]
        # active_face = bm.select_history.active
        size = bpy.data.images[int(self.p_checker)].size; size = Vector((1.0 / size[0], 1.0 / size[1]))
        negate_first = Vector((-1, 1))

        # if type(active_face) is not BMFace:
        #     self.report({'WARNING'}, "Operation cancelled: No face selected")
        #     return {'CANCELLED'}

        # projection
        if self.p_axis == "XPOS":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.yz * size / grid_scale
        elif self.p_axis == "XNEG":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.yz * negate_first * size / grid_scale
        elif self.p_axis == "YPOS":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xz * negate_first * size / grid_scale
        elif self.p_axis == "YNEG":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xz * size / grid_scale
        elif self.p_axis == "ZPOS":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xy * size / grid_scale
        elif self.p_axis == "ZNEG":
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xy * negate_first * size / grid_scale


        # apply changes
        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}


    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)