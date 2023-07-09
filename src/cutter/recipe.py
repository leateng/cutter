from typing import Optional

import qtpy

import ezdxf
from ezdxf.lldxf.const import DXFStructureError
from qtpy import QtCore
from qtpy.QtGui import QIcon
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QComboBox
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QFormLayout
from qtpy.QtWidgets import QGroupBox
from qtpy.QtWidgets import QHBoxLayout
from qtpy.QtWidgets import QLabel
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QListView
from qtpy.QtWidgets import QPushButton
from qtpy.QtWidgets import QSpinBox
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout
from qtpy.QtWidgets import QWidget, QFileDialog, QMessageBox
from cutter.consts import SUPPORTED_ENTITY_TYPES
from cutter.cad_widget import CADGraphicsView, DxfEntityScence


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
        self.search_edit = QLineEdit(self)
        self.recipe_list = QListView(self)
        self.tool_radius = QSpinBox()
        self.cutter_offset = QSpinBox()
        self.rotation_speed = QSpinBox()
        self.load_dxf_button = QPushButton(QIcon(":/images/add.png"), "")
        self.load_dxf_button.clicked.connect(self._select_doc)

        # left layout
        left_layout = QVBoxLayout(self)
        search_layout = QHBoxLayout(self)
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
        recipe_info_layout.addRow(QLabel("配方名"), self.tool_radius)
        recipe_info_layout.addRow(QLabel("文件名"), self.cutter_offset)
        recipe_info_layout.addRow(QLabel("創建人"), self.rotation_speed)
        recipe_info_layout.addRow(QLabel("創建時間"), self.rotation_speed)
        recipe_info_layout_group = QGroupBox("配方信息")
        recipe_info_layout_group.setLayout(recipe_info_layout)

        # button
        self.add_button = QPushButton("保存")
        self.del_button = QPushButton("删除")
        self.add_button.clicked.connect(self._new_recipe)
        self.del_button.clicked.connect(self._delete_recipe)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.del_button)

        # right layout
        right_layout = QVBoxLayout(self)
        right_layout.addWidget(self.view)
        right_layout.addWidget(machine_param_group)
        right_layout.addLayout(button_layout)

        self._layout.addLayout(left_layout)
        self._layout.addLayout(right_layout)
        self._layout.setStretch(0, 1)
        self._layout.setStretch(1, 2)

    def _new_recipe(self):
        dlg = EditRecipeDialg(self)
        dlg.show()

    def _delete_recipe(self):
        pass

    def _edit_recipe(self):
        dlg = EditRecipeDialg(self)
        dlg.show()

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

                self.set_document(doc, auditor, True)
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


class EditRecipeDialg(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, recipe=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("配方")
        self.setWindowIcon(QIcon(QPixmap(":/images/folder.png")))
