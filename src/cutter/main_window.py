from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QToolBar
import ezdxf
from ezdxf.lldxf.const import DXFStructureError
from cutter.cad_widget import CADGraphicsView, DxfEntityScence
import cutter.rc_images


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_toolbar()
        self.view = CADGraphicsView()
        self.scene = DxfEntityScence([])
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.view.fit_to_scene()

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
        action_start_machine.triggered.connect(self.onStartCutter)
        action_start_machine.setCheckable(False)
        toolbar.addAction(action_start_machine)

        action_open_recipe = QAction(QIcon(QPixmap(":/images/folder.png")), "配方管理", self)
        # action_open_recipe.setIconText("start")
        # action_open_recipe.setStatusTip("open recipe")
        action_open_recipe.triggered.connect(self.onStartCutter)
        action_open_recipe.setCheckable(False)
        toolbar.addAction(action_open_recipe)

        action_user_manage = QAction(QIcon(QPixmap(":/images/add-user.png")), "用户管理", self)
        # action_user_manage.setStatusTip("button")
        action_user_manage.triggered.connect(self.onStartCutter)
        action_user_manage.setCheckable(False)
        toolbar.addAction(action_user_manage)

        action_controller = QAction(QIcon(QPixmap(":/images/game-controller.png")), "JOY", self)
        # action_controller.setIconText("start")
        # action_controller.setStatusTip("This is your button")
        action_controller.triggered.connect(self.onStartCutter)
        action_controller.setCheckable(False)
        toolbar.addAction(action_controller)

        action_about_us = QAction(QIcon(QPixmap(":/images/info.png")), "关于我们", self)
        # action_about_us.setIconText("start")
        # action_about_us.setStatusTip("About Us")
        action_about_us.triggered.connect(self.onStartCutter)
        action_about_us.setCheckable(False)
        toolbar.addAction(action_about_us)

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
        entities = [e for e in mps]
        self.scene = DxfEntityScence(entities)
        self.view.setScene(self.scene)
        self.view.fit_to_scene()

    def onStartCutter(self):
        print("start machine")
