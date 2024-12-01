#!/usr/bin/env python

from build123d import *

svg_file = "knife.svg"

im = import_svg(svg_file)
blade, blade_area, intersection = im[0], im[1], im[2]

show_objects = {}

show_objects["blade"] = blade
show_objects["blade_area"] = blade_area
show_objects["intersection"] = intersection


def create_patterns(name, intersection: Face):
    global show_objects
    show_objects[f"intersection_{name}"] = intersection

    # now I want an inset:

    with BuildSketch() as insetted:
        add(intersection)
        # offset(amount = -10)
    show_objects[f"intersection_{name}_insetted"] = insetted

    bb = insetted.sketch.bounding_box();

    # now create eg rectangles with 10mm distance

    rect_size = 10
    with BuildSketch() as rectangles:
        with Locations(bb.center()):
            with GridLocations(
                rect_size, rect_size,
                round(bb.size.X) // 10,
                round(bb.size.Y) // 10
            ):
                Rectangle(rect_size - 1, rect_size - 1)

    for wire in rectangles.wires():
        print(wire)

    show_objects[f"intersection_{name}_insetted_rectangles"] = rectangles

create_patterns("svg_intersection", intersection)
# this fails
# create_patterns("123intersection", blade.intersect(blade_area))

for k, v in show_objects.items():
  show_object(v, name=k)
