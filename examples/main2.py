from __future__ import annotations
from typing import Iterable, Sequence
import math
import os
import sys
import time

from PySide6 import QtWidgets as qw, QtCore as qc, QtGui as qg
from PySide6 import QtGui
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QTableView,
    QTreeView,
    QListView,
)
from PySide6.QtCore import (
    QAbstractTableModel,
    QStringListModel,
    QFileSystemWatcher,
    QModelIndex,
    QPointF,
    QSettings,
    QSize,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QPainterPath,
    QPen,
    QPolygon,
    QPolygonF,
    QStandardItem,
    QStandardItemModel,
)

import ezdxf
import ezdxf.bbox
from ezdxf import recover
from ezdxf.addons import odafc
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.config import Configuration
from ezdxf.addons.drawing.qtviewer import CADGraphicsViewWithOverlay

from ezdxf.addons.drawing.properties import (
    is_dark_color,
    set_layers_state,
    LayerProperties,
)
from ezdxf.addons.drawing.pyqt import (
    _get_x_scale,
    PyQtBackend,
    CorrespondingDXFEntity,
    CorrespondingDXFParentStack,
)
from ezdxf.audit import Auditor
from ezdxf.document import Drawing
from ezdxf.entities import DXFGraphic
from ezdxf.lldxf.const import DXFStructureError


