"""A module used for generating images from binary data."""

from pathlib import Path
import os

def bits(file, start, end):
    """Iterates on the bytes in position [start, end] of a file object, bitwise."""
    file.read(start) # Throws away first bytes
    for i in range(end - start):
        byte = ord(file.read(1))
        for j in range(8):
            yield (byte >> j) & 1

class DxfRect:
    """Simple DXF rectangle element that mimics SVG rect element."""

    def __init__(self, insert=(0, 0), size=(1, 1), **kwargs):
        self.pos    = insert
        self.size   = size
        self.kwargs = kwargs

    @property
    def points(self):
        pts = [
            (0,            0),
            (self.size[0], 0),
            (self.size[0], self.size[1]),
            (0,            self.size[1])
        ]
        return [(pt[0] + self.pos[0], pt[1] + self.pos[1]) for pt in pts]

    def to_polyline(self):
        from dxfwrite import DXFEngine as dxf
        return dxf.polyline(points=self.points, **self.kwargs)

    def to_face3d(self):
        from dxfwrite import DXFEngine as dxf
        return dxf.face3d(points=self.points, **self.kwargs)


class FileMap:
    """Represents a file map."""
    def __init__(self, source_path, invert=False, height=2**4, scale=10):
        self.source_path = Path(source_path)
        self.invert    = invert
        self.height    = height
        self.scale     = scale

    def __str__(self):
        return "FileMap:%s" % self.source_path.name

    def draw(self, start=0, end=None, ext='svg', name=None):
        if end is None:
            end = os.path.getsize(self.source_path)
        if name is None:
            name = self.source_path.name
        name = f"{name}.{ext}"

        if ext == 'svg':
            from svgwrite        import Drawing
            from svgwrite.shapes import Rect
            dwg = Drawing(name, profile='tiny')

        elif ext == 'dxf':
            from dxfwrite import DXFEngine as dxf
            dwg = dxf.drawing(name)

        with open(self.source_path, 'rb') as source_file:
            for i, bit in enumerate(bits(source_file, start, end)):
                if bit == self.invert:
                    x = (i // self.height) * self.scale
                    y = (-i % self.height) * self.scale

                    params = {
                        'insert': (x, y),
                        'size': (self.scale, self.scale)
                    }
                    if ext == 'dxf':
                        rect = DxfRect(**params).to_face3d()
                    else:
                        rect = Rect(**params)
                    dwg.add(rect)
        dwg.save()



if __name__=='__main__':
    fmap = FileMap("test.bin")
    for ext in ('svg', 'dxf'):
        for i in range(8):
            chunk = 2**6
            fmap.draw(i*chunk, (i+1)*chunk, ext=ext, name=i)
