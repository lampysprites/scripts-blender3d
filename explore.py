import bpy
import os
import webbrowser

class SHKI_OT_Explore(bpy.types.Operator):
    """Open the output folder"""
    bl_idname = "shurushki.explore"
    bl_label = "Explore"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):       
        path = bpy.path.abspath(context.scene.render.filepath)

        if not os.path.isdir(path):
            path = os.path.dirname(path)

        return os.path.isdir(path)


    def execute(self, context):
        path = bpy.path.abspath(context.scene.render.filepath)

        if not os.path.isdir(path):
            path = os.path.dirname(path)

        if os.path.isdir(path):
            webbrowser.open(path)
            return {'FINISHED'}
        else:
            self.report('INFO', "The output path is not an existing directory.")
            return {'CANCELLED'}
