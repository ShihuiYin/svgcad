from math import sqrt

class basic_style(object):
    def __init__(self, line_width=1, line_color="black", line_style="solid", fill_color="red", opacity=1):
        self._line_width = line_width
        self._line_color = line_color
        self._line_style = line_style
        self._fill_color = fill_color
        self._opacity = opacity
    
    def get_line_width(self):
        return self._line_width

    def get_line_color(self):
        return self._line_color

    def get_line_style(self):
        return self._line_style

    def get_fill_color(self):
        return self._fill_color

    def get_opacity(self):
        return self._opacity

class basic_shape(object):
    def __init__(self, center=[0,0], size=[1,1], style="default"):
        self._center = center
        self._size = size
        self._style = style
        self._id = "unassigned"

    def get_center(self):
        return self._center

    def get_size(self):
        return self._size

    def get_style(self):
        return self._style

    def get_line_width(self):
        return self.get_style().get_line_width()

    def get_line_color(self):
        return self.get_style().get_line_color()

    def get_line_style(self):
        return self.get_style().get_line_style()

    def get_fill_color(self):
        return self.get_style().get_fill_color()

    def get_opacity(self):
        return self.get_style().get_opacity()

    def get_id(self):
        return self._id

    def get_span(self):
        center = self.get_center()
        size = self.get_size()
        return (center[0] - size[0]/2, center[1] - size[1]/2, center[0] + size[0]/2, center[1] + size[1]/2)

    def style(self, style="default"):
        # apply a new style to this shape
        if isinstance(style, basic_shape):
            self._style = style.get_style()
        else:
            self._style = style
        return self

    def translate(self, delta):
        new_center = (self._center[0] + delta[0], self._center[1] + delta[1])
        self._center = new_center
        return self

    def to_svg(self):
        return  NotImplemented

class line(basic_shape):
    def __init__(self, start=[0,0], end=[1,1], style="default"):
        self._start = start
        self._end = end
        super(line, self).__init__(center=[(start[0]+end[0])/2, (start[1]+end[1])/2], size=[abs(end[0]-start[0]), abs(end[1]-start[1])], style=style)
    
    def to_svg(self):
        x1, y1 = self._start 
        x2, y2 = self._end
        stroke = self.get_line_color()
        stroke_width = self.get_line_width()
        out_string = ' <line x1="%d" y1="%d" x2="%d" y2="%d"\n' % (x1, y1, x2, y2)
        out_string += 'stroke="%s" stroke-width="%s" />\n' % (stroke, stroke_width)
        return out_string

class polygon(basic_shape):
    def __init__(self, points=[[0,0],[2,0],[1,1]], style="default"):
        self._points = points
        xs = [points[i][0] for i in range(len(points))]
        ys = [points[i][1] for i in range(len(points))]
        x1 = min(xs)
        x2 = max(xs)
        y1 = min(ys)
        y2 = max(ys)
        center = [(x1+x2)/2, (y1+y2)/2]
        size = [x2-x1, y2-y1]
        super(polygon, self).__init__(center=center, size=size, style=style)

    def to_svg(self):
        stroke = self.get_line_color()
        stroke_width = self.get_line_width()
        fill = self.get_fill_color()
        out_string = ' <polygon points="'
        for p in self._points:
            out_string += '%d,%d ' % (p[0], p[1])
        out_string += '"\n'
        out_string += 'fill="%s" stroke="%s" stroke-width="%s" />\n' % (fill, stroke, stroke_width)
        return out_string

class rect(basic_shape):
    def __init__(self, center=[0,0], size=[1,1], style="default"):
        super(rect, self).__init__(center, size, style)
    
    def to_svg(self):
        x, y = self.get_center()
        width, height = self.get_size()
        stroke = self.get_line_color()
        stroke_width = self.get_line_width()
        fill = self.get_fill_color()
        out_string = '  <rect x="%d" y="%d" width="%d" height="%d"\n' % (x-width/2, y-height/2, width, height)
        out_string += 'fill="%s" stroke="%s" stroke-width="%s" />\n' % (fill, stroke, stroke_width)
        return out_string

class circle(basic_shape):
    def __init__(self, center=[0,0], radius=1, style="default"):
        super(circle, self).__init__(center=center, size=[radius*2, radius*2], style=style)

    def to_svg(self):
        x, y = self.get_center()
        width, height = self.get_size()
        radius = width / 2
        stroke = self.get_line_color()
        stroke_width = self.get_line_width()
        fill = self.get_fill_color()
        out_string = '  <circle cx="%d" cy="%d" r="%d"\n' % (x, y, radius)
        out_string += '          fill="%s" stroke="%s" stroke-width="%s" />\n' % (fill, stroke, stroke_width)
        return out_string
        
