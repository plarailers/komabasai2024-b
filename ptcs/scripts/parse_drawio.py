# .drawio ファイルを読み取り、セクションの座標を抜き出します。
# 使い方:
#   poetry run python scripts/parse_drawio.py docs/gogatsusai2024.drawio v1

import json
import xml.etree.ElementTree as ET

import click


@click.command
@click.argument("path")
@click.argument("diagram_name")
def main(path: str, diagram_name: str):
    tree = ET.parse(path)
    root_element = tree.getroot()

    diagram_element = root_element.find(f"diagram[@name={diagram_name!r}]")
    assert diagram_element is not None

    sections = {}

    for cell_element in diagram_element.findall("mxGraphModel/root/mxCell"):
        if cell_element.attrib.get("edge") == "1":
            source_point_element = cell_element.find('mxGeometry/mxPoint[@as="sourcePoint"]')
            assert source_point_element is not None
            target_point_element = cell_element.find('mxGeometry/mxPoint[@as="targetPoint"]')
            assert target_point_element is not None
            point_elements = cell_element.findall("mxGeometry/Array/mxPoint")

            points = []

            for point_element in [source_point_element, *point_elements, target_point_element]:
                x = round(float(point_element.attrib["x"]))
                y = round(float(point_element.attrib["y"]))
                points.append({"x": x, "y": y})

            id = cell_element.attrib["id"]
            sections[id] = {"points": points}

    result = {"sections": sections}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
