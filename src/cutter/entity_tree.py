import itertools

import ezdxf
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QCheckBox
from qtpy.QtWidgets import QTreeWidget
from qtpy.QtWidgets import QTreeWidgetItem
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QWidget


class EntityTree(QTreeWidget):
    def __init__(self, entities=[]):
        super().__init__()
        self.entities = entities
        self.initUI()
        self.setStyleSheet("QTreeView::item { padding-bottom: 5px };")

    def initUI(self):
        self.setColumnCount(2)  # 设置列数为2
        # self.setHeaderHidden(True)
        self.setHeaderLabels(["ID", "Entity Type"])
        self.header().resizeSection(0, 200)
        self.build_entities_tree()

    def set_entities(self, entities):
        self.entities = entities
        self.clear()
        self.build_entities_tree()

    def build_entities_tree(self):
        print(f"tree total entities: {len(self.entities)}")
        # @todo
        layer_groups = {}
        for layer_name, layer_entities in itertools.groupby(
            self.entities, lambda x: x.dxfattribs()["layer"]
        ):
            layer_groups[layer_name] = list(layer_entities)

        # embed()
        # # 读取dxf文件
        # doc = ezdxf.readfile("./dxf-examples/gb.dxf")
        # msp = doc.modelspace()

        # 遍历所有图层
        # for layer in doc.layers:
        #     ents = msp.query(f"LINE ARC CIRCLE [layer=='{layer.dxf.name}']")
        for layer_name in layer_groups:
            ents = layer_groups[layer_name]
            print(f"layer={layer_name} ents={len(ents)}")

            # skip empty layer
            if len(ents) == 0:
                continue

            # 创建一个图层节点，并将其添加到根节点下
            # layer_node = QTreeWidgetItem(root)
            layer_node = QTreeWidgetItem(self)
            # layer_node.setText(0, layer.dxf.name)
            layer_node.setText(0, layer_name)
            layer_node.setText(1, "")
            layer_node.setCheckState(0, Qt.CheckState.Checked)

            # 遍历图层中的实体
            for entity in ents:
                print(f"ent type = {entity.dxftype()}")
                # for entity in layer.query():
                # 创建一个实体节点，并将其添加到图层节点下
                entity_node = QTreeWidgetItem(layer_node)
                entity_node.setText(0, entity.dxf.handle)
                entity_node.setText(1, str(entity.dxftype()))
                entity_node.setCheckState(0, Qt.CheckState.Checked)

            self.addTopLevelItem(layer_node)
