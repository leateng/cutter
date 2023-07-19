from ezdxf.math import BoundingBox, Vec3

from cutter.consts import ALIGNMENT

# from IPython import embed


class GCode:
    def __init__(
        self, dxf_entities, tool_radius, cutter_offset, rotation_speed
    ) -> None:
        self.dxf_entities = dxf_entities
        self.tool_radius = tool_radius
        self.cutter_offset = cutter_offset
        self.rotation_speed = rotation_speed
        self.instructions = []

    def prepare_instructions(self):
        self.instructions.append("G90 (Absolute programming)")
        self.instructions.append("G17 (XY plane)")
        # self.instructions.append("G40 (Cancel radius comp)")
        self.instructions.append(
            "G00 Z{:.1f} (z safe margin)".format(self.safe_height())
        )
        # self.instructions.append("T1 M6")
        self.instructions.append(
            "#set ToolParam(1; 4; {:.1f})#".format(
                self.tool_radius - self.cutter_offset
            )
        )
        self.instructions.append("D1")
        self.instructions.append(f"S{self.rotation_speed} M03")

    def end_instructions(self):
        self.instructions.append(
            "G01 Z{:.1f} (z safe margin)".format(self.safe_height())
        )
        self.instructions.append("S0 M05")
        self.fast_move_xy(0, 0)
        self.instructions.append("M2 (Program end)")

    def draw_entities(self):
        if len(self.dxf_entities) == 1 and self.dxf_entities[0].dxftype() == "CIRCLE":
            self.instructions.append("G00 Z{:.1f} (cut deepth)".format(ALIGNMENT["z"]))
            self.draw_circle(self.dxf_entities[0])
        else:
            self.draw_line_and_arc()

    def draw_circle(self, circle):
        # embed()
        center = circle.dxf.center
        radius = circle.dxf.radius

        start = Vec3(center.x, center.y - radius, 0)
        end = Vec3(center.x, center.y + radius, 0)

        self.fast_move_xy(start.x, start.y - 10)
        self.instructions.append("F400")
        self.move_xy(start.x, start.y)
        self.instructions.append(
            "G03 X{:.1f} Y{:.1f} I{:.1f}  J{:.1f}".format(end.x, end.y, 0, radius)
        )
        self.instructions.append(
            "G03 X{:.1f} Y{:.1f} I{:.1f}  J{:.1f}".format(start.x, start.y, 0, -radius)
        )

    def draw_line_and_arc(self):
        pass

    def move_xy(self, x, y):
        self.instructions.append("G01 X{:.1f} Y{:.1f}".format(x, y))

    def move_z(self, z):
        self.instructions.append("G01 Z{:.1f}".format(z))

    def fast_move_xy(self, x, y):
        self.instructions.append("G00 X{:.1f} Y{:.1f}".format(x, y))

    def fast_move_z(self, z):
        self.instructions.append("G00 Z{:.1f}".format(z))

    def safe_height(self):
        return float(ALIGNMENT["z"]) + 10

    def generate(self) -> str:
        self.check_entities()
        self.check_alignment()

        self.translate_entities()

        self.prepare_instructions()
        self.draw_entities()

        # self.fast_move_z(15)
        self.end_instructions()

        return "\n".join(self.instructions)

    def check_alignment(self):
        # ALIGNMENT["x"] = 0
        # ALIGNMENT["y"] = 0
        # ALIGNMENT["z"] = 0

        if ALIGNMENT["x"] is None or ALIGNMENT["y"] is None or ALIGNMENT["z"] is None:
            raise Exception("未对刀!")

    def check_entities(self):
        if len(self.dxf_entities) == 0:
            raise Exception("没有可用的dxf实体!")

        if len(self.dxf_entities) == 1 and self.dxf_entities[0].dxftype() != "CIRCLE":
            raise Exception("dxf实体不封闭!")

    def get_entity_bbox(self, e):
        if e.dxf.dxftype == "CIRCLE":
            return self.get_circle_bounding_box(e)

        if e.dxf.dxftype == "LINE":
            return self.get_line_bounding_box(e)

        if e.dxf.dxftype == "ARC":
            return self.get_arc_bounding_box(e)

    def get_circle_bounding_box(self, circle):
        center = Vec3(circle.dxf.center)
        radius = circle.dxf.radius

        min_point = center - Vec3(radius, radius, 0)
        max_point = center + Vec3(radius, radius, 0)

        return BoundingBox([min_point, max_point])

    def get_line_bounding_box(self, line):
        start_point = line.dxf.start
        end_point = line.dxf.end

        min_x = min(start_point[0], end_point[0])
        min_y = min(start_point[1], end_point[1])
        max_x = max(start_point[0], end_point[0])
        max_y = max(start_point[1], end_point[1])

        min_point = Vec3(min_x, min_y, 0)
        max_point = Vec3(max_x, max_y, 0)

        return BoundingBox([min_point, max_point])

    def get_arc_bounding_box(self, arc):
        return BoundingBox([Vec3(0, 0, 0), Vec3(0, 0, 0)])

    def bbox_min_point(self):
        bboxs = []
        for e in self.dxf_entities:
            bboxs.append(self.get_entity_bbox(e))

        min_point = min(bboxs[0])
        x = min_point.x
        y = min_point.y
        # embed()
        for b in bboxs:
            min_point = min(b)
            if x > min_point.x:
                x = min_point.x

            if y > min_point.y:
                y = min_point.y

        return Vec3(x, y, 0)

    def calc_offset(self):
        alignment_x = ALIGNMENT["x"]
        alignment_y = ALIGNMENT["y"]

        min_point = self.bbox_min_point()
        print(f"min_point={min_point}")
        offset_x = alignment_x - min_point.x
        offset_y = alignment_y - min_point.y

        return Vec3(offset_x, offset_y, 0)

    def translate_entities(self):
        offset = self.calc_offset()
        print(f"offet={offset}")

        for e in self.dxf_entities:
            e.translate(offset.x, offset.y, 0)
