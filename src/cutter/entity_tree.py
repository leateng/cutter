from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem

class EntityTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setColumnCount(2)  # 设置列数为2
        # self.setHeaderHidden(True)
        self.setHeaderLabels(["Name", "Entity Type"])
        self.header().resizeSection(0, 200)

        # 创建一个根节点
        root = QTreeWidgetItem(self)
        root.setText(0, "Root")
        root.setText(1, "Data")

        # 创建一个子节点，并将其添加到根节点下
        child1 = QTreeWidgetItem(root)
        child1.setText(0, "Child 1")
        child1.setText(1, "More data")

        # 创建一个子树，并将其添加到根节点下
        child2 = QTreeWidgetItem(root)
        child2.setText(0, "Child 2")
        child2.setText(1, "")
        subchild1 = QTreeWidgetItem(child2)
        subchild1.setText(0, "Subchild 1")
        subchild1.setText(1, "Even more data")
        subchild2 = QTreeWidgetItem(child2)
        subchild2.setText(0, "Subchild 2")
        subchild2.setText(1, "")

        # 将根节点添加到树中
        self.addTopLevelItem(root)
