def copy_pixel(src, dst, sx, sy, dx, dy):
    """copy pixel data from one image to another. When the coordinate is out of range nothing happens."""
    sw, sh = src.size
    dw, dh = dst.size
    sidx = 4 * (int(sy * sh) * sw + int(sx * sw))
    didx = 4 * (int(dy * dh) * dw + int(dx * dw))
    try:
        dst.pixels[didx] = src.pixels[sidx]    
        dst.pixels[didx + 1] = src.pixels[sidx + 1]
        dst.pixels[didx + 2] = src.pixels[sidx + 2]
        dst.pixels[didx + 3] = src.pixels[sidx + 3]
    except:
        pass


def set_pixel(image, x, y, r=0.0, g=0.0, b=0.0, a=1.0):
    """Set pixel to a given color. When the coordinate is out of range nothing happens."""
    w, h = image.size
    idx = 4 * (int(y * h) * w + int(x * w))
    try:
        image.pixels[idx] = r
        image.pixels[idx + 1] = g
        image.pixels[idx + 2] = b
        image.pixels[idx + 3] = a
    except:
        pass


def get_pixel(image, x, y):
    """Set pixel to a given color. When the coordinate is out of range nothing happens."""
    w, h = image.size
    idx = 4 * (int(y * h) * w + int(x * w))
    try:
        return image.pixels[idx], image.pixels[idx + 1], image.pixels[idx + 2], image.pixels[idx + 3]
    except:
        return None