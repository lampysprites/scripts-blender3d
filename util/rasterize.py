import math
from numpy import linspace

def rasterize(grid, vert1, vert2, vert3):
    """
        Iterate over a triangle with a fixed step.
        args:
            grid - (u, v) grid step for both directions
            verts - vectors for vertices of a triangle
        Yields tuples (u, v) for the bottom-left corner of the pixel
    """
    v1, v2, v3 = sorted((vert1, vert2, vert3), key=lambda v: v.x)
    gx, gy = grid

    # fill with vertical bars between trianle sides
    # first loop from the left to the middle vertex, second is the rest

    # use floor/ceil to include all partially included pixels
    xstart = sfloor(gx, v1.x)
    xend = sceil(gx, v3.x)
    xmidsteps = int((sceil(gx, v2.x) - xstart) / gx)
    xsteps = int((xend - xstart) / gx)

    for i in range(xsteps):
        x = xstart + i * gx

        # let's check both sides of the pixel to handle upwards/downwards edge
        ystart = v1.lerp(v3, i / xsteps).y
        ystart2 = v1.lerp(v3, (i + 1) / xsteps).y
        yend, yend2 = 3, 3
        if i < xmidsteps:
            yend = v1.lerp(v2, i / xmidsteps).y
            yend2 = v1.lerp(v2, (i + 1) / xmidsteps).y
        else:
            yend = v2.lerp(v3, (i - xmidsteps) / (xsteps - xmidsteps)).y
            yend2 = v2.lerp(v3, (i + 1 - xmidsteps) / (xsteps - xmidsteps)).y
        
        # find the outer points and round to grid
        ystart, _, _, yend = sorted((ystart, ystart2, yend, yend2))
        ystart = sfloor(gy, ystart)
        yend = sceil(gy, yend)

        for y in linspace(ystart, yend - gy, int((yend - ystart) / gy)):
            yield (x, y)


def sfloor(step, x):
    """floor to the nearest multiple of step"""
    return math.floor(x / step) * step


def sceil(step, x):
    """ceil to the nearest multiple of step"""
    return math.ceil(x / step) * step