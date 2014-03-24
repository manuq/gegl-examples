#!/usr/bin/env seed

const Gtk = imports.gi.Gtk;
const Gegl = imports.gi.Gegl;
const GeglGtk = imports.gi.GeglGtk3;

const Lang = imports.lang;


var PhotoApp = function () {
    this.graph = undefined;
    this.nodes = {};

    this.createGraph();
    this.initUi();
}

PhotoApp.prototype.createGraph = function () {
    this.graph = new Gegl.Node();

    this.nodes['root'] = this.graph.create_child("gegl:over");

    this.nodes['brightness-contrast'] = this.graph.create_child(
        "gegl:brightness-contrast");

    this.nodes['brightness-contrast'].connect_to(
        "output", this.nodes['root'], "input");

    this.nodes['photo'] = this.graph.create_child("gegl:load");
    this.nodes['photo'].set_property("path", 'sample.jpg');
    this.nodes['photo'].connect_to(
        "output", this.nodes['brightness-contrast'], "input");
}

PhotoApp.prototype.initUi = function () {
    var appWindow = new Gtk.Window({title: "Photo Retouch"});
    appWindow.signal.destroy.connect(Gtk.main_quit);

    var topBox = new Gtk.Box();
    topBox.orientation = Gtk.Orientation.VERTICAL;
    appWindow.add(topBox);

    var viewWidget = new GeglGtk.View();
    viewWidget.set_node(this.nodes['root']);
    viewWidget.set_size_request(800, 400);
    topBox.add(viewWidget);

    contrastLabel = new Gtk.Label();
    contrastLabel.label = "Contrast:";
    topBox.add(contrastLabel);

    contrastAdj = new Gtk.Adjustment();
    contrastAdj.lower = -5;
    contrastAdj.upper = 5;
    contrastAdj.set_value(1);

    contrastAdj.signal.value_changed.connect(
        Lang.bind(this, this.contrastChangedCb));

    contrastScale = new Gtk.Scale();
    contrastScale.set_adjustment(contrastAdj);
    topBox.add(contrastScale);

    brightnessLabel = new Gtk.Label();
    brightnessLabel.label = "Brightness:";
    topBox.add(brightnessLabel);

    brightnessAdj = new Gtk.Adjustment();
    brightnessAdj.lower = -3;
    brightnessAdj.upper = 3;
    brightnessAdj.set_value(0);

    brightnessAdj.signal.value_changed.connect(
        Lang.bind(this, this.brightnessChangedCb));

    brightnessScale = new Gtk.Scale();
    brightnessScale.set_adjustment(brightnessAdj);
    topBox.add(brightnessScale);

    appWindow.show_all();
}

PhotoApp.prototype.run = function () {
    Gtk.main();
}

PhotoApp.prototype.contrastChangedCb = function (adjustment) {
    this.nodes['brightness-contrast'].set_property(
        'contrast', adjustment.value);
}

PhotoApp.prototype.brightnessChangedCb = function (adjustment) {
    this.nodes['brightness-contrast'].set_property(
        'brightness', adjustment.value);
}


function main() {
    Gegl.init(null, 0);
    Gtk.init(null, 0);

    var app = new PhotoApp();
    app.run();
}

main();
