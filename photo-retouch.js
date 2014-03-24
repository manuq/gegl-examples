#!/usr/bin/env seed

const Gtk = imports.gi.Gtk;
const GeglGtk = imports.gi.GeglGtk3;


var PhotoApp = function () {
    this.initUi();
}

PhotoApp.prototype.initUi = function () {
    var appWindow = new Gtk.Window({title: "Photo Retouch"});
    appWindow.signal.destroy.connect(Gtk.main_quit);

    var topBox = new Gtk.Box();
    topBox.orientation = Gtk.Orientation.VERTICAL;
    appWindow.add(topBox);

    var viewWidget = new GeglGtk.View();
    viewWidget.set_size_request(800, 400);
    topBox.add(viewWidget);

    appWindow.show_all();
}

PhotoApp.prototype.run = function () {
    Gtk.main();
}


function main() {
    Gtk.init(null, 0);

    var app = new PhotoApp();
    app.run();
}

main();
