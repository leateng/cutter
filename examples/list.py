from qtpy.QtCore import QAbstractItemModel, QAbstractListModel, QObject, QModelIndex, Qt
from typing import Any, Optional

from qtpy.QtWidgets import QApplication, QListView


class RecipeListModel(QAbstractListModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        # return super().rowCount(parent)
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        return super().data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        return super().setData(index, value, role)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return super().flags(index)


class RecipeListItemModel(QAbstractItemModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)


app = QApplication([])

view = QListView()
model = RecipeListModel()
view.setModel(model)
view.show()

app.exec_()
