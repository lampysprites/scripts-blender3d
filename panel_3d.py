import bpy


class SHKI_PT_Panel3D(bpy.types.Panel):
    """hey"""
    bl_label = "Mesh"
    bl_category = "Shurushki"
    bl_idname = "SHKI_PT_panel_3d"
    bl_space_type = 'PROPERTIES'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("shurushki.flatten_edge")

        row = layout.row()
        row.operator("shurushki.axis_align")

        row = layout.row()
        row.operator("shurushki.pixel_copy")

        row = layout.row()
        row.operator("shurushki.sample_render")

        row = layout.row()
        row.operator("shurushki.explore")

        row = layout.row()
        row.operator("shurushki.uv_from_grid")