# .drawio ファイルを読み取り、セクションの座標を抜き出します。
#
# 使い方:
#   poetry run python scripts/parse_drawio.py extract docs/gogatsusai2024.drawio v1
#
# 使い方 v2:
#   poetry run python scripts/parse_drawio.py extract-v2 docs/gogatsusai2024.drawio v2 data/gogatsusai2024/railway_ui.json
#
# 使い方 v3:
#   poetry run python scripts/parse_drawio.py extract-v2 docs/gogatsusai2024_v3.drawio v3 data/gogatsusai2024/railway_ui_v3.json
#   poetry run python scripts/parse_drawio.py generate-python data/gogatsusai2024/railway_ui_v3.json ptcs_control/gogatsusai2024.py
#
# 注意:
#   - PowerShell のリダイレクトを使うと BOM が付いてしまうので Python 側でファイルの書き込みを行うこと。

import itertools
import json
import math
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
@click.argument("drawio_path")
@click.argument("diagram_name")
@click.argument("output_path")
def extract_v2(drawio_path: str, diagram_name: str, output_path: str):
    tree = ET.parse(drawio_path)
    root_element = tree.getroot()

    if root_element.attrib.get("compressed") != "false":
        print("「ファイル > 属性 > 圧縮」から圧縮を無効にしてください。")
        return

    diagram_element = root_element.find(f"diagram[@name={diagram_name!r}]")
    assert diagram_element is not None

    cells: dict[str, tuple[ET.Element | None, ET.Element]] = {}

    for object_element in diagram_element.findall("mxGraphModel/root/object"):
        object_id = object_element.attrib["id"]
        cell_element = object_element.find("mxCell")
        assert cell_element is not None
        cells[object_id] = (object_element, cell_element)

    for cell_element in diagram_element.findall("mxGraphModel/root/mxCell"):
        cell_id = cell_element.attrib["id"]
        cells[cell_id] = (None, cell_element)

    platforms = {}
    junctions = {}
    sections = {}

    for id, (object_element, cell_element) in sorted(cells.items()):
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

    for id, (object_element, cell_element) in sorted(cells.items()):
        if cell_element.attrib.get("edge") == "1":
            points = []

            source_element_id = cell_element.attrib.get("source")
            assert source_element_id is not None, f"辺 {id} に source が設定されていません。"

            target_element_id = cell_element.attrib.get("target")
            assert target_element_id is not None, f"辺 {id} に target が設定されていません。"

            block_id = object_element.attrib.get("blockId") if object_element else None
            assert block_id is not None, f"辺 {id} に blockId が設定されていません。"

            x = junctions[source_element_id]["position"]["x"]
            y = junctions[source_element_id]["position"]["y"]
            points.append({"x": x, "y": y})

            for point_element in cell_element.findall("mxGeometry/Array/mxPoint"):
                x = round(float(point_element.attrib["x"]))
                y = round(float(point_element.attrib["y"]))
                points.append({"x": x, "y": y})

            x = junctions[target_element_id]["position"]["x"]
            y = junctions[target_element_id]["position"]["y"]
            points.append({"x": x, "y": y})

            sections[id] = {"from": source_element_id, "to": target_element_id, "points": points, "block_id": block_id}

    result = {"platforms": platforms, "junctions": junctions, "sections": sections}

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


@cli.command()
@click.argument("json_path")
@click.argument("output_path")
def generate_python(json_path: str, output_path: str):
    with open(json_path) as f:
        data = json.load(f)

    code = ""

    code += "# このファイルは自動生成されたものです。\n"
    code += "# 詳しくは scripts/parse_drawio.py を見てください。\n"
    code += "\n"
    code += "from .components.junction import Junction, JunctionConnection\n"
    code += "from .components.section import Section, SectionConnection\n"
    code += "from .control.base import BaseControl\n"
    code += "\n"
    code += "\n"
    code += "def configure(control: BaseControl) -> None:\n"

    for junction_id, _junction in data["junctions"].items():
        code += f'    {junction_id} = Junction(id="{junction_id}")\n'
    code += "\n"

    for junction_id, _junction in data["junctions"].items():
        code += f"    control.add_junction({junction_id})\n"
    code += "\n"

    for section_id, section in data["sections"].items():
        code += f'    {section_id} = Section(id="{section_id}", length=100.0, block_id="{section["block_id"]}")\n'
    code += "\n"

    for section_id, _section in data["sections"].items():
        code += f"    control.add_section({section_id})\n"
    code += "\n"

    code += "    A, B = SectionConnection.A, SectionConnection.B\n"
    code += "    THROUGH, DIVERGING, CONVERGING = (\n"
    code += "        JunctionConnection.THROUGH,\n"
    code += "        JunctionConnection.DIVERGING,\n"
    code += "        JunctionConnection.CONVERGING,\n"
    code += "    )\n"

    connections = []
    for junction_id, _junction in data["junctions"].items():
        angles = []
        for section_id, section in data["sections"].items():
            if section["from"] == junction_id:
                angle = get_angle(section["points"][1], section["points"][0])
                angles.append((section_id, "A", angle))
            if section["to"] == junction_id:
                angle = get_angle(section["points"][-2], section["points"][-1])
                angles.append((section_id, "B", angle))
        assert len(angles) == 2 or len(angles) == 3
        if len(angles) == 2:
            s0_id, s0_connection, _s0_angle = angles[0]
            s1_id, s1_connection, _s1_angle = angles[1]
            connections.append((s0_id, s0_connection, junction_id, "THROUGH"))
            connections.append((s1_id, s1_connection, junction_id, "CONVERGING"))
        elif len(angles) == 3:
            connections.extend(compute_three_connections(junction_id, angles))

    for section_id, section_connection, junction_id, junction_connection in sorted(connections):
        code += f"    control.connect({section_id}, {section_connection}, {junction_id}, {junction_connection})\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)


def get_angle(p0, p1):
    "p0 から p1 へ伸びるベクトルの角度を計算する"
    return math.atan2(p1["y"] - p0["y"], p1["x"] - p0["x"])


def angle_diff(a0, a1):
    "a0 と a1 の角度の差を劣角で返す"
    return min(abs(a0 - a1), math.tau - abs(a0 - a1))


def compute_three_connections(junction_id, angles):
    assert len(angles) == 3

    for a0, a1, a2 in itertools.permutations(angles):
        s0_id, s0_connection, s0_angle = a0
        s1_id, s1_connection, s1_angle = a1
        s2_id, s2_connection, s2_angle = a2
        if math.isclose(angle_diff(s0_angle, s1_angle), math.pi):
            connections = []
            if angle_diff(s0_angle, s2_angle) < angle_diff(s1_angle, s2_angle):
                connections.append((s0_id, s0_connection, junction_id, "THROUGH"))
                connections.append((s1_id, s1_connection, junction_id, "CONVERGING"))
                connections.append((s2_id, s2_connection, junction_id, "DIVERGING"))
            else:
                connections.append((s0_id, s0_connection, junction_id, "CONVERGING"))
                connections.append((s1_id, s1_connection, junction_id, "THROUGH"))
                connections.append((s2_id, s2_connection, junction_id, "DIVERGING"))
            return connections

    assert False


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
