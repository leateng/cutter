import sys
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QSpacerItem, QVBoxLayout, QHBoxLayout, QFormLayout
import cutter.rc_images

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        # 设置对话框标题
        self.setWindowTitle("登录")

        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(":/images/hc.png"))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建用户名标签、文本框
        self.username_label = QLabel("用户:")
        self.username_edit = QLineEdit()

        # 创建密码标签、文本框
        self.password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password) # 输入时显示为*

        # 创建登录按钮
        self.login_button = QPushButton("登录")        # 创建取消按钮和布局
        self.cancel_button = QPushButton("取消")
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.cancel_button)

        # 创建 FormLayout 并将组件添加到布局中
        self.form_layout = QFormLayout()
        self.form_layout.addRow(self.username_label, self.username_edit)
        self.form_layout.addRow(self.password_label, self.password_edit)

        # 将登录按钮添加到主布局中
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.logo)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)

        # 将主布局设置为对话框的布局
        self.setLayout(self.main_layout)

        # 连接登录按钮的点击事件
        self.login_button.clicked.connect(self.validate_login)
        self.cancel_button.clicked.connect(self.reject)

        # 设置对话框大小和最小尺寸
        self.setFixedSize(300, 180)
        self.setMinimumSize(300, 150)

    @Slot()
    def validate_login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        # 此处应调用验证函数，这里只做简单的模拟
        if username == "root" and password == "root":
            self.accept() # 验证成功，关闭对话框
        else:
            self.password_edit.clear() # 清空密码文本框
            self.password_edit.setPlaceholderText("用户名或密码错误")
            self.password_edit.setStyleSheet("QLineEdit { background-color: #FFCCCC; }") # 将密码文本框的背景色设置为红色
