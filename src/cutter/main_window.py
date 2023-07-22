import os

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
from cutter.cad_widget import CADGraphicsView, DxfEntityScence
from cutter.consts import SUPPORTED_ENTITY_TYPES
from cutter.entity_tree import EntityTree
from cutter.gcode import GCode
from cutter.gcode_dialog import GCodeDialog
from cutter.joy import JoyDialog
from cutter.machine_info import MachineInfo
from cutter.plc import PLC_CONN
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
        self._regist_fullscreen()

        # self._init_statusbar()

    def _init_toolbar(self):
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(48, 48))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        action_open_dxf = QAction(QIcon(QPixmap(":/images/dxf.png")), "打开文件", self)
        action_open_dxf.triggered.connect(self._select_doc)
        toolbar.addAction(action_open_dxf)

        action_start_machine = QAction(
            QIcon(QPixmap(":/images/start.png")), "启动机器", self
        )
        # action_start_machine.setIconText("start")
        # action_start_machine.setStatusTip("This is your button")
        action_start_machine.triggered.connect(self._start_machine)
        toolbar.addAction(action_start_machine)

        action_open_recipe = QAction(
            QIcon(QPixmap(":/images/folder.png")), "配方管理", self
        )
        action_open_recipe.triggered.connect(self._open_recipe_dialog)
        toolbar.addAction(action_open_recipe)

        action_user_manage = QAction(QIcon(QPixmap(":/images/user1.png")), "用户管理", self)
        action_user_manage.triggered.connect(self._open_users_management)
        toolbar.addAction(action_user_manage)

        action_controller = QAction(
            QIcon(QPixmap(":/images/game-controller.png")), "JOY", self
        )
        action_controller.triggered.connect(self._open_joy)
        toolbar.addAction(action_controller)

        generate_gcode = QAction(QIcon(QPixmap(":/images/gcode.png")), "生成GCODE", self)
        generate_gcode.triggered.connect(self._open_gcode_dialog)
        toolbar.addAction(generate_gcode)

        go_home = QAction(QIcon(QPixmap(":/images/target.png")), "回零", self)
        go_home.triggered.connect(self._go_home)
        toolbar.addAction(go_home)

        action_about_us = QAction(QIcon(QPixmap(":/images/info.png")), "关于我们", self)
        action_about_us.triggered.connect(self._open_about_us)
        toolbar.addAction(action_about_us)

        # set background image
        banner_image = QLabel()
        banner_image.setPixmap(QPixmap(":/images/hc.png"))
        banner_image.setScaledContents(True)  # 自动缩放图像以适应标签大小
        banner_image.setStyleSheet("background: transparent; padding-right: 5px;")
        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)

        # 添加标签和占位符到工具栏中
        toolbar.addWidget(spacer)
        toolbar.addWidget(banner_image)

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
        self.rotation_speed.setRange(0, 6000)

        machine_param_layout = QFormLayout()
        machine_param_layout.addRow(QLabel("刀具半径(mm)"), self.tool_radius)
        machine_param_layout.addRow(QLabel("偏移量(mm)"), self.cutter_offset)
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

    def _open_about_us(self):
        dlg = AboutUsDialog()
        dlg.exec()

    def _open_recipe_dialog(self):
        dlg = RecipeDialg(self)
        dlg.resize(1200, 600)
        dlg.exec()

    def _open_users_management(self):
        dlg = UsersDialog()
        dlg.resize(1000, 620)
        dlg.exec()

    def _open_joy(self):
        dlg = JoyDialog()
        dlg.exec()

    def _init_statusbar(self):
        self.statusBar = QStatusBar()
        self.b = QPushButton("click here")
        self.statusBar.addWidget(QLabel("x: 1, y:2 z: 3"))
        self.setStatusBar(self.statusBar)

    def _start_machine(self):
        if len(self.dxf_entities) == 0:
            QMessageBox.warning(self, "Warning", "没有可用的dxf实体!")
            return

        gcode = ""
        try:
            tool_radius = self.tool_radius.value()
            cutter_offset = self.cutter_offset.value()
            rotation_speed = self.rotation_speed.value()
            generator = GCode(
                self.dxf_entities, tool_radius, cutter_offset, rotation_speed
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
            rotation_speed = self.rotation_speed.value()
            generator = GCode(
                self.dxf_entities, tool_radius, cutter_offset, rotation_speed
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
