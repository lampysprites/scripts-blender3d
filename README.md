# Shurushki for Blender

In-house blender addons, me being the house. Caveat emptor.

# Installation

Same as any other addon, download .zip and install it from the addons menu.

# Scripts

## Mesh

### Flatten Edge

Align (one) selected face in the same plane with the active one, by rotating around the common edge. When the model is triangulated, the latter means the texture mapping is not affected at all.

### Axis Align

Rotate the mesh so that the active face faces the picked axis.


## Skin

### Check Weights

Display all bone groups to which the active vert belongs, and the corresponding weight.

### Copy Weights

Copy weight data from the active to the selected verts. Existing weights are cleared.

### Replace Bone

Move verts from one group to another with the same weights. Preserves the data related to other groups. If the vert already belongs to the new group, the weight is replaced.


## Texture

### Pixel Copy

Fills the texture for the selected faces by looking up every pixel of it in the another texture/uvmap.

### Sample From Render

Fills the texture for the selected faces by looking up every pixel of it in the viewport (ignores overlays). Due to a finely aged bug in the eevee's offscreen render, a workaround had to be added, which, if the bug is ever fixed, will fuck up the gamma. Probably won't work with custom gamma settings too.

### UV From Grid

Project the uvs onto the world grid, so that 1 step corresponds to 1 pixel.


## Render

### Explore

Open the output folder specified in the render settings.