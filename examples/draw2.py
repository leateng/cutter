import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
import ezdxf
from qtpy.QtGui import QPainterPath


class DXFViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 创建一个场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 加载DXF文件
        self.load_dxf_file("./dxf-examples/gb3.dxf")

        # 缩放到适合视图的大小
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def load_dxf_file(self, file_name):
        # 加载DXF文件
        doc = ezdxf.readfile(file_name)

        # 获取所有实体
        entities = doc.modelspace().query("LINE CIRCLE ARC LWPOLYLINE POLYLINE")

        # 遍历所有实体
        for entity in entities:
            # 获取实体类型
            entity_type = entity.dxftype()

            # 如果是线条
            if entity_type == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                self.draw_line(start, end)

            # 如果是圆
            elif entity_type == "CIRCLE":
                center = entity.dxf.center
                radius = entity.dxf.radius
                self.draw_circle(center, radius)

            # 如果是圆弧
            elif entity_type == "ARC":
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                self.draw_arc(center, radius, start_angle, end_angle)

            # 如果是多段线
            elif entity_type == "LWPOLYLINE":
                vertices = entity.get_points("xy")
                self.draw_polyline(vertices)

            # 如果是多边形
            elif entity_type == "POLYLINE":
                if entity.is_closed:
                    vertices = entity.get_points("xy")
                    self.draw_polygon(vertices)

    def draw_line(self, start, end):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制线条
        self.scene.addLine(start[0], -start[1], end[0], -end[1], pen)

    def draw_circle(self, center, radius):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制圆
        self.scene.addEllipse(center[0]-radius, -center[1]-radius, radius*2, radius*2, pen)

    def draw_arc(self, center, radius, start_angle, end_angle):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制圆弧
        self.scene.addEllipse(center[0]-radius, -center[1]-radius, radius*2, radius*2, start_angle/16, (end_angle-start_angle)/16, pen)

    def draw_text(self, pos, text):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制文本
        self.scene.addText(text, self.font()).setPos(pos[0], -pos[1])

    def draw_polyline(self, vertices):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制多段线
        path = QPainterPath()
        path.moveTo(vertices[0][0], -vertices[0][1])
        for vertex in vertices[1:]:
            path.lineTo(vertex[0], -vertex[1])
        self.scene.addPath(path, pen)

    def draw_polygon(self, vertices):
        # 创建一个画笔
        pen = QPen(Qt.black, 1)

        # 在场景中绘制多边形
        path = QPainterPath()
        path.moveTo(vertices[0][0], -vertices[0][1])
        for vertex in vertices[1:]:
            path.lineTo(vertex[0], -vertex[1])
        path.closeSubpath()
        self.scene.addPath(path, pen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DXFViewer()
    window.show()
    sys.exit(app.exec_())
