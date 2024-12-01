#!/usr/bin/env python

from shapely import is_empty
import svgpathtools
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import xml.etree.ElementTree as ET

from typing import Dict

def load_svg_polygons(svg_file, ids):
    """
    Load polygons with specific IDs from an SVG file.
    """
    paths, attributes, svg_attributes = svgpathtools.svg2paths2(svg_file)
    polygons: Dict[str, Polygon] = {}
    for path, attr in zip(paths, attributes):
        if "id" in attr and attr["id"] in ids:
            # Convert the path to a Shapely Polygon
            poly_points = [(seg.start.real, seg.start.imag) for seg in path] + [
                (path[-1].end.real, path[-1].end.imag)
            ]
            polygons[attr["id"]] = Polygon(poly_points)
    return polygons


def save_rectangles_to_svg(output_file, pattern_borders, millings):
    """
    Save a list of millings to an SVG file.
    """

    svg_ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", svg_ns)
    svg = ET.Element("svg", xmlns=svg_ns, version="1.1", width="100%", height="100%")


    def polygon_to_xml(polygon: Polygon, style):
        if not polygon.is_empty and polygon.geom_type == "Polygon":
            # Extract exterior coordinates (ignoring holes for simplicity)
            points = " ".join(f"{x},{y}" for x, y in polygon.exterior.coords)
            
            # Create the SVG <polygon> element
            ET.SubElement(
                svg,
                "polygon",
                points=points,
                style=style,
            )


    for polygon in pattern_borders:
        polygon_to_xml(polygon, "fill:gray")

    for polygon in millings:
        polygon_to_xml(polygon, "stroke:black;stroke-width:0.2;fill:none")

    tree = ET.ElementTree(svg)
    tree.write(output_file)


def kulling(svg_file, output_file, 
            rect_size = 10, space: float = 2,
    alternate = True
    ):

    # Step 1: Load polygons
    ids = ["blade", "cuttting_bounding_box"]
    polygons = load_svg_polygons(svg_file, ids)

    if "blade" not in polygons or "cuttting_bounding_box" not in polygons:
        print("Missing required polygons in SVG.")
        return

    blade = polygons["blade"]
    cuttting_bounding_box = polygons["cuttting_bounding_box"]

    # Step 2: Intersect both polygons
    p_intersect = blade.intersection(cuttting_bounding_box)

    # Step 3: Inset 10 mm (buffering with negative value)
    p_inset = p_intersect.buffer(-10, single_sided = True)

    # Step 4: Find bounding box
    bounding_box = p_inset.bounds
    minx, miny, maxx, maxy = bounding_box

    pattern_borders = []
    milling = []

    for ix in range(0, round(maxx-minx) // rect_size):
        x = ix * rect_size + minx
        for iy in range(0, round(maxy-miny) // rect_size):
            y = iy*rect_size + miny

            rect = box(x, y, x + rect_size, y + rect_size)

            if rect.intersects(p_inset):
                print(f"xy {ix} {iy}")
                pb = rect.intersection(p_inset)
                pattern_borders.append(pb)
                i = pb.buffer(-space / 2)
                iter = 0
                odd = (ix % 2) == 0
                if (iy % 2) == 0:
                    odd = not odd
                print(f"buffering f{odd}")

                while iter < 1000 and not i.is_empty:
                    print(iter, odd, i.area, i)
                    even = (iter % 2 == 0) == odd
                    if ((not alternate) or even):
                        milling.append(i)
                    i = i.buffer(-space)
                    iter += 1

        print("y loops done")

    print("for loops done")


    print(len(milling))
    # Step 6: Export rectangles to SVG
    save_rectangles_to_svg(  output_file, pattern_borders, milling)
    print(f"Output saved to {output_file}")


def main():
    svg_file = "knife.svg"
    output_file = "output.svg"

    kulling(svg_file, output_file, 
            rect_size = 10,
            space = 3
    )


if __name__ == "__main__":
    main()
