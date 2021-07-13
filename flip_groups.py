import bpy
import bmesh
from .check_weights import SHKI_OT_CheckWeights
from bmesh.types import BMVert

# TODO create missing groups, optionally

class SHKI_OT_FlipGroups(bpy.types.Operator):
    """TODO"""
    bl_idname = "shurushki.flip_groups"
    bl_label = "Flip Groups"


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
        touched = set() # used to avoid mirroring twice depending on the group order
        
        for g in obj.vertex_groups:
            f_name = ""
            left = False # used to avoid mirroring twice, when the vertex has weights in both groups

            if g.name.endswith(".L"):
                f_name = g.name[:-2] + ".R"
                left = True
            elif g.name.endswith(".l"):
                f_name = g.name[:-2] + ".r"
                left = True
            elif g.name.endswith(".R"):
                f_name = g.name[:-2] + ".L"
            elif g.name.endswith(".r"):
                f_name = g.name[:-2] + ".l"
            
            if not f_name:
                continue
            
            if f_name not in obj.vertex_groups:
                self.report({'WARN'}, f"Group {g.name} doesn't have a symmetric counterpart")
                continue

            f = obj.vertex_groups[f_name]

            for v in verts:
                if (f.index, v.index) in touched:
                    continue

                touched.add((f.index, v.index))
                touched.add((g.index, v.index))

                # irl fizzbuzz
                if g.index in v[weights] and f.index in v[weights] and left:
                    v[weights][g.index], v[weights][f.index] = v[weights][f.index], v[weights][g.index]
                elif g.index in v[weights]:
                    v[weights][f.index] = v[weights][g.index]
                    del v[weights][g.index]
                elif f.index in v[weights]:
                    v[weights][g.index] = v[weights][f.index]
                    del v[weights][f.index]

        # apply changes
        bmesh.update_edit_mesh(obj.data)
        
        self.report({'INFO'}, f"Changed {len(verts)} verts")

        return {'FINISHED'}