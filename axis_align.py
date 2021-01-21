import bpy
import bmesh
from mathutils import Vector,Matrix,Quaternion


class SHKI_OT_AxisAlign(bpy.types.Operator):
    """Rotate the selecton to align the active face normal with the provided axis"""
    bl_idname = "shurushki.axis_align"
    bl_label = "Axis Align Face"
    bl_options = {'REGISTER', 'UNDO'}

    p_axis:bpy.props.EnumProperty(
            name = "Axis",
            description = "Axis to which to align the face",
            items = [
                ("XPOS", "X+", ""),
                ("XNEG", "X-", ""),          
                ("YPOS", "Y+", ""),
                ("YNEG", "Y-", ""),              
                ("ZPOS", "Z+", ""),
                ("ZNEG", "Z-", ""),                  
            ]
        )
    p_local:bpy.props.BoolProperty(
        name="Local",
        description = "Use the object's coordinates instead of global"
    )

    @classmethod
    def poll(cls, context):        
        if context.mode != 'EDIT_MESH':
            return False
            
        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'FACE'}
        f = bm.select_history.active

        return f is not None and isinstance(f, bmesh.types.BMFace)

    def p_axis_to_vector(self):
        v = None
        lt = bpy.context.edit_object.matrix_local

        if self.p_axis == "XPOS":
            v = Vector((1, 0, 0))
        elif self.p_axis == "XNEG":
            v = Vector((-1, 0, 0))
        elif self.p_axis == "YPOS":
            v = Vector((0, 1, 0))
        elif self.p_axis == "YNEG":
            v = Vector((0, -1, 0))
        elif self.p_axis == "ZPOS":
            v = Vector((0, 0, 1))
        elif self.p_axis == "ZNEG":
            v = Vector((0, 0, -1))
        
        if not self.p_local:
            v = lt.inverted() @ v

        return v


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    def execute(self, context):
        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'FACE'}
        f = bm.select_history.active

        diff = f.normal.rotation_difference(self.p_axis_to_vector()).to_matrix()
        bmesh.ops.rotate(bm, cent=f.calc_center_bounds(), matrix=diff, verts=[v for v in bm.verts if v.select])

        # finalize
        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}
