#!/usr/bin/env python

import sys
sys.path.append("../mypaint")

from gi.repository import Gegl, Gtk
from gi.repository import GeglGtk3 as GeglGtk

from lib import tiledsurface, brush


class FlipbookApp(object):
    def __init__(self):
        brush_file = open('../mypaint/brushes/classic/charcoal.myb')
        brush_info = brush.BrushInfo(brush_file.read())
        brush_info.set_color_rgb((0.0, 0.0, 0.0))
        self.brush = brush.Brush(brush_info)

        self.button_pressed = False
        self.last_event = (0.0, 0.0, 0.0)  # (x, y, time)

        self.surface = tiledsurface.GeglSurface()
        self.surface_node = self.surface.get_node()

        self.graph = None
        self.nodes = {}

        self.create_graph()
        self.init_ui()


    def create_graph(self):
        self.graph = Gegl.Node()

        self.nodes['background'] = self.graph.create_child("gegl:rectangle")
        self.nodes['background'].set_property('color', Gegl.Color.new("#fff"))
        self.nodes['background'].set_property("width", 800)
        self.nodes['background'].set_property("height", 400)

        self.nodes['root'] = self.graph.create_child("gegl:over")

        self.nodes['background'].connect_to(
            "output", self.nodes['root'], "input")

        self.surface_node.connect_to(
            "output", self.nodes['root'], "aux")

    def init_ui(self):
        window = Gtk.Window()
        window.props.title = "Flipbook"
        window.connect("destroy", self.destroy_cb)

        top_box = Gtk.Box()
        top_box.props.orientation = Gtk.Orientation.VERTICAL;
        window.add(top_box)

        event_box = Gtk.EventBox()
        event_box.connect("motion-notify-event", self.motion_to_cb)
        event_box.connect("button-press-event", self.button_press_cb)
        event_box.connect("button-release-event", self.button_release_cb)
        top_box.add(event_box)

        view_widget = GeglGtk.View()
        view_widget.set_node(self.nodes['root'])
        view_widget.set_autoscale_policy(GeglGtk.ViewAutoscale.DISABLED)
        view_widget.set_size_request(800, 400)
        event_box.add(view_widget)

        window.show_all()

    def run(self):
        return Gtk.main()

    def destroy_cb(self, *ignored):
        Gtk.main_quit()

    def motion_to_cb(self, widget, event):
        (x, y, time) = event.x, event.y, event.time

        pressure = 0.5
        dtime = (time - self.last_event[2])/1000.0
        if self.button_pressed:
            self.surface.begin_atomic()
            self.brush.stroke_to(self.surface.backend, x, y, pressure,
                                 0.0, 0.0, dtime)
            self.surface.end_atomic()

        self.last_event = (x, y, time)

    def button_press_cb(self, widget, event):
        self.button_pressed = True

    def button_release_cb(self, widget, event):
        self.button_pressed = False
        self.brush.reset()


if __name__ == '__main__':
    Gegl.init([])
    Gtk.init([])

    app = FlipbookApp()
    app.run()
