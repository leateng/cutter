from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
import ezdxf
from ezdxf.lldxf.const import DXFStructureError
from cutter.cad_widget import CADGraphicsView, DxfEntityScence

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.view = CADGraphicsView()
        self.scene = DxfEntityScence([])
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        self.view.fit_to_scene()

        menu = self.menuBar()
        select_doc_action = QAction("File", self)
        select_doc_action.triggered.connect(self._select_doc)
        menu.addAction(select_doc_action)

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