class canvas(object):
    def __init__(self, bg_color="none", border_width=0, border_color="none", default_style=None, margin=10):
        self._border_width = border_width
        self._bg_color = bg_color
        self._border_color = border_color
        self._shapes = []
        self._margin = margin
        self._width = self._margin * 2
        self._height = self._margin * 2
        if default_style is None:
            default_style = basic_style()
        self._default_style = default_style
        self._span = (99999999, 99999999, -99999999, -999999999)

    def get_shapes(self):
        return self._shapes

    def set_default_style(self, style):
        self._default_style = style
        return self

    def get_default_style(self):
        return self._default_style

    def get_span(self):
        return self._span

    def get_margin(self):
        return self._margin

    def _set_span(self, span):
        self._span = span
        return self

    def _append_shape(self, shape):
        canvas_span = self.get_span()
        shape_span = shape.get_span()
        top_left_x = shape_span[0] if shape_span[0] < canvas_span[0] else canvas_span[0]
        top_left_y = shape_span[1] if shape_span[1] < canvas_span[1] else canvas_span[1]
        bottom_right_x = shape_span[2] if shape_span[2] > canvas_span[2] else canvas_span[2]
        bottom_right_y = shape_span[3] if shape_span[3] > canvas_span[3] else canvas_span[3]
        self._set_span((top_left_x, top_left_y, bottom_right_x, bottom_right_y))
        self._shapes.append(shape)
        return self

    def _adjust_shapes(self):
        canvas_span = self.get_span()
        canvas_margin = self.get_margin()
        delta_x = -canvas_span[0] + canvas_margin
        delta_y = -canvas_span[1] + canvas_margin
        for shape in self.get_shapes():
            shape.translate((delta_x, delta_y))
        new_canvas_span = (canvas_span[0] + delta_x, canvas_span[1] + delta_y, canvas_span[2] + delta_x, canvas_span[3] + delta_y)
        self._set_span(new_canvas_span)
        return self

    def get_size(self):
        span = self.get_span()
        margin = self.get_margin()
        self._width = span[2] - span[0] + 2 * margin
        self._height = span[3] - span[1] + 2 * margin
        return (self._width, self._height)

    def rect(self, center=[0, 0], size=[5, 5], style="default"):
        if style == "default":
            style = self.get_default_style()
        shape = rect(center, size, style)
        self._append_shape(shape)

    def circle(self, center=[0, 0], radius=4, style="default"):
        if style == "default":
            style = self.get_default_style()
        shape = circle(center, radius, style)
        self._append_shape(shape)

    def line(self, start=[0, 0], end=[1, 1], style="default"):
        if style == "default":
            style = self.get_default_style()
        shape = line(start, end, style)
        self._append_shape(shape)

    def polygon(self, points=[], style="default"):
        if style == "default":
            style = self.get_default_style()
        shape = polygon(points, style)
        self._append_shape(shape)

    def arrow(self,start=[0,0], end=[10,10], line_width=10, arrow_size=20,style="default"):
        if style == "default":
            style = self.get_default_style()
        x1,y1 = start
        x2,y2 = end
        length=sqrt((x2-x1)**2+(y2-y1)**2)
        x2i = x2 - arrow_size/2*sqrt(3)/length*(x2-x1)
        y2i = y2 - arrow_size/2*sqrt(3)/length*(y2-y1)
        dx = line_width/2*(y2-y1)/length
        dy = line_width/2*(x2-x1)/length
        points = [[x1-dx,y1+dy],[x2i-dx,y2i+dy],[x2i-dx/line_width*arrow_size,y2i+dy/line_width*arrow_size],[x2,y2],[x2i+dx/line_width*arrow_size,y2i-dy/line_width*arrow_size],
            [x2i+dx,y2i-dy],[x1+dx,y1-dy]]
        shape = polygon(points, style)
        self._append_shape(shape)

    def to_svg(self, filename=None):
        self._adjust_shapes()
        width, height = self.get_size()
        border_style = basic_style(line_width=self._border_width, line_color=self._border_color, fill_color=self._bg_color)
        box = rect(center=[width/2, height/2], size=[width-self._border_width, height-self._border_width], style=border_style)
        out_string = '<?xml version="1.0" standalone="no"?>\n'
        out_string += '<svg width="%dcm" height="%dcm" viewBox="0 0 %d %d"\n' % (width/100, height/100, width, height)
        out_string += '     xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
        out_string += box.to_svg()
        for s in self.get_shapes():
            out_string += s.to_svg()
        out_string += '</svg>'
        if filename is not None:
            with open(filename, 'w+') as f:
                f.write(out_string)
        return out_string

if __name__ == "__main__":
    default_style = basic_style(line_width=10, fill_color="yellow", line_color="navy")
    highlight_style = basic_style(line_width=10, fill_color="olive", line_color="black")
    arrow_style = basic_style(line_width=0, fill_color="black", line_color="black")
    c = canvas(bg_color="lightblue", margin=40, border_width=5, border_color="red")
    for i in range(15):
        for j in range(15):
            c.rect((500*i, 300*j), (400,200), default_style)
            c.circle((500*i, 300*j), 100, highlight_style)
    c.line((0,0), (200,200), default_style)
    c.polygon(((20,20), (80,60), (100, 20)), default_style)
    c.arrow((200,500), (500,500), line_width=10, arrow_size=60, style=arrow_style)
    print(c.to_svg('/mnt/c/Users/admin/Downloads/test.svg'))
        
