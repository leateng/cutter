import os
from typing import Optional

import ezdxf
import pyads
import qtawesome as qta
from ezdxf.lldxf.const import DXFStructureError
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QIcon, QKeySequence, QPixmap
from qtpy.QtWidgets import (
    QAction,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from cutter.about_dialog import AboutUsDialog
from cutter.axis_timer import axis_timer
from cutter.database import DXF_PATH
from cutter.error_info_widget import ErrorInfo
from cutter.error_report_timer import error_report_timer
from cutter.cad_widget import CADGraphicsView, DxfEntityScence
from cutter.consts import SUPPORTED_ENTITY_TYPES
from cutter.entity_tree import EntityTree
from cutter.gcode import GCode
from cutter.gcode_dialog import GCodeDialog
from cutter.joy import JoyDialog
from cutter.machine_info import MachineInfo
from cutter.models import Recipe
from cutter.plc import PLC_CONN, reset_machine
from cutter.recipe import RecipeCombo, RecipeDialg
from cutter.users import UsersDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dxf_entities = []
        self.machine_info = MachineInfo(self)
        axis_timer.addObserver(self.machine_info)
        self._init_toolbar()
        self._init_layout()
        self.setWindowIcon(QIcon(QPixmap(":/images/cutter.png")))
        # self._init_statusbar()
        self._regist_fullscreen()

    def _init_toolbar(self):
        self.toolbar = QToolBar("My main toolbar")
        self.toolbar.setIconSize(QSize(48, 48))
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        self._init_toolbar_actions()

        # set background image
        banner_image = QLabel()
        banner_image.setPixmap(QPixmap(":/images/hc.png"))
        banner_image.setScaledContents(True)  # 自动缩放图像以适应标签大小
        banner_image.setStyleSheet("background: transparent; padding-right: 5px;")
        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)

        # 添加标签和占位符到工具栏中
        self.toolbar.addWidget(spacer)
        self.toolbar.addWidget(banner_image)

    def _init_toolbar_actions(self):
        actions_config = [
            ["dxf.png", "打开文件", self._select_doc, "Ctrl+o"],
            ["start.png", "启动机器", self._start_machine, "F5"],
            ["folder.png", "配方管理", self._open_recipe_dialog, "Ctrl+m"],
            ["user1.png", "用户管理", self._open_users_management, "Ctrl+u"],
            ["game-controller.png", "JOG", self._open_joy, "Ctrl+j"],
            ["gcode.png", "生成GCODE", self._open_gcode_dialog, "Ctrl+g"],
            ["target.png", "回零", self._go_home, "ctrl+h"],
            ["reset.png", "复位", self._reset_machine, "ctrl+r"],
            ["info.png", "关于我们", self._open_about_us, "Ctrl+i"],
        ]

        for e in actions_config:
            action = QAction(QIcon(QPixmap(f":/images/{e[0]}")), e[1], self)
            action.triggered.connect(e[2])
            action.setShortcut(QKeySequence(e[3]))
            self.toolbar.addAction(action)

    def _init_layout(self):
        self.main_splitter = QSplitter()
        self.view = CADGraphicsView()
        self.scene = DxfEntityScence([])
        self.view.setScene(self.scene)
        self.setCentralWidget(self.main_splitter)
        self.recipe_combox = RecipeCombo()
        self.entity_tree = EntityTree()
        self.tool_radius = QDoubleSpinBox()
        self.cutter_offset = QDoubleSpinBox()
        self.rotation_speed = QSpinBox()
        self.cutter_deepth = QDoubleSpinBox()
        self.rotation_speed.setRange(0, 6000)

        # events
        self.recipe_combox.currentIndexChanged.connect(self.recipe_selection_changed)

        machine_param_layout = QFormLayout()
        machine_param_layout.addRow(QLabel("刀具半径(mm)"), self.tool_radius)
        machine_param_layout.addRow(QLabel("偏移量(mm)"), self.cutter_offset)
        machine_param_layout.addRow(QLabel("切割深度(mm)"), self.cutter_deepth)
        machine_param_layout.addRow(QLabel("转速(rpm)"), self.rotation_speed)
        machine_param_group = QGroupBox("参数")
        machine_param_group.setLayout(machine_param_layout)

        machine_info_layout = QVBoxLayout()
        machine_info_layout.addWidget(self.machine_info)
        machine_info_group = QGroupBox("机器信息")
        machine_info_group.setLayout(machine_info_layout)

        left_layout = QVBoxLayout()
        recipe_layout = QFormLayout()
        recipe_icon = QLabel("选择配方")
        recipe_icon.setPixmap(qta.icon("ei.th-list", color="#525960").pixmap(20, 20))
        recipe_layout.addRow(recipe_icon, self.recipe_combox)
        left_layout.addLayout(recipe_layout)
        left_layout.addWidget(self.entity_tree)
        left_layout.addWidget(machine_param_group)
        left_layout.addWidget(machine_info_group)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.view)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)

        # 设置左侧宽度
        sizes = [400, 1000]
        self.main_splitter.setSizes(sizes)

        # 使QSplitter右侧自适应大小
        self.main_splitter.setStretchFactor(1, 1)
        self.resize(sum(sizes), 900)
        self.view.fit_to_scene()

    def _select_doc(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select CAD Document",
            filter="CAD Documents (*.dxf *.DXF)",
        )
        self.load_dxf_file(path)

    def load_dxf_file(self, path):
        if path:
            try:
                try:
                    doc = ezdxf.readfile(path)
                except ezdxf.DXFError:
                    doc, auditor = recover.readfile(path)
                else:
                    auditor = doc.audit()

                self.set_document(doc, auditor)
            except IOError as e:
                QMessageBox.critical(self, "Loading Error", str(e))
            except DXFStructureError as e:
                QMessageBox.critical(
                    self,
                    "DXF Structure Error",
                    f'Invalid DXF file "{path}": {str(e)}',
                )
        else:
            self.set_empty_document()

    def set_document(self, doc, auditor):
        doc.modelspace()
        self.doc = doc
        self.dxf_entities = doc.modelspace().query(" ".join(SUPPORTED_ENTITY_TYPES))

        # draw entity view
        self.scene = DxfEntityScence(self.dxf_entities)
        self.view.setScene(self.scene)
        self.view.fit_to_scene()

        # draw entity tree
        # self.entity_tree = EntityTree(self.dxf_entities)
        self.entity_tree.set_entities(self.dxf_entities)

    def set_empty_document(self):
        self.doc = None
        self.dxf_entities = []

        # draw entity view
        self.scene = DxfEntityScence(self.dxf_entities)
        self.view.setScene(self.scene)

        # draw entity tree
        self.entity_tree.set_entities(self.dxf_entities)

    def _open_about_us(self):
        dlg = AboutUsDialog()
        dlg.exec()

    def _open_recipe_dialog(self):
        dlg = RecipeDialg(self)
        dlg.recipes_changed.connect(self.refresh_recipe_combo)
        dlg.resize(1200, 600)
        dlg.exec()

    def _open_users_management(self):
        dlg = UsersDialog()
        dlg.resize(1000, 620)
        dlg.exec()

    def _open_joy(self):
        dlg = JoyDialog(self)
        dlg.exec()

    # def _init_statusbar(self):
    #     self.error_info = ErrorInfo()
    #     self.statusBar = QStatusBar()
    #     self.statusBar.setStyleSheet("QStatusBar::item { border: none; }")
    #     self.statusBar.addWidget(self.error_info)
    #     self.setStatusBar(self.statusBar)
    #     self.error_info.update_error_info(False, None)
    #     error_report_timer.addObserver(self.error_info)
    #     error_report_timer.start()

    def _start_machine(self):
        if len(self.dxf_entities) == 0:
            QMessageBox.warning(self, "Warning", "没有可用的dxf实体!")
            return

        gcode = ""
        try:
            tool_radius = self.tool_radius.value()
            cutter_offset = self.cutter_offset.value()
            cutter_deepth = self.cutter_deepth.value()
            rotation_speed = self.rotation_speed.value()
            generator = GCode(
                self.dxf_entities,
                tool_radius,
                cutter_offset,
                rotation_speed,
                cutter_deepth,
            )
            gcode = generator.generate()
        except Exception as e:
            QMessageBox.warning(self, "Warning", e.args[0])
            # raise e
            return

        path = "c:\\TWinCAT\\Mc\\Nci\\cutter.nc"
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file = open(path, "w")

        file.write(gcode)
        file.close()

        if PLC_CONN.is_open:
            path = ""
            strGFileName = PLC_CONN.write_by_name(
                "GVL_HMI.strGFileName", "cutter.nc", pyads.PLCTYPE_STRING
            )
            bExecuteGCode = PLC_CONN.write_by_name(
                "GVL_HMI.bExecuteGCode", True, pyads.PLCTYPE_BOOL
            )
            current_status = PLC_CONN.read_by_name(
                "GVL_HMI.diCrtStatus", pyads.PLCTYPE_INT
            )
            print(f"strGFileName = {strGFileName}")
            print(f"bExecuteGCode = {bExecuteGCode}")
            print(f"current_status = {current_status}")
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def _open_gcode_dialog(self):
        gcode = ""
        try:
            tool_radius = self.tool_radius.value()
            cutter_offset = self.cutter_offset.value()
            cutter_deepth = self.cutter_deepth.value()
            rotation_speed = self.rotation_speed.value()
            generator = GCode(
                self.dxf_entities,
                tool_radius,
                cutter_offset,
                rotation_speed,
                cutter_deepth,
            )
            gcode = generator.generate()
        except Exception as e:
            QMessageBox.warning(self, "Warning", e.args[0])
            # @todo
            # raise e
            return

        dlg = GCodeDialog(self, gcode)
        dlg.setFixedSize(800, 390)
        dlg.exec()

    def _go_home(self):
        if PLC_CONN.is_open:
            print("GVL_HMI.bHome=True")
            PLC_CONN.write_by_name("GVL_HMI.bHome", True, pyads.PLCTYPE_BOOL)
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def _reset_machine(self):
        if PLC_CONN.is_open:
            reset_machine()
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def _unimplement(self):
        QMessageBox.warning(self, "Warning", "开发中")

    def _regist_fullscreen(self):
        self.toggle_fullscreen_shortcut = QShortcut(QKeySequence(Qt.Key_F11), self)
        self.toggle_fullscreen_shortcut.activated.connect(self._toggle_fullscreen)

        self.exit_fullscreen_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.exit_fullscreen_shortcut.activated.connect(self._exit_fullscreen)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    def refresh_recipe_combo(self):
        print("refresh recipe dialog")
        current_index = self.recipe_combox.currentIndex()
        current_recipe = self.recipe_combox.itemData(current_index)
        self.recipe_combox.reloadRecipes()
        if current_recipe is not None:
            self.recipe_combox.setCurrentIndexByRecipeId(current_recipe._id)

    def recipe_selection_changed(self, index):
        recipe = self.recipe_combox.itemData(index)
        self.load_recipe(recipe)

    def load_recipe(self, recipe: Optional[Recipe]):
        if recipe is not None:
            self.tool_radius.setValue(recipe._tool_radius or 0)
            self.cutter_offset.setValue(recipe._cutter_offset or 0)
            self.rotation_speed.setValue(recipe._rotation_speed or 0)
            self.cutter_deepth.setValue(recipe._cutter_deepth or 0)
            dxf_path = DXF_PATH / f"{recipe._id}.dxf"
            self.load_dxf_file(dxf_path)
        else:
            self.tool_radius.setValue(0)
            self.cutter_offset.setValue(0)
            self.rotation_speed.setValue(0)
            self.cutter_deepth.setValue(0)
            self.set_empty_document()
