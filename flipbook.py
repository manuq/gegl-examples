#!/usr/bin/env python

import sys
sys.path.append("../mypaint")

from gi.repository import Gegl, Gtk, Gdk, GObject
from gi.repository import GeglGtk3 as GeglGtk

from lib import tiledsurface, brush


class Cel(object):
    def __init__(self):
        self.surface = tiledsurface.GeglSurface()
        self.surface_node = self.surface.get_node()


class Timeline(object):
    def __init__(self, length):
        self.idx = 0
        self.frames = []
        for idx in range(length):
            self.frames.append(Cel())

    def go_previous(self, loop=False):
        if not loop:
            if self.idx == 0:
                return False
        else:
            if self.idx == 0:
                self.idx = len(self.frames)-1
                return True

        self.idx -= 1
        return True

    def go_next(self, loop=False):
        if not loop:
            if self.idx == len(self.frames)-1:
                return False
        else:
            if self.idx == len(self.frames)-1:
                self.idx = 0
                return True

        self.idx += 1
        return True

    def get_cel(self, idx=None):
        if idx is None:
            idx = self.idx

        if idx < 0 or idx > len(self.frames)-1:
            return False

        return self.frames[idx]


class FlipbookApp(object):
    def __init__(self):
        brush_file = open('../mypaint/brushes/classic/charcoal.myb')
        brush_info = brush.BrushInfo(brush_file.read())
        brush_info.set_color_rgb((0.0, 0.0, 0.0))
        self.brush = brush.Brush(brush_info)

        self.button_pressed = False
        self.last_event = (0.0, 0.0, 0.0)  # (x, y, time)

        self.onionskin_on = True

        self.surface = None
        self.surface_node = None

        self.play_hid = None

        self.timeline = Timeline(12)
        self.update_surface()

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

        self.nodes['layer1-over'] = self.graph.create_child("gegl:over")

        self.nodes['layer1-opacity'] = self.graph.create_child("gegl:opacity")
        self.nodes['layer1-opacity'].set_property('value', 0.5)

        self.nodes['layer2-over'] = self.graph.create_child("gegl:over")

        self.nodes['layer2-opacity'] = self.graph.create_child("gegl:opacity")
        self.nodes['layer2-opacity'].set_property('value', 0.5)

        self.nodes['background'].connect_to(
            "output", self.nodes['root'], "input")

        self.nodes['layer1-over'].connect_to(
            "output", self.nodes['root'], "aux")

        self.nodes['layer1-opacity'].connect_to(
            "output", self.nodes['layer1-over'], "aux")

        self.nodes['layer2-over'].connect_to(
            "output", self.nodes['layer1-opacity'], "input")

        self.nodes['layer2-opacity'].connect_to(
            "output", self.nodes['layer2-over'], "aux")

        self.update_graph()

    def update_graph(self):
        self.surface_node.connect_to(
            "output", self.nodes['layer1-over'], "input")

        if not self.onionskin_on:
            return

        prev_cel1 = self.timeline.get_cel(self.timeline.idx-1)
        if prev_cel1:
            prev_surface_node1 = prev_cel1.surface_node
            prev_surface_node1.connect_to(
                "output", self.nodes['layer2-over'], "input")
        else:
            self.nodes['layer2-over'].disconnect("input")

        prev_cel2 = self.timeline.get_cel(self.timeline.idx-2)
        if prev_cel2:
            prev_surface_node2 = prev_cel2.surface_node
            prev_surface_node2.connect_to(
                "output", self.nodes['layer2-opacity'], "input")
        else:
            self.nodes['layer2-opacity'].disconnect("input")


    def init_ui(self):
        window = Gtk.Window()
        window.props.title = "Flipbook"
        window.connect("destroy", self.destroy_cb)
        window.connect("key-release-event", self.key_release_cb)

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

    def update_surface(self):
        cel = self.timeline.get_cel()
        self.surface = cel.surface
        self.surface_node = cel.surface_node

    def go_previous(self, loop=False):
        changed = self.timeline.go_previous(loop)
        if changed:
            self.update_surface()
            self.update_graph()

        return changed

    def go_next(self, loop=False):
        changed = self.timeline.go_next(loop)
        if changed:
            self.update_surface()
            self.update_graph()

        return changed

    def toggle_play_stop(self):
        if self.play_hid == None:
            self.play_hid = GObject.timeout_add(42, self.go_next, True)
        else:
            GObject.source_remove(self.play_hid)
            self.play_hid = None

    def toggle_onionskin(self):
        self.onionskin_on = not self.onionskin_on

        if self.onionskin_on:
            self.nodes['layer1-opacity'].connect_to(
                "output", self.nodes['layer1-over'], "aux")
        else:
            self.nodes['layer1-over'].disconnect("aux")

        self.update_graph()

    def key_release_cb(self, widget, event):
        if event.keyval == Gdk.KEY_Left:
            self.go_previous()
        elif event.keyval == Gdk.KEY_Right:
            self.go_next()
        elif event.keyval == Gdk.KEY_p:
            self.toggle_play_stop()
        elif event.keyval == Gdk.KEY_o:
            self.toggle_onionskin()


if __name__ == '__main__':
    Gegl.init([])
    Gtk.init([])

    app = FlipbookApp()
    app.run()
