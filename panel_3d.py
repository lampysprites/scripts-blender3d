import bpy

class SHKI_PT_PanelMesh(bpy.types.Panel):
    """hey"""
    bl_label = "Mesh"
    bl_category = "Shurushki"
    bl_idname = "SHKI_PT_panel_mesh"
    bl_space_type = 'PROPERTIES'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("shurushki.flatten_edge")

        row = layout.row()
        row.operator("shurushki.axis_align")


class SHKI_PT_PanelUV(bpy.types.Panel):
    """hey"""
    bl_label = "Texture"
    bl_category = "Shurushki"
    bl_idname = "SHKI_PT_panel_uv"
    bl_space_type = 'PROPERTIES'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("shurushki.pixel_copy")

        row = layout.row()
        row.operator("shurushki.sample_render")

        row = layout.row()
        row.operator("shurushki.uv_from_grid")


class SHKI_PT_PanelSkin(bpy.types.Panel):
    """hey"""
    bl_label = "Skin"
    bl_category = "Shurushki"
    bl_idname = "SHKI_PT_panel_skin"
    bl_space_type = 'PROPERTIES'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("shurushki.check_weights")

        row = layout.row()
        row.operator("shurushki.copy_weights")

        row = layout.row()
        row.operator("shurushki.replace_bone")

        row = layout.row()
        row.operator("shurushki.flip_groups")


class SHKI_PT_PanelRender(bpy.types.Panel):
    """hey"""
    bl_label = "Render"
    bl_category = "Shurushki"
    bl_idname = "SHKI_PT_panel_render"
    bl_space_type = 'PROPERTIES'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("shurushki.explore")