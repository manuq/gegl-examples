#!/usr/bin/env python

from gi.repository import Gegl, Gtk
from gi.repository import GeglGtk3 as GeglGtk


class FlipbookApp(object):
    def __init__(self):
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

    def init_ui(self):
        window = Gtk.Window()
        window.props.title = "Flipbook"
        window.connect("destroy", self.destroy_cb)

        top_box = Gtk.Box()
        top_box.props.orientation = Gtk.Orientation.VERTICAL;
        window.add(top_box)

        view_widget = GeglGtk.View()
        view_widget.set_node(self.nodes['root'])
        view_widget.set_autoscale_policy(GeglGtk.ViewAutoscale.DISABLED)
        view_widget.set_size_request(800, 400)
        top_box.add(view_widget)

        window.show_all()

    def run(self):
        return Gtk.main()

    def destroy_cb(self, *ignored):
        Gtk.main_quit()


if __name__ == '__main__':
    Gegl.init([])
    Gtk.init([])

    app = FlipbookApp()
    app.run()
