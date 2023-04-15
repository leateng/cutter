from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QFileDialog, QMessageBox, QSizePolicy, QSplitter, QToolBar, QVBoxLayout, QWidget, QPushButton
import ezdxf
from ezdxf.lldxf.const import DXFStructureError
from qtpy.QtWidgets import QGroupBox, QStatusBar
from cutter.about_dialog import AboutUsDialog
from cutter.cad_widget import CADGraphicsView, DxfEntityScence
from cutter.consts import SUPPORTED_ENTITY_TYPES
from cutter.entity_tree import EntityTree
import cutter.rc_images
from cutter.recipe_combox import RecipeCombo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dxf_entities = []
        self._init_toolbar()
        self._init_layout()
        self._init_statusbar()

        menu = self.menuBar()
        select_doc_action = QAction("File", self)
        select_doc_action.triggered.connect(self._select_doc)
        menu.addAction(select_doc_action)

    def _init_toolbar(self):
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        action_start_machine = QAction(QIcon(QPixmap(":/images/start.png")), "启动机器", self)
        # action_start_machine.setIconText("start")
        # action_start_machine.setStatusTip("This is your button")
        action_start_machine.triggered.connect(self._unimplement)
        toolbar.addAction(action_start_machine)

        action_open_recipe = QAction(QIcon(QPixmap(":/images/folder.png")), "配方管理", self)
        action_open_recipe.triggered.connect(self._unimplement)
        toolbar.addAction(action_open_recipe)

        action_user_manage = QAction(QIcon(QPixmap(":/images/user1.png")), "用户管理", self)
        action_user_manage.triggered.connect(self._unimplement)
        toolbar.addAction(action_user_manage)

        action_controller = QAction(QIcon(QPixmap(":/images/game-controller.png")), "JOY", self)
        action_controller.triggered.connect(self._unimplement)
        toolbar.addAction(action_controller)

        generate_gcode = QAction(QIcon(QPixmap(":/images/gcode.png")), "生成GCODE", self)
        generate_gcode.triggered.connect(self._unimplement)
        toolbar.addAction(generate_gcode)

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

        machine_info_layout = QVBoxLayout()
        machine_info_layout.addWidget(QLabel("坐标: X: 12 Y: 11 Z: 22"))
        machine_info_layout.addWidget(QLabel("转速: 5000"))
        machine_info_group = QGroupBox("机器信息")
        machine_info_group.setLayout(machine_info_layout)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.addWidget(self.recipe_combox)
        left_layout.addWidget(self.entity_tree)
        left_layout.addWidget(machine_info_group)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.view)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)


        self.main_splitter.addWidget(left_widget)
        self.main_splitter.addWidget(right_widget)
        # self.setFixedSize(self.size())

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
        mps = doc.modelspace()
        self.doc = doc
        self.dxf_entities = doc.modelspace().query(" ".join(SUPPORTED_ENTITY_TYPES))

        # draw entity view
        self.scene = DxfEntityScence(self.dxf_entities)
        self.view.setScene(self.scene)
        self.view.fit_to_scene()

        # draw entity tree
        # self.entity_tree = EntityTree(self.dxf_entities)
        self.entity_tree.set_entities(self.dxf_entities)

    def onStartCutter(self):
        print("start machine")

    def _open_about_us(self):
        dlg = AboutUsDialog()
        dlg.exec()

    def _init_statusbar(self):
        self.statusBar = QStatusBar()
        self.b = QPushButton("click here")
        self.statusBar.addWidget(QLabel("x: 1, y:2 z: 3"))
        self.setStatusBar(self.statusBar)

    def _unimplement(self):
        QMessageBox.information(self, "Info", str("开发中"))
