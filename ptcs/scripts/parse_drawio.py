# .drawio ファイルを読み取り、セクションの座標を抜き出します。
#
# 使い方:
#   poetry run python scripts/parse_drawio.py extract docs/gogatsusai2024.drawio v1
#
# 使い方 v2:
#   poetry run python scripts/parse_drawio.py extract-v2 docs/gogatsusai2024.drawio v2 > data/gogatsusai2024/railway_ui.json


import json
import xml.etree.ElementTree as ET

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("path")
@click.argument("diagram_name")
def extract(path: str, diagram_name: str):
    tree = ET.parse(path)
    root_element = tree.getroot()

    if root_element.attrib.get("compressed") != "false":
        print("「ファイル > 属性 > 圧縮」から圧縮を無効にしてください。")
        return

    diagram_element = root_element.find(f"diagram[@name={diagram_name!r}]")
    assert diagram_element is not None

    sections = {}

    for cell_element in diagram_element.findall("mxGraphModel/root/mxCell"):
        cell_id = cell_element.attrib["id"]

        if cell_element.attrib.get("edge") == "1":
            source_point_element = cell_element.find('mxGeometry/mxPoint[@as="sourcePoint"]')
            assert source_point_element is not None, f"sourcePoint not found in cell {cell_id}"
            target_point_element = cell_element.find('mxGeometry/mxPoint[@as="targetPoint"]')
            assert target_point_element is not None, f"targetPoint not found in cell {cell_id}"
            point_elements = cell_element.findall("mxGeometry/Array/mxPoint")

            points = []

            for point_element in [source_point_element, *point_elements, target_point_element]:
                x = round(float(point_element.attrib["x"]))
                y = round(float(point_element.attrib["y"]))
                points.append({"x": x, "y": y})

            sections[cell_id] = {"points": points}

    result = {"sections": sections}
    print(json.dumps(result, indent=2))


@cli.command()
@click.argument("path")
@click.argument("diagram_name")
def extract_v2(path: str, diagram_name: str):
    tree = ET.parse(path)
    root_element = tree.getroot()

    if root_element.attrib.get("compressed") != "false":
        print("「ファイル > 属性 > 圧縮」から圧縮を無効にしてください。")
        return

    diagram_element = root_element.find(f"diagram[@name={diagram_name!r}]")
    assert diagram_element is not None

    cells: dict[str, ET.Element] = {}

    for object_element in diagram_element.findall("mxGraphModel/root/object"):
        object_id = object_element.attrib["id"]
        cell_element = object_element.find("mxCell")
        assert cell_element is not None
        cells[object_id] = cell_element

    for cell_element in diagram_element.findall("mxGraphModel/root/mxCell"):
        cell_id = cell_element.attrib["id"]
        cells[cell_id] = cell_element

    platforms = {}
    junctions = {}
    sections = {}

    for id, cell_element in cells.items():
        if cell_element.attrib.get("vertex") == "1":
            # 円の場合
            if "ellipse" in cell_element.attrib["style"].split(";"):
                geometry_element = cell_element.find("mxGeometry")
                assert geometry_element is not None

                x = round(float(geometry_element.attrib["x"]))
                y = round(float(geometry_element.attrib["y"]))
                width = round(float(geometry_element.attrib["width"]))
                height = round(float(geometry_element.attrib["height"]))

                position = {"x": (x + width // 2), "y": (y + height // 2)}
                junctions[id] = {"position": position}

            # テキストの場合
            elif "text" in cell_element.attrib["style"].split(";"):
                pass

            # 長方形の場合
            else:
                geometry_element = cell_element.find("mxGeometry")
                assert geometry_element is not None

                x = round(float(geometry_element.attrib["x"]))
                y = round(float(geometry_element.attrib["y"]))
                width = round(float(geometry_element.attrib["width"]))
                height = round(float(geometry_element.attrib["height"]))

                position = {"x": (x + width // 2), "y": (y + height // 2)}
                platforms[id] = {"position": position}

    for id, cell_element in cells.items():
        if cell_element.attrib.get("edge") == "1":
            points = []

            source_element_id = cell_element.attrib.get("source")
            assert source_element_id is not None, f"辺 {id} に source が設定されていません。"

            target_element_id = cell_element.attrib.get("target")
            assert target_element_id is not None, f"辺 {id} に target が設定されていません。"

            points.append(
                {
                    "x": junctions[source_element_id]["position"]["x"],
                    "y": junctions[source_element_id]["position"]["y"],
                }
            )

            for point_element in cell_element.findall("mxGeometry/Array/mxPoint"):
                x = round(float(point_element.attrib["x"]))
                y = round(float(point_element.attrib["y"]))
                points.append({"x": x, "y": y})

            points.append(
                {
                    "x": junctions[target_element_id]["position"]["x"],
                    "y": junctions[target_element_id]["position"]["y"],
                }
            )

            sections[id] = {"from": source_element_id, "to": target_element_id, "points": points}

    result = {"platforms": platforms, "junctions": junctions, "sections": sections}
    print(json.dumps(result, indent=2))


@cli.command()
@click.argument("path")
@click.argument("diagram_name")
def scale(path: str, diagram_name: str):
    tree = ET.parse(path)
    root_element = tree.getroot()

    diagram_element = root_element.find(f"diagram[@name={diagram_name!r}]")
    assert diagram_element is not None

    for a in diagram_element.findall(".//*[@x]"):
        a.attrib["x"] = str(float(a.attrib["x"]) * 2)
        a.attrib["y"] = str(float(a.attrib["y"]) * 2)

    for a in diagram_element.findall(".//*[@width]"):
        a.attrib["width"] = str(float(a.attrib["width"]) * 2)
        a.attrib["height"] = str(float(a.attrib["height"]) * 2)

    tree.write(path)


if __name__ == "__main__":
    cli()
