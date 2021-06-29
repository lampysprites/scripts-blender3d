def copy_pixel(srcpixels, dstpixels, srcsize, sx, sy, dstsize, dx, dy):
    """copy pixel data from one image to another. When the coordinate is out of range nothing happens. DO NOT PASS TUPLE IT WONT WORK"""
    sw, sh = srcsize
    dw, dh = dstsize
    sidx = 4 * (int(sy * sh) * sw + int(sx * sw))
    didx = 4 * (int(dy * dh) * dw + int(dx * dw))
    try:
        dstpixels[didx] = srcpixels[sidx]    
        dstpixels[didx + 1] = srcpixels[sidx + 1]
        dstpixels[didx + 2] = srcpixels[sidx + 2]
        dstpixels[didx + 3] = srcpixels[sidx + 3]
    except:
        pass


def set_pixel(imagepixels, imagesize, x, y, r=0.0, g=0.0, b=0.0, a=1.0):
    """Set pixel to a given color. When the coordinate is out of range nothing happens. DO NOT PASS TUPLE IT WONT WORK"""
    w, h = imagesize
    idx = 4 * (int(y * h) * w + int(x * w))
    try:
        imagepixels[idx] = r
        imagepixels[idx + 1] = g
        imagepixels[idx + 2] = b
        imagepixels[idx + 3] = a
    except:
        pass


def get_pixel(imagepixels, imagesize, x, y):
    """Set pixel to a given color. When the coordinate is out of range nothing happens."""
    w, h = imagesize
    idx = 4 * (int(y * h) * w + int(x * w))
    try:
        return imagepixels[idx], imagepixels[idx + 1], imagepixels[idx + 2], imagepixels[idx + 3]
    except:
        return None