class CadViewer(qw.QMainWindow):
    def __init__(self, config: Configuration = Configuration.defaults()):
        super().__init__()
        self._config = config
        # Avoid using Optional[...], otherwise mypy requires None checks
        # everywhere!
        self.doc: Drawing = None  # type: ignore
        self._render_context: RenderContext = None  # type: ignore
        self._visible_layers: set[str] = set()
        self._current_layout: str = "Model"
        self._reset_backend()
        self._bbox_cache = ezdxf.bbox.Cache()

        self.view = CADGraphicsViewWithOverlay()
        self.view.setBackgroundBrush(QColor(25, 35, 48))
        self.scence = qw.QGraphicsScene()
        self.view.setScene(self.scence)
        self.view.scale(1, -1)  # so that +y is up
        self.view.element_selected.connect(self._on_element_selected)
        self.view.mouse_moved.connect(self._on_mouse_moved)

        menu = self.menuBar()
        select_doc_action = QAction("Select Document", self)
        select_doc_action.triggered.connect(self._select_doc)
        menu.addAction(select_doc_action)
        self.select_layout_menu = menu.addMenu("Select Layout")

        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
        menu.addAction(toggle_sidebar_action)

        self.sidebar = qw.QSplitter(qc.Qt.Vertical)
        self.layers = qw.QListWidget()
        self.layers.setStyleSheet(
            "QListWidget {font-size: 12pt;} "
            "QCheckBox {font-size: 12pt; padding-left: 5px;}"
        )
        self.sidebar.addWidget(self.layers)
        info_container = qw.QWidget()
        info_layout = qw.QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_info = qw.QPlainTextEdit()
        self.selected_info.setReadOnly(True)
        info_layout.addWidget(self.selected_info)
        self.mouse_pos = qw.QLabel()
        info_layout.addWidget(self.mouse_pos)
        info_container.setLayout(info_layout)
        self.sidebar.addWidget(info_container)

        container = qw.QSplitter()
        self.setCentralWidget(container)
        container.addWidget(self.view)
        container.addWidget(self.sidebar)
        container.setCollapsible(0, False)
        container.setCollapsible(1, True)
        w = container.width()
        container.setSizes([int(3 * w / 4), int(w / 4)])

        self.setWindowTitle("CAD Viewer")
        self.resize(1600, 900)
        self.show()

    def _reset_backend(self):
        # clear caches
        self._backend = PyQtBackend(use_text_cache=True)

    def _select_doc(self):
        path, _ = qw.QFileDialog.getOpenFileName(
            self,
            caption="Select CAD Document",
            filter="CAD Documents (*.dxf *.DXF *.dwg *.DWG)",
        )
        if path:
            try:
                if os.path.splitext(path)[1].lower() == ".dwg":
                    doc = odafc.readfile(path)
                    auditor = doc.audit()
                else:
                    try:
                        doc = ezdxf.readfile(path)
                    except ezdxf.DXFError:
                        doc, auditor = recover.readfile(path)
                    else:
                        auditor = doc.audit()

                # force use songti
                for st in doc.styles:
                    st.set_dxf_attrib("font", "simsun.ttc")
                    st.set_dxf_attrib("bigfont", "simsun.ttc")

                self.set_document(doc, auditor)
            except IOError as e:
                qw.QMessageBox.critical(self, "Loading Error", str(e))
            except DXFStructureError as e:
                qw.QMessageBox.critical(
                    self,
                    "DXF Structure Error",
                    f'Invalid DXF file "{path}": {str(e)}',
                )

    def set_document(
        self,
        document: Drawing,
        auditor: Auditor,
        *,
        layout: str = "Model",
    ):
        error_count = len(auditor.errors)
        if error_count > 0:
            ret = qw.QMessageBox.question(
                self,
                "Found DXF Errors",
                f'Found {error_count} errors in file "{document.filename}"\n'
                f"Load file anyway? ",
            )
            if ret == qw.QMessageBox.No:
                auditor.print_error_report(auditor.errors)
                return

        self.doc = document
        # initialize bounding box cache for faste paperspace drawing
        self._bbox_cache = ezdxf.bbox.Cache()
        self._render_context = self._make_render_context(document)
        self._reset_backend()
        self._visible_layers = set()
        self._current_layout = None
        self._populate_layouts()
        self._populate_layer_list()
        self.draw_layout(layout)

        self.setWindowTitle("CAD Viewer - " + str(document.filename))

    def _make_render_context(self, doc) -> RenderContext:
        def update_layers_state(layers: Sequence[LayerProperties]):
            if self._visible_layers:
                set_layers_state(layers, self._visible_layers, state=True)

        render_context = RenderContext(doc)
        render_context.set_layer_properties_override(update_layers_state)
        return render_context

    def _populate_layer_list(self):
        self.layers.blockSignals(True)
        self.layers.clear()
        for layer in self._render_context.layers.values():
            name = layer.layer
            item = qw.QListWidgetItem()
            self.layers.addItem(item)
            checkbox = qw.QCheckBox(name)
            checkbox.setCheckState(qc.Qt.Checked if layer.is_visible else qc.Qt.Unchecked)
            checkbox.stateChanged.connect(self._layers_updated)
            text_color = ("#FFFFFF" if is_dark_color(layer.color, 0.4) else "#000000")
            checkbox.setStyleSheet(f"color: {text_color}; background-color: {layer.color}")
            self.layers.setItemWidget(item, checkbox)
        self.layers.blockSignals(False)

    def _populate_layouts(self):
        def draw_layout(name: str):
            def run():
                self.draw_layout(name, reset_view=True)

            return run

        self.select_layout_menu.clear()
        for layout_name in self.doc.layout_names_in_taborder():
            action = QAction(layout_name, self)
            action.triggered.connect(draw_layout(layout_name))
            self.select_layout_menu.addAction(action)

    def draw_layout(
        self,
        layout_name: str,
        reset_view: bool = True,
    ):
        print(f"drawing {layout_name}")
        self._current_layout = layout_name
        self.view.begin_loading()
        new_scene = qw.QGraphicsScene()
        self._draw_coordinate_axis(new_scene, 20)
        self._backend.set_scene(new_scene)
        layout = self.doc.layout(layout_name)
        self._update_render_context(layout)
        try:
            start = time.perf_counter()
            # self.create_frontend().draw_layout(layout)
            ents = layout.query("CIRCLE LINE ARC")
            print(f"ents={len(ents)}")
            self.create_frontend().draw_entities(ents)

            duration = time.perf_counter() - start
            print(f"draw layout {layout_name} took {duration:.4f} seconds")
        except DXFStructureError as e:
            qw.QMessageBox.critical(
                self,
                "DXF Structure Error",
                f'Abort rendering of layout "{layout_name}": {str(e)}',
            )
        finally:
            self._backend.finalize()
        self.view.end_loading(new_scene)
        self.view.buffer_scene_rect()
        if reset_view:
            self.view.fit_to_scene()

    def create_frontend(self):
        return Frontend(
            ctx=self._render_context,
            out=self._backend,
            config=self._config,
            bbox_cache=self._bbox_cache
        )

    def _update_render_context(self, layout):
        assert self._render_context is not None
        self._render_context.set_current_layout(layout)

    def resizeEvent(self, event: qg.QResizeEvent) -> None:
        self.view.fit_to_scene()

    def _layer_checkboxes(self) -> Iterable[tuple[int, qw.QCheckBox]]:
        for i in range(self.layers.count()):
            item = self.layers.itemWidget(self.layers.item(i))
            yield i, item  # type: ignore

    def _draw_coordinate_axis(self, scene: qw.QGraphicsScene, axis_len: float = 10) -> None:
        x_color = Qt.GlobalColor.green
        y_color = Qt.GlobalColor.red

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

        scene.addLine(0, 0, axis_len, 0, pen)
        scene.addPolygon(right_arrow, pen, brush)

        pen.setColor(y_color)
        brush.setColor(y_color)
        scene.addLine(0, 0, 0, axis_len, pen)
        scene.addPolygon(up_arrow, pen, brush)

    @Slot(int)  # type: ignore
    def _layers_updated(self, item_state: qc.Qt.CheckState):
        shift_held = qw.QApplication.keyboardModifiers() & qc.Qt.ShiftModifier
        if shift_held:
            for i, item in self._layer_checkboxes():
                item.blockSignals(True)
                item.setCheckState(item_state)
                item.blockSignals(False)

        self._visible_layers = set()
        for i, layer in self._layer_checkboxes():
            if layer.checkState() == qc.Qt.Checked:
                self._visible_layers.add(layer.text())
        self.draw_layout(self._current_layout, reset_view=False)

    @Slot()
    def _toggle_sidebar(self):
        self.sidebar.setHidden(not self.sidebar.isHidden())

    @Slot(qc.QPointF)
    def _on_mouse_moved(self, mouse_pos: qc.QPointF):
        self.mouse_pos.setText(
            f"mouse position: {mouse_pos.x():.4f}, {mouse_pos.y():.4f}\n"
        )

    @Slot(object, int)
    def _on_element_selected(
        self, elements: list[qw.QGraphicsItem], index: int
    ):
        if not elements:
            text = "No element selected"
        else:
            text = (
                f"Selected: {index + 1} / {len(elements)}    (click to cycle)\n"
            )
            element = elements[index]
            dxf_entity = element.data(CorrespondingDXFEntity)
            if dxf_entity is None:
                text += "No data"
            else:
                text += (
                    f"Selected Entity: {dxf_entity}\n"
                    f"Layer: {dxf_entity.dxf.layer}\n\nDXF Attributes:\n"
                )
                text += _entity_attribs_string(dxf_entity)

                dxf_parent_stack = element.data(CorrespondingDXFParentStack)
                if dxf_parent_stack:
                    text += "\nParents:\n"
                    for entity in reversed(dxf_parent_stack):
                        text += f"- {entity}\n"
                        text += _entity_attribs_string(entity, indent="    ")

        self.selected_info.setPlainText(text)


def _entity_attribs_string(dxf_entity: DXFGraphic, indent: str = "") -> str:
    text = ""
    for key, value in dxf_entity.dxf.all_existing_dxf_attribs().items():
        text += f"{indent}- {key}: {value}\n"
    return text


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # setup drawing add-on configuration
    config = Configuration.defaults()
    config = config.with_changes(
        lineweight_scaling = 0 
    )

    window = CadViewer(config=config)
    window.show()

    sys.exit(app.exec())
