GEGL GObject introspection Examples
-----------------------------------

Examples to start playing with GEGL in Python and JavaScript.

Install
-------

We need GEGL and its dependencies compiled with GObject introspection
enabled.  We'll also install MyPaint with GEGL support to play with
its brushes.  We'll build everything in user-space, so no need to be
root or mess the system.

```bash
mkdir gegl-project
cd gegl-project

# clone dependencies

git clone git://git.gnome.org/babl
git clone git://git.gnome.org/gegl
git clone git://git.gnome.org/gegl-gtk
git clone git://gitorious.org/mypaint/mypaint.git

# clone these examples too

git clone https://github.com/manuq/gegl-examples.git

# these variables are to build in user-space and to enable GEGL in
# MyPaint.

mkdir workplace
export prefix=`realpath .`/workplace
export XDG_DATA_DIRS=$prefix/share/:/usr/share/:$XDG_DATA_DIRS
export GI_TYPELIB_PATH=$prefix/lib/girepository-1.0
export PKG_CONFIG_PATH=$prefix/lib/pkgconfig
export LD_LIBRARY_PATH=$prefix/lib
export MYPAINT_ENABLE_GEGL=1

# compile each dependency

cd babl
./autogen.sh --prefix=$prefix
make
make install
cd ..

cd gegl
./autogen.sh --enable-introspection --prefix=$prefix
make
make install
cd ..

cd gegl-gtk
./autogen.sh --enable-introspection --prefix=$prefix --without-vala
make
make install
cd ..

cd mypaint
scons enable_gegl=true enable_introspection=true prefix=$prefix install
cd ..
```

Play
----

For learning purposes, you can see the examples as incremental steps
that grow in complexity.  You can move from step to step with git:

```bash
git checkout -f step-0
```
