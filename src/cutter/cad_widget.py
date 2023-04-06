import sys
import math
import ezdxf
from PySide6.QtWidgets import QFileDialog, QFrame, QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QGraphicsItem, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath, QPainter, QTransform, QWheelEvent, QBrush, QPolygonF, QAction
from PySide6.QtCore import Qt, QRectF, QPointF
from IPython import embed
from ezdxf.lldxf.const import LWPOLYLINE_CLOSED

def _get_x_scale(t: QTransform) -> float:
    return math.sqrt(t.m11() * t.m11() + t.m21() * t.m21())

class CADGraphicsView(QGraphicsView):
    def __init__(
        self,
        *,
        view_buffer: float = 0.2,
        zoom_per_scroll_notch: float = 0.2,
        loading_overlay: bool = True,
    ):
        super().__init__()
        self._zoom = 1.0
        self._default_zoom = 1.0
        self._zoom_limits = (0.5, 100)
        self._zoom_per_scroll_notch = zoom_per_scroll_notch
        self._view_buffer = view_buffer
        self._loading_overlay = loading_overlay
        self._is_loading = False

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setRenderHints( QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.scale(1, -1)  # so that +y is up

    def clear(self):
        pass

    def begin_loading(self):
        self._is_loading = True
        self.scene().invalidate(QRectF(), QGraphicsScene.SceneLayer.AllLayers)
        QApplication.processEvents()

    def end_loading(self, new_scene: QGraphicsScene):
        self.setScene(new_scene)
        self._is_loading = False
        self.buffer_scene_rect()
        self.scene().invalidate(QRectF(), QGraphicsScene.SceneLayer.AllLayers)

    def buffer_scene_rect(self):
        scene = self.scene()
        r = scene.sceneRect()
        bx, by = (
            r.width() * self._view_buffer / 2,
            r.height() * self._view_buffer / 2,
        )
        scene.setSceneRect(r.adjusted(-bx, -by, bx, by))

    def fit_to_scene(self):
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._default_zoom = _get_x_scale(self.transform())
        self._zoom = 1

    def _get_zoom_amount(self) -> float:
        return _get_x_scale(self.transform()) / self._default_zoom

    def wheelEvent(self, event: QWheelEvent) -> None:
        # dividing by 120 gets number of notches on a typical scroll wheel.
        # See QWheelEvent documentation
        delta_notches = event.angleDelta().y() / 120
        direction = math.copysign(1, delta_notches)
        factor = (1.0 + self._zoom_per_scroll_notch * direction) ** abs(delta_notches)
        resulting_zoom = self._zoom * factor
        if resulting_zoom < self._zoom_limits[0]:
            factor = self._zoom_limits[0] / self._zoom
        elif resulting_zoom > self._zoom_limits[1]:
            factor = self._zoom_limits[1] / self._zoom
        self.scale(factor, factor)
        self._zoom *= factor

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        if self._is_loading and self._loading_overlay:
            painter.save()
            painter.fillRect(rect, QColor("#aa000000"))
            painter.setWorldMatrixEnabled(False)
            r = self.viewport().rect()
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(r.center(), "Loading...")
            painter.restore()


class DxfEntityScence(QGraphicsScene):
    def __init__(self, entities): 
        super().__init__()
        self.setBackgroundBrush(QColor(33, 40, 48))
        self.entities = entities
        self.pen = QPen(Qt.GlobalColor.white)
        self.pen.setCosmetic(True)

        self.draw_coordinate_axis(20)
        self.draw_entities()

    def draw_entities(self):
        for entity in self.entities:
            item = self.create_qgraphicsitem_from_entity(entity)
            if item:
                self.addItem(item)

    def create_qgraphicsitem_from_entity(self, entity):
        item = None
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            item = QGraphicsLineItem(start.x, start.y, end.x, end.y)
        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            item = QGraphicsEllipseItem(center.x - radius, center.y - radius, radius * 2, radius * 2)
        elif entity.dxftype() == 'ELLIPSE':
            center = entity.dxf.center
            major_axis = entity.dxf.major_axis
            minor_axis = entity.minor_axis
            item = QGraphicsEllipseItem(center.x - major_axis.x , center.y - minor_axis.y, major_axis.x*2, minor_axis.y*2)
        elif entity.dxftype() == 'ARC':
            center = entity.dxf.center
            radius = entity.dxf.radius
            item = QGraphicsEllipseItem(center.x - radius, center.y - radius, radius * 2, radius * 2)
            start_angle = -entity.dxf.end_angle
            end_angle = -entity.dxf.start_angle
            if end_angle < start_angle:
                end_angle = (end_angle+360)
            item.setStartAngle(start_angle*16)
            item.setSpanAngle(end_angle*16 - start_angle*16)
        elif entity.dxftype() == 'LWPOLYLINE':
            path = QPainterPath()
            # embed()
            first_vertex = entity[0]
            path.moveTo(first_vertex[0], first_vertex[1])

            for vertex in entity[1:]:
                path.lineTo(vertex[0], vertex[1])

            item = QGraphicsPathItem(path)
        else:
            print("skip entity type:", entity.dxftype())

        if item:
            item.setPen(self.pen)
        return item

    def draw_coordinate_axis(self, axis_len: float = 10) -> None:
        x_color = QColor(255, 0, 0, 100) # Qt.GlobalColor.green
        y_color = QColor(0, 255, 0, 100) # Qt.GlobalColor.red

        brush = QBrush(x_color)
        pen = QPen(x_color)
        pen.setCosmetic(True)
    
        right_arrow = QPolygonF()
        right_arrow.append(QPointF(0, 1))
        right_arrow.append(QPointF(2, 0))
        right_arrow.append(QPointF(0, -1))
        right_arrow.translate(axis_len, 0)

        up_arrow = QPolygonF()
        up_arrow.append(QPointF(1, 0))
        up_arrow.append(QPointF(0, 2))
        up_arrow.append(QPointF(-1, 0))
        up_arrow.translate(0, axis_len)

        self.addLine(0, 0, axis_len, 0, pen)
        self.addPolygon(right_arrow, pen, brush)

        pen.setColor(y_color)
        brush.setColor(y_color)
        self.addLine(0, 0, 0, axis_len, pen)
        self.addPolygon(up_arrow, pen, brush)

