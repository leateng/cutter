# import sys
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QPainter, QPen
# from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
# import ezdxf
# from qtpy.QtGui import QPainterPath


# class DXFViewer(QGraphicsView):
#     def __init__(self):
#         super().__init__()

#         # 创建一个场景
#         self.scene = QGraphicsScene()
#         self.setScene(self.scene)

#         # 加载DXF文件
#         self.load_dxf_file("./dxf-examples/gb3.dxf")

#         # 缩放到适合视图的大小
#         self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

#     def load_dxf_file(self, file_name):
#         # 加载DXF文件
#         doc = ezdxf.readfile(file_name)

#         # 获取所有实体
#         entities = doc.modelspace().query("LINE CIRCLE ARC LWPOLYLINE POLYLINE")

#         # 遍历所有实体
#         for entity in entities:
#             # 获取实体类型
#             entity_type = entity.dxftype()

#             # 如果是线条
#             if entity_type == "LINE":
#                 start = entity.dxf.start
#                 end = entity.dxf.end
#                 self.draw_line(start, end)

#             # 如果是圆
#             elif entity_type == "CIRCLE":
#                 center = entity.dxf.center
#                 radius = entity.dxf.radius
#                 self.draw_circle(center, radius)

#             # 如果是圆弧
#             elif entity_type == "ARC":
#                 center = entity.dxf.center
#                 radius = entity.dxf.radius
#                 start_angle = entity.dxf.start_angle
#                 end_angle = entity.dxf.end_angle
#                 self.draw_arc(center, radius, start_angle, end_angle)

#             # 如果是多段线
#             elif entity_type == "LWPOLYLINE":
#                 vertices = entity.get_points("xy")
#                 self.draw_polyline(vertices)

#             # 如果是多边形
#             elif entity_type == "POLYLINE":
#                 if entity.is_closed:
#                     vertices = entity.get_points("xy")
#                     self.draw_polygon(vertices)

#     def draw_line(self, start, end):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制线条
#         self.scene.addLine(start[0], -start[1], end[0], -end[1], pen)

#     def draw_circle(self, center, radius):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制圆
#         self.scene.addEllipse(center[0]-radius, -center[1]-radius, radius*2, radius*2, pen)

#     def draw_arc(self, center, radius, start_angle, end_angle):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制圆弧
#         self.scene.addEllipse(center[0]-radius, -center[1]-radius, radius*2, radius*2, start_angle/16, (end_angle-start_angle)/16, pen)

#     def draw_text(self, pos, text):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制文本
#         self.scene.addText(text, self.font()).setPos(pos[0], -pos[1])

#     def draw_polyline(self, vertices):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制多段线
#         path = QPainterPath()
#         path.moveTo(vertices[0][0], -vertices[0][1])
#         for vertex in vertices[1:]:
#             path.lineTo(vertex[0], -vertex[1])
#         self.scene.addPath(path, pen)

#     def draw_polygon(self, vertices):
#         # 创建一个画笔
#         pen = QPen(Qt.black, 1)

#         # 在场景中绘制多边形
#         path = QPainterPath()
#         path.moveTo(vertices[0][0], -vertices[0][1])
#         for vertex in vertices[1:]:
#             path.lineTo(vertex[0], -vertex[1])
#         path.closeSubpath()
#         self.scene.addPath(path, pen)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DXFViewer()
#     window.show()
#     sys.exit(app.exec_())

# =======================================================================================
import sys
from PySide2.QtCore import Qt, QRectF, QSize
from PySide2.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
)
from PySide2.QtGui import QPainter
import ezdxf
from qtpy.QtGui import QImage


class DXFViewer(QGraphicsView):
    def __init__(self, dxf_file, parent=None):
        super(DXFViewer, self).__init__(parent)

        self.setScene(QGraphicsScene(self))
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setOptimizationFlags(QGraphicsView.DontSavePainterState)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing, True)

        # origin = QGraphicsSimpleTextItem("O")
        # origin.setPos(0, 0)
        # origin.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        # self.scene().addItem(origin)

        self.load_dxf(dxf_file)

    def load_dxf(self, dxf_file):
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()

        for entity in msp:
            if entity.dxftype() in [
                "LINE",
                "ARC",
                "CIRCLE",
                "POLYLINE",
                "LWPOLYLINE",
                "INSERT",
            ]:
                self.draw_entity(entity)

        self.setSceneRect(self.scene().itemsBoundingRect())

    def draw_entity(self, entity):
        item = self.dxf_entity_to_qgraphicsitem(entity)
        self.scene().addItem(item)

    def dxf_entity_to_qgraphicsitem(self, entity):
        if entity.dxftype() == "LINE":
            start_point = entity.dxf.start
            end_point = entity.dxf.end
            line = QGraphicsLineItem(
                start_point[0], -start_point[1], end_point[0], -end_point[1]
            )
            return line
        elif entity.dxftype() == "ARC":
            center = entity.dxf.center
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            arc = QGraphicsEllipseItem(
                center[0] - radius, -(center[1] - radius), radius * 2, radius * 2
            )
            arc.setStartAngle(-start_angle * 16)
            arc.setSpanAngle(-(end_angle - start_angle) * 16)
            return arc
        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            circle = QGraphicsEllipseItem(
                center[0] - radius, -(center[1] - radius), radius * 2, radius * 2
            )
            return circle
        elif entity.dxftype() == "POLYLINE":
            polyline = QGraphicsPolygonItem()
            points = []
            for vertex in entity.vertices():
                points.append((vertex.dxf.location[0], vertex.dxf.location[1]))
            polyline.setPolygon(QPolygonF(points))
            return polyline
        elif entity.dxftype() == "LWPOLYLINE":
            polyline = QGraphicsPathItem()
            path = QPainterPath()
            for i, vertex in enumerate(entity.vertices()):
                if i == 0:
                    path.moveTo(vertex.dxf.location[0], vertex.dxf.location[1])
                else:
                    path.lineTo(vertex.dxf.location[0], vertex.dxf.location[1])
            if entity.is_closed:
                path.closeSubpath()
            polyline.setPath(path)
            return polyline
        else:
            return None

    def save_image(self, name):
        self.scene().clearSelection()
        # self.scene().setSceneRect(self.scene().itemsBoundingRect())
        # image = QImage(self.scene().sceneRect().size().toSize(), QImage.Format_ARGB32)
        self.scene().setSceneRect(QRectF(0, 0, 100, 100))
        image = QImage(QSize(100, 100), QImage.Format_ARGB32)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        self.scene().render(painter)
        image.save(f"D:\\{name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    dxf_viewer = DXFViewer("dxf-examples/gb.dxf")
    dxf_viewer.save_image("dxf.png")
    main_layout.addWidget(dxf_viewer)

    main_win.setCentralWidget(main_widget)
    main_win.show()
    sys.exit(app.exec_())
