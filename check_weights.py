import bpy
import bmesh
from bmesh.types import BMVert

class SHKI_OT_CheckWeights(bpy.types.Operator):
    """Display the weights of the selected vertex"""
    bl_idname = "shurushki.check_weights"
    bl_label = "Check Weights"


    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.edit_object
        return obj is not None and obj.data is not None


    def execute(self, context):
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        v = bm.select_history.active
        groups = []

        if type(v) is not BMVert:
            self.report({'INFO'}, 'No vert selected')
            return {'CANCELLED'}

        for g in obj.vertex_groups:
            try:
                groups.append(f"{g.name:<30} {g.weight(v.index):0.3}")
            except:
                pass # vert not in the group
            
        def draw(self, context):
            col = self.layout.column()
            for t in groups:
                col.label(text=t)
            
            if not groups:
                col.label(text="No Groups")

        bpy.context.window_manager.popup_menu(draw, title = "Vertex Groups", icon = 'NONE')

        return {'FINISHED'}