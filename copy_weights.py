import bpy
import bmesh
from .check_weights import SHKI_OT_CheckWeights
from bmesh.types import BMVert

class SHKI_OT_CopyWeights(bpy.types.Operator):
    """Display the weights of the selected vertex"""
    bl_idname = "shurushki.copy_weights"
    bl_label = "Copy Weights"


    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.edit_object
        return obj is not None and obj.data is not None


    def execute(self, context):
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        source = bm.select_history.active
        dests = [v for v in bm.verts if v.select and not v.hide and v is not source]
        weights = bm.verts.layers.deform.active

        if type(source) is not BMVert:
            self.report({'INFO'}, 'No active vert')
            return {'CANCELLED'}
        
        source_groups = [g.index for g in obj.vertex_groups if g.index in source[weights]]
        
        for d in dests:
            d[weights].clear()

            for i in source_groups:
                d[weights][i] = source[weights][i]
                
        # apply changes
        bmesh.update_edit_mesh(obj.data)

        self.report({'INFO'}, f"Moved {len(dests)} verts to {len(source_groups)} layers")
        bpy.ops.shurushki.check_weights() # displays the copied weights

        return {'FINISHED'}