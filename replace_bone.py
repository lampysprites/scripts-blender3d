import bpy
import bmesh
from .check_weights import SHKI_OT_CheckWeights
from bmesh.types import BMVert

def list_vertex_groups_all(self, context):
    return [(str(i), g.name, "Group") for i, g in enumerate(context.edit_object.vertex_groups)]

def list_vertex_groups_selected(self, context):
    selected_groups = set()

    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    verts = [v for v in bm.verts if v.select and not v.hide]

    for g in obj.vertex_groups:
        for v in verts:
            try:
                g.weight(v.index)
                selected_groups.add(g)
                break
            except:
                pass # move along

    return [(str(i), g.name, "Group") for i, g in enumerate(context.edit_object.vertex_groups) if g in selected_groups]


class SHKI_OT_ReplaceBone(bpy.types.Operator):
    """Move verts from one group to another with the same weights"""
    bl_idname = "shurushki.replace_bone"
    bl_label = "Replace Bone"


    p_from: bpy.props.EnumProperty(name="From", items=list_vertex_groups_selected, description="Bone that is replaced")
    p_to: bpy.props.EnumProperty(name="To", items=list_vertex_groups_all, description="Bone that replaces") # ahem


    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.edit_object
        return obj is not None and obj.data is not None


    def execute(self, context):
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [v for v in bm.verts if v.select and not v.hide]
        weights = bm.verts.layers.deform.active

        i_from = int(self.p_from)
        i_to = int(self.p_to)

        changed = 0
        
        for v in verts:
            if i_from in v[weights]:
                changed += 1
                v[weights][i_to] = v[weights][i_from]
                del v[weights][i_from]
                
        # apply changes
        bmesh.update_edit_mesh(obj.data)

        self.report({'INFO'}, f"Changed {changed} verts")

        return {'FINISHED'}
    

    def invoke(self, context, event):
        if list_vertex_groups_selected(self, context):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        
        self.report({'INFO'}, f"Verts aren't attached to a bone")
        return {'CANCELLED'}