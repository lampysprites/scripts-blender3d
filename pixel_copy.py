import bpy
import bmesh
import mathutils
from mathutils import Vector,Matrix
from .util.rasterize import rasterize
from .util.imagedata import copy_pixel, set_pixel


def shared_edge(tri1, tri2):
    for e1 in tri1.edges:
        for e2 in tri2.edges:
            if e1.index == e2.index:
                return e1.index
    return -1


def list_images(self, context):
    return [(str(i), img.name, "Image") for i, img in enumerate(bpy.data.images)]


def list_uv_maps(self,context):
    return [(str(i), uv.name, "UV layer") for i, uv in enumerate(context.active_object.data.uv_layers)]
    

class SHKI_OT_PixelCopy(bpy.types.Operator):
    """Copy the texture pixel-by-pixel between uv's without resampling"""
    bl_idname = "shurushki.pixel_copy"
    bl_label = "Pixel Copy"
    

    p_source_img: bpy.props.EnumProperty(name="Source", items=list_images, description="The image from which the data is comes from")
    p_source_uv: bpy.props.EnumProperty(name="Source UV", items=list_uv_maps, description="UV layer that aligns to the source texture")
    
    p_dest_img: bpy.props.EnumProperty(name="Output", items=list_images, description="The image to write to")
    p_dest_uv: bpy.props.EnumProperty(name="Output UV", items=list_uv_maps, default=1, description="UV layer for the generated texture")

    p_clear: bpy.props.BoolProperty(name="Clear Image", description="Clear the target image before writing")

    p_highlight: bpy.props.EnumProperty(name="Overlap", items=[('none', "Ignore", "Do nothing"), ('all', "Show All", "Highlight every overlap")], description="Handle pixel overwrites")
    p_highlight_color: bpy.props.FloatVectorProperty(name="Highlight", size=3, subtype='COLOR', min=0.0, max=1.0, default=(1.0,0.0,0.0), description="Show overlap in this color")
    

    @classmethod
    def poll(cls, context):
        obj = None

        if context.mode == 'OBJECT':
            obj = context.active_object
        elif context.mode == 'EDIT_MESH':
            obj = context.edit_object

        return obj is not None and obj.data is not None and obj.data.uv_layers is not None and len(obj.data.uv_layers) > 1
    

    def execute(self, context):
        if int(self.p_source_img) == int(self.p_dest_img) and self.p_clear:
            self.report({'ERROR'}, "Operation cancelled: Can not clear the image when the output is same as the source")
            return {'CANCELLED'}
        
        if int(self.p_source_img) == int(self.p_dest_img) and int(self.p_source_uv) == int(self.p_dest_uv):
            self.report({'WARNING'}, "Operation cancelled: Source and output are identical, nothing to do")
            return {'CANCELLED'}
        
        obj = None # the active mesh
        bm = None # BMesh representation
        faces = None # Target faces
        if context.mode == 'EDIT_MESH':
            obj = bpy.context.edit_object
            # without a copy triangualtion happens the edit mesh, even if bmesh is not converted back x _ x
            bm = bmesh.from_edit_mesh(obj.data).copy()
            faces = [face for face in bm.faces if face.select and not face.hide]
        else:
            obj = bpy.context.active_object
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            faces = bm.faces

        img_from = bpy.data.images[int(self.p_source_img)]
        img_to = bpy.data.images[int(self.p_dest_img)]
        uv_from = bm.loops.layers.uv[int(self.p_source_uv)]
        uv_to = bm.loops.layers.uv[int(self.p_dest_uv)]

        size = [1/x for x in img_to.size]

        
        
        ttion = bmesh.ops.triangulate(bm, faces=faces)
        tris = ttion["faces"]
        
        bm.faces.ensure_lookup_table()

        # track the pixels visited several times
        # dict ((x,y)) => set(faces)
        visited = {}

        if self.p_clear:
            img_to.pixels.foreach_set([i % 4 == 3 and 1.0 or 0.0  for i in range(len(img_to.pixels))])
        
        for tri in tris:
            v1, v2, v3 = (loop[uv_to].uv.to_3d() for loop in tri.loops)
            w1, w2, w3 = (loop[uv_from].uv.to_3d() for loop in tri.loops)

            # iterate over pixels in the UV space
            for (u, v) in rasterize(size, v1, v2, v3):
                source_uv = mathutils.geometry.barycentric_transform(
                    Vector((u + .5 * size[0], v + .5 * size[1], 0)),
                    v1, v2, v3,
                    w1, w2, w3)

                copy_pixel(img_from, img_to, source_uv.x, source_uv.y, u, v)
                
                if self.p_highlight != 'none':
                    if not (u, v) in visited:
                        visited[(u, v)] = set()
                    visited[(u, v)].add(tri.index)
            
            # highlight overlaps
            for (u, v) in visited:
                if len(visited[(u, v)]) == 2:
                    tri1, tri2 = visited[(u, v)]
                    tri1 = bm.faces[tri1]
                    tri2 = bm.faces[tri2]

                    if shared_edge(tri1, tri2) == -1:
                        col = self.p_highlight_color
                        set_pixel(img_to, u, v, col.r, col.g, col.b)

        return {'FINISHED'}


    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)