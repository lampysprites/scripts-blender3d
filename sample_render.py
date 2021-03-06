import bpy
import bmesh
import math
import random
import bgl
from gpu.types import GPUOffScreen
from mathutils import Vector,Matrix,Color
from bpy_extras.view3d_utils import location_3d_to_region_2d
import mathutils.geometry

from .util.rasterize import rasterize
from .util.imagedata import set_pixel, get_pixel
from .util.srgb import linear_to_srgb
from .pixel_copy import shared_edge, list_images, list_uv_maps


class SHKI_OT_SampleRender(bpy.types.Operator):
    """Unproject pixels from a render back into the texture"""
    bl_idname = "shurushki.sample_render"
    bl_label = "Sample From Render"

    p_dest_img: bpy.props.EnumProperty(name="Output", items=list_images, description="The image to write to")
    p_dest_uv: bpy.props.EnumProperty(name="UV Layer", items=list_uv_maps, description="UV layer for the generated texture")

    p_clear: bpy.props.BoolProperty(name="Clear Image", description="Clear the target image before writing")
    p_no_overwire: bpy.props.BoolProperty(name="No Overwrite", description="Only write to empty (black) pixels")

    p_highlight: bpy.props.EnumProperty(name="Overlap", items=[('none', "Ignore", "Do nothing"), ('all', "Show All", "Highlight every overlap")], description="Handle pixel overwrites")
    p_highlight_color: bpy.props.FloatVectorProperty(name="Highlight", size=3, subtype='COLOR', min=0.0, max=1.0, default=(1.0,0.0,0.0), description="Show overlap in this color")
    
    
    @classmethod
    def poll(cls, context):  
        return bpy.context.active_object is not None


    def render_view_offscreen(self, context):
        sv3d = context.space_data
        # backup settings and set them to render
        overlays_were = sv3d.overlay.show_overlays
        sv3d.overlay.show_overlays = False
        shading_was = sv3d.shading.type
        sv3d.shading.type = 'RENDERED'

        width = context.region.width
        height = context.region.height
        offscreen = GPUOffScreen(width, height)    
        scene = context.scene
        view_matrix = context.region_data.view_matrix
        projection_matrix = context.region_data.window_matrix

        with offscreen.bind():
            offscreen.draw_view3d(
                scene,
                context.view_layer,
                context.space_data,
                context.region,
                view_matrix,
                projection_matrix)

            buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 4)
            bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

        offscreen.free()
        sv3d.overlay.show_overlays = overlays_were
        sv3d.shading.type = shading_was

        return buffer


    def execute(self, context):
        buf = self.render_view_offscreen(context)

        img = bpy.data.images[int(self.p_dest_img)]
        size = [1/l for l in img.size]
        if self.p_clear:
            img.pixels.foreach_set([i % 4 == 3 and 1.0 or 0.0  for i in range(len(img.pixels))])

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

        uv_layer = bm.loops.layers.uv[int(self.p_dest_uv)]
        
        ttion = bmesh.ops.triangulate(bm, faces=faces)
        tris = ttion["faces"]
        
        bm.faces.ensure_lookup_table()

        # track the pixels visited several times
        # dict ((x,y)) => set(faces)
        visited = {}

        for tri in tris:

            x1, x2, x3 = (obj.matrix_world @ Vector(x.co) for x in tri.verts)
            v1, v2, v3 = (loop[uv_layer].uv.to_3d() for loop in tri.loops)

            # iterate over pixels in the UV space
            for (u, v) in rasterize(size, v1, v2, v3):
                if self.p_no_overwire:
                    r,g,b,_a = get_pixel(img, u, v)
                    if r > 0.0 or g > 0.0 or b > 0.0:
                        continue

                # find the pixel's position in the scene space
                space_coord = mathutils.geometry.barycentric_transform(
                    Vector((u + size[0]*.5, v + size[1]*.5, 0.0)),
                    v1, v2, v3,
                    x1, x2, x3)

                screen_coord = location_3d_to_region_2d(context.region, context.region_data, space_coord)

                try:
                    buf_idx = 4 * (int(screen_coord.y) * context.region.width + int(screen_coord.x))
                    r = linear_to_srgb(buf[buf_idx] / 255)
                    g = linear_to_srgb(buf[buf_idx + 1] / 255)
                    b = linear_to_srgb(buf[buf_idx + 2] / 255)
                    set_pixel(img, u, v, r, g, b)
                except:
                    pass
                
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
