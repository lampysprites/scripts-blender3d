from bmesh.types import BMEdge, BMFace
import bpy
import bmesh
from mathutils import Matrix, Vector
from .pixel_copy import list_images, list_uv_maps

# TODO
# * finish 'active'


class SHKI_OT_UVFromGrid(bpy.types.Operator):
    """Project UV in a way that a pixel of chosen texture aligns to the view grid"""
    bl_idname = "shurushki.uv_from_grid"
    bl_label = "UV From Grid"
    bl_options = {'REGISTER', 'UNDO'}


    p_checker: bpy.props.EnumProperty(name="Texture", items=list_images, description="Texture used as a size reference for the UVs")
    p_axis: bpy.props.EnumProperty(
        name = "Axis",
        description = "Direction from which UV will be projected",
        items = [
            ('CLOSEST', "Active Axis", ""),
            ('ACTIVE', "Active Normal", ""),
            ('XPOS', "X+", ""),
            ('XNEG', "X-", ""),
            ('YPOS', "Y+", ""),
            ('YNEG', "Y-", ""),
            ('ZPOS', "Z+", ""),
            ('ZNEG', "Z-", ""),
        ]
    )
    p_dest_uv: bpy.props.EnumProperty(name="UV Layer", items=list_uv_maps, description="UV layer to use")
    p_pin: bpy.props.BoolProperty(name="Pin", description="Pin the UVs afterwards")


    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.edit_object
        return obj is not None and obj.data is not None and obj.data.uv_layers is not None


    def closest_axis(self, d):
            x, y, z = (abs(x) for x in d.xyz)

            if x >= y and x >= z:
                if d.x >= 0:
                    return 'XPOS'
                else:
                    return 'XNEG'
            if y >= x and y >= z:
                if d.y >= 0:
                    return 'YPOS'
                else:
                    return 'YNEG'
            else:
                if d.z >= 0:
                    return 'ZPOS'
                else:
                    return 'ZNEG'


    def execute(self, context):
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        uv = bm.loops.layers.uv[int(self.p_dest_uv)]
        grid_scale = context.space_data.overlay.grid_scale
        selected_faces = [face for face in bm.faces if face.select and not face.hide]
        active_face = bm.select_history.active
        size = bpy.data.images[int(self.p_checker)].size; size = Vector((1.0 / size[0], 1.0 / size[1]))
        negate_first = Vector((-1, 1))

        # auto pick axis
        axis = self.p_axis
        if axis == 'CLOSEST':
            if type(active_face) is not BMFace:
                self.report({'WARNING'}, "Operation cancelled: No active face")
                return {'CANCELLED'}
            axis = self.closest_axis(active_face.normal)

        # projection
        if axis == 'XPOS':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.yz * size / grid_scale
        elif axis == 'XNEG':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.yz * negate_first * size / grid_scale
        elif axis == 'YPOS':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xz * negate_first * size / grid_scale
        elif axis == 'YNEG':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xz * size / grid_scale
        elif axis == 'ZPOS':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xy * size / grid_scale
        elif axis == 'ZNEG':
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].uv.xy = loop.vert.co.xy * negate_first * size / grid_scale
        elif axis == 'ACTIVE':
            # a very different case
            if type(active_face) is not BMFace:
                self.report({'WARNING'}, "Operation cancelled: No active face")
                return {'CANCELLED'}
            
            # grab some edge as a temporary axis, then rotate the basis the same amount in 3d it has to be rotated in the uv
            # to align with pixel edges
            edge:bmesh.types.BMEdge = None
            for e in active_face.edges:
                if e in active_face.edges and e.calc_length() > 0:
                    edge = e
                    break
            assert edge is not None
            ends = [l for l in active_face.loops if edge in l.vert.link_edges]

            dir_uv = Vector((ends[1][uv].uv.x - ends[0][uv].uv.x, ends[1][uv].uv.y - ends[0][uv].uv.y))
            to_x = dir_uv.angle((1.0, 0.0))

            z_3d = active_face.normal
            dir_3d = Vector((ends[1].vert.co.x - ends[0].vert.co.x, ends[1].vert.co.y - ends[0].vert.co.y, ends[1].vert.co.z - ends[0].vert.co.z))
            dir_3d.normalize()
            x_3d = Matrix.Rotation(to_x, 4, z_3d) @ dir_3d
            y_3d = z_3d.cross(x_3d)

            print(x_3d, y_3d, z_3d)
            # basis = Matrix(x_3d, y_3d, z_3d).to_4x4()

        # pin if asked
        if self.p_pin:
            for face in selected_faces:
                for loop in face.loops:
                    loop[uv].pin_uv = True

        # apply changes
        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}
