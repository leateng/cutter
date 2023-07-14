from typing import Any
from typing import Optional
from typing import Union

import qtpy.QtCore
import qtpy.QtWidgets
import cutter.consts as g
from cutter.consts import COLUMN_NAME_MAPPING
from cutter.consts import ROLE_NAMES
from cutter.database import DB_CONN
from cutter.database import get_users, create_user, update_user, delete_user
from cutter.models import User
from cutter.role_combox import RoleCombox
from qtpy.QtCore import QAbstractTableModel
from qtpy.QtCore import QModelIndex
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtCore import Slot
from qtpy.QtGui import QBrush
from qtpy.QtGui import QColor
from qtpy.QtGui import QIcon
from qtpy.QtGui import QPixmap
from qtpy.QtSql import QSqlQuery
from qtpy.QtWidgets import QAbstractItemView
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QComboBox
from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QFormLayout
from qtpy.QtWidgets import QHBoxLayout
from qtpy.QtWidgets import QHeaderView
from qtpy.QtWidgets import QLabel
from qtpy.QtWidgets import QLineEdit
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QPushButton
from qtpy.QtWidgets import QTableView
from qtpy.QtWidgets import QTextEdit
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QStyle


class UserModel(QAbstractTableModel):
    def __init__(self, parent: Optional[qtpy.QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self.load_users()

    def load_users(self):
        self.rawData = get_users()

    def headerData(
        self, section: int, orientation: qtpy.QtCore.Qt.Orientation, role: int = 0
    ) -> Any:
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return ["姓名", "部门", "角色", "创建时间"][section]

        return super().headerData(section, orientation, role)

    def rowCount(
        self,
        parent: Union[
            qtpy.QtCore.QModelIndex, qtpy.QtCore.QPersistentModelIndex
        ] = None,
    ) -> int:
        return len(self.rawData)

    def columnCount(
        self,
        parent: Union[
            qtpy.QtCore.QModelIndex, qtpy.QtCore.QPersistentModelIndex
        ] = None,
    ) -> int:
        return 4

    def sort(self, column: int, order: qtpy.QtCore.Qt.SortOrder = ...) -> None:
        print(f"sort column: {column} order: {order}")
        return super().sort(column, order)

    # def flags(self, index):
    #     return Qt.ItemFlag.ItemIsEditable | super().flags(index)

    def data(
        self,
        index: Union[qtpy.QtCore.QModelIndex, qtpy.QtCore.QPersistentModelIndex],
        role: int = 0,
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            column = index.column()
            column_name = self.columnIndexToRowName(column)
            user = self.rawData[row]
            data = user.__getattribute__(f"_{column_name}")
            # print(f"Row{row}, Column{column}, column_name: {column_name}, data={data}")

            if column_name == "role":
                return ROLE_NAMES[str(data)]
            # elif column_name == "created_at":
            #     return data.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return str(data)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() % 2 == 0:
                return QBrush(QColor(248, 249, 251))

        # return super().data(index, role)
        return None

    def columnIndexToRowName(self, i: int) -> str:
        mapping = ["name", "department", "role", "created_at"]
        return mapping[i]

    def addUser(self, userData):
        self.rawData.append(userData)


class UsersGridView(QTableView):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # self.setColumnWidth(0, 200)
        # self.setColumnWidth(1, 200)
        # self.setColumnWidth(2, 200)
        # self.setColumnWidth(3, 200)
        # self.verticalHeader().show()
        self.setSortingEnabled(True)


class UserFormDialog(QDialog):
    saveUser = Signal(User)

    def __init__(
        self,
        user: Optional[User] = None,
        parent: Optional[qtpy.QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        if user is None:
            self.user = User()
            self._is_new = True
        else:
            self.user = user
            self._is_new = False

        self._name_edit = QLineEdit()
        self._department_edit = QLineEdit()
        self._password_edit = QLineEdit()
        self._password_edit.setEchoMode(QLineEdit.Password)
        self._password_confirmation_edit = QLineEdit()
        self._password_confirmation_edit.setEchoMode(QLineEdit.Password)
        self._role_combox = RoleCombox()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow(QLabel("用户名"), self._name_edit)
        form_layout.addRow(QLabel("密码"), self._password_edit)
        form_layout.addRow(QLabel("确认密码"), self._password_confirmation_edit)
        form_layout.addRow(QLabel("部门"), self._department_edit)
        form_layout.addRow(QLabel("角色"), self._role_combox)

        # 创建登录按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        self.setFixedSize(400, 220)

        if self._is_new:
            self.setWindowTitle("添加用户")
        else:
            self.setWindowTitle("编辑用户")
            self._name_edit.setText(self.user._name)
            self._department_edit.setText(self.user._department)
            self._role_combox.setCurrentIndex(self.user._role)

    def get_form_values(self):
        self.user._name = self._name_edit.text()
        self.user._password = self._password_edit.text()
        self.user._department = self._department_edit.text()
        self.user._role = int(self._role_combox.currentData())

    def accept(self):
        self.get_form_values()
        self.saveUser.emit(self.user)
        super().accept()


class UsersDialog(QDialog):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowIcon(QIcon(QPixmap(":/images/user1.png")))
        self.setWindowTitle("用户管理")

        self.usersModel = UserModel()
        self.usersView = UsersGridView()
        self.usersView.setModel(self.usersModel)
        self.addUserButton = QPushButton("Add")
        self.addUserButton.setIcon(QIcon(":/images/add.png"))
        self.deleteUserButton = QPushButton("Delete")

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

        self.addUserButton.clicked.connect(self.openAddUserDialog)
        self.deleteUserButton.clicked.connect(self.deleteUser)
        self.usersView.doubleClicked.connect(self.openUpdateUserDialog)

    def deleteUser(self):
        indexes = self.usersView.selectionModel().selectedRows()
        if len(indexes) < 1:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setText("请选择要删除的用户！")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()
        else:
            index = indexes[0]
            row = index.row()
            user = self.usersModel.rawData[row]
            if user:
                if user._id == g.CURRENT_USER._id:
                    QMessageBox.warning(self, "Warning", "该账号登录中，无法删除！")
                    return

                delete_user(user._id)
                self.usersModel.rawData.pop(row)
                self.usersModel.layoutChanged.emit()

    def openAddUserDialog(self):
        print("create_user")
        dlg = UserFormDialog(None, self)
        dlg.saveUser.connect(self.receiveUserData)
        dlg.exec_()

    def openUpdateUserDialog(self, index: QModelIndex = None) -> None:
        print("edit user: ", index.row())
        if index.row() < len(self.usersModel.rawData):
            user = self.usersModel.rawData[index.row()]
            dlg = UserFormDialog(user, self)
            dlg.saveUser.connect(self.receiveUserData)
            dlg.exec_()

    def receiveUserData(self, user: User):
        print(f"received user data: {user}")
        if user._id is None:
            create_user(user)
        else:
            update_user(user)

        self.usersModel.load_users()
        self.usersModel.layoutChanged.emit()

    # self.usersModel.addUser(
    #     {
    #         "name": "liteng",
    #         "department": "QA",
    #         "role": 1,
    #         "created_at": datetime.now(),
    #     }
    # )
    #
    # query = QSqlQuery(DB_CONN)
    # query.prepare(
    #     "INSERT INTO users (username, password) VALUES (:username, :password)"
    # )
    # query.bindValue(":username", "example_user")
    # query.bindValue(":password", "example_password")
    #
    # if query.exec():
    #     print("插入成功！")
    # else:
    #     print("插入失败：", query.lastError().text())
    # self.usersModel.layoutChanged.emit()
