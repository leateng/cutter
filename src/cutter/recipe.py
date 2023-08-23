from datetime import datetime
from pathlib import Path
from typing import Optional
import shutil

# from IPython import embed
from PySide2.QtCore import QItemSelectionModel

from ezdxf import recover
from ezdxf.lldxf.const import DXFError
from qtpy import QtCore
from qtpy.QtGui import QIcon, QImage, QPixmap
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
from cutter.database import (
    create_recipe,
    DXF_PATH,
    create_user,
    delete_recipe,
    get_recipes,
    update_recipe,
)
from cutter.models import Recipe


class RecipeCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["", "recipe 1", "recipe 2", "recipe 3"])
        self.setCurrentIndex(0)


class RecipeListModel(QtCore.QAbstractListModel):
    def __init__(self, recipes=None):
        super().__init__()
        self.recipes = recipes or []
        self.icon = QImage(":/images/dxf.png").scaledToHeight(18)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            recipe = self.recipes[index.row()]
            return recipe._name

        if role == QtCore.Qt.DecorationRole:
            return self.icon

    def rowCount(self, index) -> int:
        return len(self.recipes)

    def getIndexById(self, recipe_id: int) -> Optional[QtCore.QModelIndex]:
        for idx, e in enumerate(self.recipes):
            if e._id == recipe_id:
                return self.index(idx, 0)


class RecipeListView(QListView):
    def __init__(self) -> None:
        super().__init__()


