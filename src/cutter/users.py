from typing import Any, Optional, Union
from datetime import datetime
import PySide6.QtCore
import PySide6.QtWidgets
from PySide6.QtCore import QModelIndex, Qt, QAbstractTableModel, Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QAbstractItemView, QApplication, QDialog, QHBoxLayout, QHeaderView, QMessageBox, QPushButton, QTableView, QVBoxLayout
from cutter.consts import COLUMN_NAME_MAPPING, ROLE_NAMES

class UserModel(QAbstractTableModel):

    def __init__(self, parent: Optional[PySide6.QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self.rawData = [
                {"name": "liteng", "dept": "QA", "role": 1, "created_at": datetime.now() },
                {"name": "Jim", "dept": "DEV", "role": 2, "created_at": datetime.now() },
                {"name": "Sam", "dept": "DEV", "role": 3, "created_at": datetime.now() },
                ]

    def headerData(self, section: int, orientation: PySide6.QtCore.Qt.Orientation, role: int = 0)-> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ["姓名", "部门", "角色", "创建时间"][section]

        return super().headerData(section, orientation, role)


    def rowCount(self, parent: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex] = None) -> int:
        return len(self.rawData)

    def columnCount(self, parent: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex] = None ) -> int:
        return 4

    def sort(self, column: int, order: PySide6.QtCore.Qt.SortOrder = ...) -> None:
        print(f"sort column: {column} order: {order}")
        return super().sort(column, order)

    # def flags(self, index):
    #     return Qt.ItemFlag.ItemIsEditable | super().flags(index)

    def data(self, index: Union[PySide6.QtCore.QModelIndex, PySide6.QtCore.QPersistentModelIndex], role: int = 0) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            column_name = self.columnIndexToRowName(column)
            data = self.rawData[row][column_name]
            print(f"Row{row}, Column{column}, column_name: {column_name}, data={data}")

            if data:
                if column_name == "role":
                    return ROLE_NAMES[str(data)]
                elif column_name == "created_at":
                    return data.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    return data
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
               return  QBrush(QColor(248, 249, 251))

        # return super().data(index, role)
        return None

    def columnIndexToRowName(self, i: int) -> str:
        mapping = ["name", "dept", "role", "created_at"]
        return mapping[i]

    def addUser(self, userData):
        self.rawData.append(userData)


class UsersGridView(QTableView):
    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # self.setColumnWidth(0, 200)
        # self.setColumnWidth(1, 200)
        # self.setColumnWidth(2, 200)
        # self.setColumnWidth(3, 200)
        # self.verticalHeader().show()
        self.setSortingEnabled(True)

        self.doubleClicked.connect(self.editUserDialog)

    # def sortByColumn(self, column: int, order: Qt.SortOrder):
    #     print(f"column={column}, order={order}")

    def editUserDialog(self, index: QModelIndex = None ) -> None:
        print("edit user")

class UsersDialog(QDialog):
    def __init__(self, parent: Optional[PySide6.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.usersModel = UserModel()
        self.usersView = UsersGridView()
        self.usersView.setModel(self.usersModel)
        self.addUserButton = QPushButton("Add")
        self.addUserButton.clicked.connect(self.addUser)
        self.deleteUserButton = QPushButton("Delete")
        self.deleteUserButton.clicked.connect(self.deleteUsers)

        action_layout = QHBoxLayout()
        action_layout.addStretch(1)
        action_layout.addWidget(self.addUserButton)
        action_layout.addWidget(self.deleteUserButton)

        grid_layout = QHBoxLayout()
        grid_layout.addWidget(self.usersView)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(action_layout)
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

    def deleteUsers(self):
        indexes = self.usersView.selectionModel().selectedRows()
        if len(indexes) < 1:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setText("请选择要删除的用户！")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
        else:
            index = indexes[0]
            print(f"delete row {index.row()}")

    def addUser(self):
        self.usersModel.addUser( {"name": "liteng", "dept": "QA", "role": 1, "created_at": datetime.now() })
        self.usersModel.layoutChanged.emit()


# if __name__ == "__main__":
#     app = QApplication([])

#     dlg = UsersDialog()
#     dlg.resize(1000, 620)
#     dlg.show()
#     app.exec()
