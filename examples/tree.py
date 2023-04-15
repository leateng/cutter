# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem

# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         vbox = QVBoxLayout()

#         tree = QTreeWidget()
#         tree.setColumnCount(2)  # 设置列数为2

#         # 创建一个根节点
#         root = QTreeWidgetItem(tree)
#         root.setText(0, "Root")
#         root.setText(1, "Data")

#         # 创建一个子节点，并将其添加到根节点下
#         child1 = QTreeWidgetItem(root)
#         child1.setText(0, "Child 1")
#         child1.setText(1, "More data")

#         # 创建一个子树，并将其添加到根节点下
#         child2 = QTreeWidgetItem(root)
#         child2.setText(0, "Child 2")
#         child2.setText(1, "")
#         subchild1 = QTreeWidgetItem(child2)
#         subchild1.setText(0, "Subchild 1")
#         subchild1.setText(1, "Even more data")
#         subchild2 = QTreeWidgetItem(child2)
#         subchild2.setText(0, "Subchild 2")
#         subchild2.setText(1, "")

#         # 将根节点添加到树中
#         tree.addTopLevelItem(root)

#         vbox.addWidget(tree)
#         self.setLayout(vbox)

# if __name__ == '__main__':
#     app = QApplication([])
#     ex = Example()
#     ex.show()
#     app.exec_()

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QCheckBox
from PySide6.QtCore import Qt
from IPython import embed
import ezdxf

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        tree = QTreeWidget()
        tree.setColumnCount(2)  # 设置列数为2

        # # 创建一个根节点
        # root = QTreeWidgetItem(tree)
        # root.setText(0, "Layers")
        # root.setText(1, "")

        # 读取dxf文件
        doc = ezdxf.readfile("./dxf-examples/gb.dxf")
        msp = doc.modelspace()

        # 遍历所有图层
        for layer in doc.layers:
            ents = msp.query(f"LINE ARC CIRCLE [layer=='{layer.dxf.name}']")
            embed()

            # skip empty layer
            if len(ents) == 0:
                continue

            # 创建一个图层节点，并将其添加到根节点下
            # layer_node = QTreeWidgetItem(root)
            layer_node = QTreeWidgetItem(tree)
            layer_node.setText(0, layer.dxf.name)
            layer_node.setText(1, "")
            layer_node.setCheckState(0, Qt.CheckState.PartiallyChecked)

            # 遍历图层中的实体
            for entity in ents:
            # for entity in layer.query():
                # 创建一个实体节点，并将其添加到图层节点下
                entity_node = QTreeWidgetItem(layer_node)
                entity_node.setText(0, entity.dxftype())
                entity_node.setText(1, str(entity.dxf.handle))
                entity_node.setCheckState(0, Qt.CheckState.Checked)

            tree.addTopLevelItem(layer_node)

        # 将根节点添加到树中
        # tree.addTopLevelItem(root)

        vbox.addWidget(tree)
        self.setLayout(vbox)

    def get_checked_entities(self):
        checked_entities = []
        for layer_index in range(self.tree.topLevelItemCount()):
            layer_node = self.tree.topLevelItem(layer_index)
            for entity_index in range(layer_node.childCount()):
                entity_node = layer_node.child(entity_index)
                if entity_node.checkState(0) == 2:
                    checked_entities.append(entity_node.text(1))
        return checked_entities

if __name__ == '__main__':
    app = QApplication([])
    ex = Example()
    ex.show()
    app.exec_()
