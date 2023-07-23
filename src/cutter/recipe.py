from datetime import datetime
from pathlib import Path
from typing import Optional

import ezdxf
import qtpy
from ezdxf.lldxf.const import DXFStructureError
from qtpy import QtCore
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)

import cutter.consts as g
from cutter.cad_widget import CADGraphicsView, DxfEntityScence
from cutter.consts import SUPPORTED_ENTITY_TYPES


class RecipeCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["", "recipe 1", "recipe 2", "recipe 3"])
        self.setCurrentIndex(0)


class RecipeDialg(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("配方管理")
        self.setWindowIcon(QIcon(QPixmap(":/images/folder.png")))

        # dxf view
        self.is_new = False
        self.origin_path = None
        self.view = CADGraphicsView()
        self.scene = DxfEntityScence([])

        self._layout = QHBoxLayout(self)
        self.search_edit = QLineEdit()
        self.recipe_list = QListView()
        self.tool_radius = QSpinBox()
        self.cutter_offset = QSpinBox()
        self.rotation_speed = QSpinBox()
        self.load_dxf_button = QPushButton(QIcon(":/images/add.png"), "")
        self.load_dxf_button.clicked.connect(self._select_doc)
        self.recipe_name = QLineEdit()
        self.origin_filename = QLabel()
        self.created_by = QLabel()
        self.created_at = QLabel()

        # left layout
        left_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.load_dxf_button)
        search_layout.addWidget(self.search_edit)
        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.recipe_list)

        # machine info
        machine_param_layout = QFormLayout()
        machine_param_layout.addRow(QLabel("刀具半径"), self.tool_radius)
        machine_param_layout.addRow(QLabel("偏移量"), self.cutter_offset)
        machine_param_layout.addRow(QLabel("转速"), self.rotation_speed)
        machine_param_group = QGroupBox("参数")
        machine_param_group.setLayout(machine_param_layout)

        # recipe info
        recipe_info_layout = QFormLayout()
        recipe_info_layout.addRow(QLabel("配方名"), self.recipe_name)
        recipe_info_layout.addRow(QLabel("文件名"), self.origin_filename)
        recipe_info_layout.addRow(QLabel("创建人"), self.created_by)
        recipe_info_layout.addRow(QLabel("创建时间"), self.created_at)
        recipe_info_layout_group = QGroupBox("配方信息")
        recipe_info_layout_group.setLayout(recipe_info_layout)

        # info layout
        info_layout = QHBoxLayout()
        info_layout.addWidget(recipe_info_layout_group)
        info_layout.addWidget(machine_param_group)
        info_layout.setStretch(0, 2)
        info_layout.setStretch(1, 1)

        # button
        self.add_button = QPushButton("保存")
        self.add_button.setIcon(
            QApplication.style().standardIcon(QStyle.SP_DialogOkButton)
        )
        self.add_button.clicked.connect(self.saveRecipe)
        self.del_button = QPushButton("删除")
        self.del_button.setIcon(
            QApplication.style().standardIcon(QStyle.SP_DialogCancelButton)
        )
        self.del_button.clicked.connect(self._delete_recipe)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.del_button)
        button_layout.addWidget(self.add_button)

        # right layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.view)
        right_layout.addLayout(info_layout)
        right_layout.addLayout(button_layout)

        self._layout.addLayout(left_layout)
        self._layout.addLayout(right_layout)
        self._layout.setStretch(0, 1)
        self._layout.setStretch(1, 2)

    def saveRecipe(self):
        recipe_name = self.recipe_name.text()
        origin_filename = self.origin_filename.text()
        created_by = g.CURRENT_USER._id if g.CURRENT_USER is not None else None
        created_at = datetime.now()
        tool_radius = self.tool_radius.value()
        cutter_offset = self.cutter_offset.value()
        rotation_speed = self.rotation_speed.value()

    def _delete_recipe(self):
        pass

    def _edit_recipe(self):
        pass

    def _select_doc(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select CAD Document",
            filter="CAD Documents (*.dxf *.DXF)",
        )
        if path:
            try:
                try:
                    self.origin_path = path
                    doc = ezdxf.readfile(path)
                except ezdxf.DXFError:
                    doc, auditor = recover.readfile(path)
                else:
                    auditor = doc.audit()

                pypath = Path(path)
                self.set_document(doc, auditor, True)
                self.recipe_name.setText(pypath.stem)
                self.origin_filename.setText(pypath.name)
                self.created_by.setText(g.CURRENT_USER._name)
                self.created_at.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except IOError as e:
                self.origin_path = None
                QMessageBox.critical(self, "Loading Error", str(e))
            except DXFStructureError as e:
                self.origin_path = None
                QMessageBox.critical(
                    self,
                    "DXF Structure Error",
                    f'Invalid DXF file "{path}": {str(e)}',
                )

    def set_document(self, doc, auditor, is_new):
        # is new recipe
        self.is_new = is_new

        mps = doc.modelspace()
        self.doc = doc
        self.dxf_entities = doc.modelspace().query(" ".join(SUPPORTED_ENTITY_TYPES))

        # draw entity view
        self.scene = DxfEntityScence(self.dxf_entities)
        self.view.setScene(self.scene)
        self.view.fit_to_scene()

        # # draw entity tree
        # # self.entity_tree = EntityTree(self.dxf_entities)
        # self.entity_tree.set_entities(self.dxf_entities)