class RecipeDialg(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_recipe: Optional[Recipe] = None
        self.recipe_view = RecipeListView()
        self.recipes_data = get_recipes()
        self.recipes_model = RecipeListModel(self.recipes_data)
        self.recipe_view.setModel(self.recipes_model)
        self.recipe_view.selectionModel().selectionChanged.connect(
            self.recipe_selection_changed
        )

        self.setWindowTitle("配方管理")
        self.setWindowIcon(QIcon(QPixmap(":/images/folder.png")))

        # dxf view
        self.is_new = False
        self.origin_path = None
        self.view = CADGraphicsView()
        self.scene = DxfEntityScence([])

        self._layout = QHBoxLayout(self)
        self.search_edit = QLineEdit()
        self.tool_radius = QSpinBox()
        self.cutter_offset = QSpinBox()
        self.cutter_deepth = QSpinBox()
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
        left_layout.addWidget(self.recipe_view)

        # machine info
        machine_param_layout = QFormLayout()
        machine_param_layout.addRow(QLabel("刀具半径(mm)"), self.tool_radius)
        machine_param_layout.addRow(QLabel("偏移量(mm)"), self.cutter_offset)
        machine_param_layout.addRow(QLabel("切割深度(mm)"), self.cutter_deepth)
        machine_param_layout.addRow(QLabel("转速(rpm)"), self.rotation_speed)
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
        self.add_button.setEnabled(False)
        self.add_button.setIcon(
            QApplication.style().standardIcon(QStyle.SP_DialogOkButton)
        )
        self.add_button.clicked.connect(self.saveRecipe)

        self.del_button = QPushButton("删除")
        self.del_button.setEnabled(False)
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
        if self.current_recipe is None:
            return

        recipe = self.current_recipe
        recipe._name = self.recipe_name.text()
        recipe._file_name = self.origin_filename.text()
        recipe._tool_radius = self.tool_radius.value()
        recipe._cutter_offset = self.cutter_offset.value()
        recipe._cutter_deepth = self.cutter_deepth.value()
        recipe._rotation_speed = self.rotation_speed.value()
        recipe._updated_by = g.CURRENT_USER._id if g.CURRENT_USER is not None else None
        recipe._updated_at = datetime.now()

        if recipe._id is not None:
            status, recipe_id = update_recipe(recipe)
        else:
            recipe._created_by = (
                g.CURRENT_USER._id if g.CURRENT_USER is not None else None
            )
            recipe._created_at = datetime.now()
            status, recipe_id = create_recipe(recipe)
            if status is True and recipe_id is not None:
                self._save_recipe_dxf(recipe_id)
                self.refresh_recipe_list()

        if status == False:
            QMessageBox.critical(self, "Error", "添加Recipe失败！")
            return

    def _delete_recipe(self):
        if self.current_recipe is not None:
            if self.current_recipe._id is not None:
                delete_recipe(self.current_recipe._id)
                self.current_recipe = None
                self.refresh_recipe_list()
                self.sync_recipe_ui()

    def refresh_recipe_list(self):
        self.recipes_model.recipes = get_recipes()
        self.recipes_model.layoutChanged.emit()

        if self.current_recipe is None:
            self.recipe_view.clearSelection()
            self.del_button.setEnabled(False)
            self.add_button.setEnabled(False)
        else:
            if self.current_recipe._id is not None:
                index = self.recipes_model.getIndexById(self.current_recipe._id)
                if index is not None:
                    self.recipe_view.setCurrentIndex(index)

    def _select_doc(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select CAD Document",
            filter="CAD Documents (*.dxf *.DXF)",
        )
        self.load_dxf_view(path)
        self.origin_path = path
        self.current_recipe = Recipe()
        pypath = Path(path)
        self.recipe_name.setText(pypath.stem)
        self.origin_filename.setText(pypath.name)
        self.created_at.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if g.CURRENT_USER is not None and g.CURRENT_USER._name is not None:
            self.created_by.setText(g.CURRENT_USER._name)
        self.add_button.setEnabled(True)

    def load_dxf_view(self, path):
        if path:
            try:
                doc, auditor = recover.readfile(path)
            except IOError:
                QMessageBox.critical(
                    self, "Loading Error", "Not a DXF file or a generic I/O error."
                )
                self.origin_path = None
                return
            except DXFError:
                QMessageBox.critical(
                    self, "Loading Error", "Invalid or corrupted DXF file."
                )
                self.origin_path = None
                return
            self.set_document(doc, auditor, True)

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

    def _save_recipe_dxf(self, recipe_id: int):
        dst = DXF_PATH / f"{recipe_id}.dxf"
        if self.origin_path is not None:
            shutil.copy(self.origin_path, str(dst))

    def recipe_selection_changed(self, selected, deselected):
        print("select changed")
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            recipe = self.recipes_model.recipes[index.row()]
            self.current_recipe = recipe
            self.load_recipe()

    def sync_recipe_ui(self):
        recipe = self.current_recipe
        if recipe is None:
            self.tool_radius.setValue(0)
            self.cutter_offset.setValue(0)
            self.cutter_deepth.setValue(0)
            self.rotation_speed.setValue(0)
            self.recipe_name.setText("")
            self.origin_filename.setText("")
            self.created_by.setText("")
            self.created_at.setText("")
            self.scene = DxfEntityScence([])
            self.view.setScene(self.scene)
        else:
            self.tool_radius.setValue(recipe._tool_radius)
            self.cutter_offset.setValue(recipe._cutter_offset)
            self.cutter_deepth.setValue(recipe._cutter_deepth)
            self.rotation_speed.setValue(recipe._rotation_speed)
            self.recipe_name.setText(recipe._name)
            self.origin_filename.setText(recipe._file_name)
            self.created_by
            self.created_at.setText(recipe._created_at)
            dxf_path = DXF_PATH / f"{recipe_id}.dxf"
            self.load_dxf_view(dxf_path)

    def load_recipe(self):
        recipe = self.current_recipe
        if recipe:
            self.del_button.setEnabled(True)
            self.add_button.setEnabled(True)
            self.tool_radius.setValue(recipe._tool_radius)
            self.cutter_offset.setValue(recipe._cutter_offset)
            self.cutter_deepth.setValue(recipe._cutter_deepth)
            self.rotation_speed.setValue(recipe._rotation_speed)
            self.recipe_name.setText(recipe._name)
            self.origin_filename.setText(recipe._file_name)
            self.created_by
            self.created_at.setText(recipe._created_at)
