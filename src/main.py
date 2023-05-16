import os
import sys

import cutter.consts as g
from cutter.database import init_db
from cutter.login import LoginDialog
from cutter.main_window import MainWindow
from cutter.plc import init_plc_conn
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QDialog

os.environ["QT_API"] = "pyside2"

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置默认字体
    font = QFont("Sans", 9)
    app.setFont(font)

    # for debug
    # win = MainWindow()
    # print("main_window")
    # win.show()
    # app.exec_()

    init_db()
    # init_plc_conn()

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # 验证成功，启动程序
        print("Successful login")
        win = MainWindow()
        win.setWindowTitle(f"Cutter-{g.CURRENT_USER._name}")
        win.show()
        app.exec_()
    else:
        # 用户取消登录，退出程序
        print("Login cancelled")
        sys.exit()
