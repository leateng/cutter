from ezdxf.math import BoundingBox, Vec3

# from IPython import embed

from cutter.consts import ALIGNMENT
import math


class GCode:
    def __init__(
        self, dxf_entities, tool_radius, cutter_offset, rotation_speed
    ) -> None:
        self.dxf_entities = dxf_entities
        self.tool_radius = tool_radius
        self.cutter_offset = cutter_offset
        self.rotation_speed = rotation_speed
        self.instructions = []

    def generate(self) -> str:
        self.check_tool_params()
        self.check_entities()
        self.check_alignment()

        self.translate_entities()

        self.prepare_instructions()
        self.draw_entities()

        # self.fast_move_z(15)
        self.end_instructions()

        return "\n".join(self.instructions)

    def prepare_instructions(self):
        self.instructions.append("G90 (Absolute programming)")
        self.instructions.append("G17 (XY plane)")
        # self.instructions.append("G40 (Cancel radius comp)")
        self.instructions.append(
            "G00 Z{:.3f} (z safe margin)".format(self.safe_height())
        )
        # self.instructions.append("T1 M6")
        self.instructions.append(
            "#set ToolParam(1; 4; {:.3f})#".format(
                self.tool_radius - self.cutter_offset
            )
        )
        self.instructions.append("D1")
        self.instructions.append(f"S{self.rotation_speed} M03")
        self.set_right_compensation()

    def end_instructions(self):
        self.instructions.append(
            "G01 Z{:.3f} (z safe margin)".format(self.safe_height())
        )
        self.instructions.append("S0 M05")
        self.stop_compensation()
        self.fast_move_xy(0, 0)
        self.instructions.append("M2 (Program end)")

    def draw_entities(self):
        if len(self.dxf_entities) == 1 and self.dxf_entities[0].dxftype() == "CIRCLE":
            self.draw_circle(self.dxf_entities[0])
        else:
            self.draw_line_and_arc()

    def draw_circle(self, circle):
        # embed()
        center = circle.dxf.center
        radius = circle.dxf.radius

        start = Vec3(center.x, center.y - radius, 0)
        end = Vec3(center.x, center.y + radius, 0)

        self.move_to_prepare_point(start)
        self.set_move_speed(400)
        self.move_to_cut_deepth()
        self.move_xy(start.x, start.y)
        self.instructions.append(
            "G03 X{:.3f} Y{:.3f} I{:.3f}  J{:.3f}".format(end.x, end.y, 0, radius)
        )
        self.instructions.append(
            "G03 X{:.3f} Y{:.3f} I{:.3f}  J{:.3f}".format(start.x, start.y, 0, -radius)
        )

    def draw_line_and_arc(self):
        (start_entity, start_point, end_point) = self.get_start_entity()

        self.move_to_prepare_point(start_point)
        self.set_move_speed(400)
        self.move_to_cut_deepth()
        self.move_xy(start_point.x, start_point.y)

        entity = start_entity
        sp = start_point
        ep = end_point

        while entity is not None:
            if entity.dxftype() == "LINE":
                print(f"move to {ep.x} {ep.y}")
                self.move_xy(ep.x, ep.y)

            if entity.dxftype() == "ARC":
                center = entity.dxf.center

                instruct = (
                    "G03" if self.is_same_point(entity.start_point, sp) else "G02"
                )
                self.instructions.append(
                    "{} X{:.3f} Y{:.3f} I{:.3f}  J{:.3f}".format(
                        instruct, ep.x, ep.y, center.x - sp.x, center.y - sp.y
                    )
                )

            (entity, sp, ep) = self.get_next_entity(entity.dxf.handle, ep)
            if entity is None or entity.dxf.handle == start_entity.dxf.handle:
                break

    def move_xy(self, x, y):
        self.instructions.append("G01 X{:.3f} Y{:.3f}".format(x, y))

    def move_z(self, z):
        self.instructions.append("G01 Z{:.3f}".format(z))

    def fast_move_xy(self, x, y):
        self.instructions.append("G00 X{:.3f} Y{:.3f}".format(x, y))

    def fast_move_z(self, z):
        self.instructions.append("G00 Z{:.3f}".format(z))

    def safe_height(self):
        return float(ALIGNMENT["z"]) + 10

    def move_to_prepare_point(self, start_point):
        self.fast_move_xy(start_point.x, start_point.y - 10)

    def move_to_cut_deepth(self):
        self.instructions.append("G00 Z{:.3f} (cut deepth)".format(ALIGNMENT["z"]))

    def set_move_speed(self, speed):
        self.instructions.append(f"F{speed}")

    def set_right_compensation(self):
        self.instructions.append("G42")

    def stop_compensation(self):
        self.instructions.append("G40")

    def check_alignment(self):
        ALIGNMENT["x"] = 0
        ALIGNMENT["y"] = 0
        ALIGNMENT["z"] = 0

        if ALIGNMENT["x"] is None or ALIGNMENT["y"] is None or ALIGNMENT["z"] is None:
            raise Exception("未对刀!")

    def check_entities(self):
        if len(self.dxf_entities) == 0:
            raise Exception("没有可用的dxf实体!")

        if len(self.dxf_entities) == 1 and self.dxf_entities[0].dxf.dxftype != "CIRCLE":
            raise Exception("dxf实体不封闭!")

    def check_tool_params(self):
        if self.rotation_speed == 0:
            raise Exception("刀具转速未配置!")

        if (self.tool_radius - self.cutter_offset) == 0:
            raise Exception("刀具半径配置错误!")

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

    def get_start_point_entity(self):
        entities_map = {}
        dist_lines = []

        for e in self.dxf_entities:
            entities_map[e.dxf.handle] = e
            if e.dxftype() == "LINE":
                p, m = self.min_point(e.dxf.start, e.dxf.end)
                dist_lines.append((e, m, p))
            if e.dxftype() == "ARC":
                p, m = self.min_point(e.start_point, e.end_point)
                dist_lines.append((e, m, p))

        dist_lines.sort(key=lambda x: x[1])

        # embed()
        return (dist_lines[0][0], dist_lines[1][0])

    def min_point(self, p1, p2):
        m1 = p1.magnitude
        m2 = p2.magnitude

        if m1 < m2:
            return (p1, m1)
        else:
            return (p2, m2)

    def get_entities_by_point(self, point):
        entities = []
        for e in self.dxf_entities:
            if e.dxftype() == "LINE":
                print(f"entity[{e.dxf.handle}]")
                if self.is_same_point(point, e.dxf.start) or self.is_same_point(
                    point, e.dxf.end
                ):
                    entities.append(e)
            if e.dxftype() == "ARC":
                if self.is_same_point(point, e.start_point) or self.is_same_point(
                    point, e.end_point
                ):
                    entities.append(e)

        return entities

    def get_start_point(self):
        points = []

        for e in self.dxf_entities:
            if e.dxftype() == "LINE":
                points.append(e.dxf.start)
                points.append(e.dxf.end)
            if e.dxftype() == "ARC":
                points.append(e.start_point)
                points.append(e.end_point)

        points.sort(key=lambda x: x.magnitude)

        return points[0]

    def get_start_entity(self):
        point = self.get_start_point()
        start_entities = self.get_entities_by_point(point)

        if len(start_entities) != 2:
            raise Exception("找不到起始点！")

        e1 = start_entities[0]
        e2 = start_entities[1]

        p1 = (
            self.entity_end_point(e1)
            if self.is_same_point(self.entity_start_point(e1), point)
            else self.entity_start_point(e1)
        )
        p2 = (
            self.entity_end_point(e2)
            if self.is_same_point(self.entity_start_point(e2), point)
            else self.entity_start_point(e2)
        )

        if math.atan2(p1.y, p1.x) < math.atan2(p2.y, p2.x):
            return (e1, point, p1)
        else:
            return (e2, point, p2)

    def entity_start_point(self, entity):
        if entity.dxftype() == "LINE":
            return entity.dxf.start

        if entity.dxftype() == "ARC":
            return entity.start_point

    def entity_end_point(self, entity):
        if entity.dxftype() == "LINE":
            return entity.dxf.end

        if entity.dxftype() == "ARC":
            return entity.end_point

    def get_next_entity(self, entity_id, point):
        start_point = None
        end_point = None

        for e in self.dxf_entities:
            if e.dxf.handle != entity_id:
                if e.dxftype() == "LINE":
                    start_point = e.dxf.start
                    end_point = e.dxf.end

                if e.dxftype() == "ARC":
                    start_point = e.start_point
                    end_point = e.end_point

                if self.is_same_point(point, start_point):
                    return (e, start_point, end_point)

                if self.is_same_point(point, end_point):
                    return (e, end_point, start_point)

        return (None, None, None)

    def is_same_point(self, p1, p2):
        epsilon = 0.001
        return p1.distance(p2) < epsilon

    def is_end(self, start_point, point):
        return self.is_same_point(start_point, point)
