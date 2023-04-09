import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QCheckBox
import ezdxf


class DxfTree(QMainWindow):
    def __init__(self, filename):
        super().__init__()

        # Load DXF file
        self.doc = ezdxf.readfile(filename)

        # Initialize tree widget and checkbox dict
        self.tree = QTreeWidget()
        self.checkboxes = {}

        # Build tree
        self.build_tree()

        # Set main window properties
        self.setWindowTitle(filename)
        self.setCentralWidget(self.tree)
        self.resize(640, 480)

    def build_tree(self):
        # Add DXF layers as root nodes
        for layer in self.doc.layers:
            item = QTreeWidgetItem(self.tree, [layer.dxf.name])
            self.tree.addTopLevelItem(item)

            # Add entities as child nodes
            for entity in layer.query("*"):
                entity_item = QTreeWidgetItem(item, [str(entity.dxf.handle)])
                item.addChild(entity_item)

                # Add checkbox to each node
                checkbox = QCheckBox()
                checkbox.setCheckState(Qt.Unchecked)
                self.tree.setItemWidget(entity_item, 0, checkbox)

                # Record checkbox object in dict
                self.checkboxes[entity_item] = checkbox

    def get_checked_items(self):
        checked_items = []
        for item, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                checked_items.append(item)
        return checked_items


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DxfTree('./dxf-example/gb.dxf')
    window.show()
    sys.exit(app.exec())
