from typing import Optional

import qtpy
from cutter.cad_widget import CADGraphicsView
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
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QWidget


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
        self._layout = QHBoxLayout(self)

        self.search_edit = QLineEdit(self)
        self.search_edit.setFixedWidth(400)
        self.recipe_list = QListView(self)
        self.recipe_list.setFixedWidth(400)
        self.dxf_view = CADGraphicsView()
        self.add_button = QPushButton("Add")
        self.tool_radius = QSpinBox()
        self.cutter_offset = QSpinBox()
        self.rotation_speed = QSpinBox()

        left_layout = QVBoxLayout(self)
        left_layout.addWidget(self.search_edit)
        left_layout.addWidget(self.recipe_list)

        machine_param_layout = QFormLayout()
        machine_param_layout.addRow(QLabel("刀具半径"), self.tool_radius)
        machine_param_layout.addRow(QLabel("偏移量"), self.cutter_offset)
        machine_param_layout.addRow(QLabel("转速"), self.rotation_speed)
        machine_param_group = QGroupBox("参数")
        machine_param_group.setLayout(machine_param_layout)

        right_layout = QVBoxLayout(self)
        right_layout.addWidget(self.dxf_view)
        right_layout.addWidget(machine_param_group)

        self._layout.addLayout(left_layout)
        self._layout.addLayout(right_layout)


class EditRecipeDialg(QDialog):
    def __init__(self, parent: Optional[QWidget] = None, recipe=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("配方")
        self.setWindowIcon(QIcon(QPixmap(":/images/folder.png")))
