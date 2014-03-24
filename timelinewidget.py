import cairo

from gi.repository import Gtk
from gi.repository import Gdk

HEIGHT = 30.0


def _get_cairo_color(gdk_color):
    return (float(gdk_color.red), float(gdk_color.green),
            float(gdk_color.blue))


class TimelineWidget(Gtk.DrawingArea):
    def __init__(self, app):
        Gtk.DrawingArea.__init__(self)

        self.app = app

        self.props.hexpand = True

        self._pixbuf = None

        self.fg_color = _get_cairo_color(
            self.get_style_context().lookup_color('theme_fg_color')[1])

        self.background_color = _get_cairo_color(
            self.get_style_context().lookup_color('theme_bg_color')[1])

        self.selected_color = _get_cairo_color(
            self.get_style_context().lookup_color(
                'theme_selected_bg_color')[1])

        self.connect('draw', self.draw_cb)
        self.connect('configure-event', self.configure_cb)

        self.set_size_request(-1, HEIGHT)

    def configure_cb(self, widget, event, data=None):
        width = self.get_allocated_width()
        height = self.get_allocated_height()

        if self._pixbuf is not None:
            self._pixbuf.finish()
            self._pixbuf = None

        self._pixbuf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)

        return False

    def draw_cb(self, widget, context):
        if self._pixbuf is None:
            print('No buffer to paint')
            return False

        pixbuf_context = cairo.Context(self._pixbuf)
        self.draw_background(pixbuf_context)
        self.draw_selected(pixbuf_context)
        self.draw_grid(pixbuf_context)

        context.set_source_surface(self._pixbuf, 0, 0)
        context.paint()

    def draw_background(self, context):
        width = self.get_allocated_width()

        context.set_source_rgb(*self.background_color)
        context.rectangle(0, 0, width, HEIGHT)
        context.fill()

    def draw_selected(self, context):
        context.set_source_rgb(*self.selected_color)

        cel_width = self.get_allocated_width() * 1.0 / len(self.app.timeline.frames)
        x = cel_width * self.app.timeline.idx

        context.rectangle(x, 0, cel_width, HEIGHT)
        context.fill()

    def draw_grid(self, context):
        context.set_source_rgb(*self.fg_color)
        context.set_line_width(1)

        cel_width = self.get_allocated_width() * 1.0 / len(self.app.timeline.frames)
        frames_length = len(self.app.timeline.frames)
        for i in range(frames_length + 1):
            x = cel_width * i
            context.move_to(x, 0)
            context.line_to(x, HEIGHT)
            context.stroke()
