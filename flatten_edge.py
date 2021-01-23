import bpy
import bmesh
import math
from mathutils import Vector,Matrix

class SHKI_OT_FlattenEdge(bpy.types.Operator):
    """Flatten the adjacent faces without distorting the mesh"""
    bl_idname = "shurushki.flatten_edge"
    bl_label = "Flatten Edge"
    bl_options = {'REGISTER', 'UNDO'}
    
    p_flip: bpy.props.BoolProperty(name="Reverse Rotation")
    
    @classmethod
    def poll(cls, context):        
        if context.mode != 'EDIT_MESH':
            return False
        return True
        
        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'EDGE'}
        ax = bm.select_history.active

        return ax is not None and isinstance(ax, bmesh.types.BMEdge) and 2 == len(ax.link_faces)


    def execute(self, context):

        # check if two edges are geometrically the same
        def has_same_verts(e1, e2):
            return (e1.verts[0].co == e2.verts[0].co and e1.verts[1].co == e2.verts[1].co) or (e1.verts[0].co == e2.verts[1].co and e1.verts[1].co == e2.verts[0].co)

        # used to hack around the selection weirdness by re-selecting the faces
        def are_all_edges_select(f):
            for e in f.edges:
                if not e.select:
                    return False
            return True 

        # Get the active mesh
        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        bm.select_mode = {'EDGE'}
        ax = bm.select_history.active

        # prepare the transform
        rotcent = Vector(ax.verts[0].co)
        rotax = Vector(ax.verts[1].co) - rotcent
        rotangle = ax.calc_face_angle_signed()
        rotmat = Matrix.Rotation(rotangle, 4, rotax)

        # kinda hard to figure out which direction the angle is, so let' just
        # test it the same way it's applied later and flip it if there's a mistake
        face_a = None
        face_b = None
        for f in ax.link_faces:
            if f.select:
                face_a = f
            else:
                face_b = f

        ndiff = rotmat @ face_a.normal - face_b.normal
        if ndiff.dot(ndiff) > 0.001:
            rotangle = -rotangle

        # just in case let user override it
        if self.p_flip:
            rotangle = -rotangle
        rotmat = Matrix.Rotation(rotangle, 4, rotax)
        
        # disconnect the selected part of the mesh
        splits = [f for f in bm.faces if are_all_edges_select(f)]
        split = bmesh.ops.split(bm, geom=splits)['geom']

        # reconnect what became of the active edge
        merge_verts = list()
        for e in bm.edges:
            if has_same_verts(e, ax):
                merge_verts += list(e.verts)
            e.select = False
        bmesh.ops.remove_doubles(bm, verts=merge_verts, dist=0.01)

        # reselect what became of the selection
        for vef in split:
            if vef.is_valid:
                vef.select = True
                
        # transform
        split_verts = [vef for vef in split if isinstance(vef, bmesh.types.BMVert) and vef.is_valid]
        bmesh.ops.rotate(bm, cent=rotcent, matrix=rotmat, verts=split_verts)

        # finalize
        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}
