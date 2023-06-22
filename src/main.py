import os
import sys

from qtpy import QtCore, QtGui
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QApplication, QDialog

import cutter.consts as g
from cutter.database import init_db
from cutter.login import LoginDialog
from cutter.main_window import MainWindow
from cutter.plc import init_plc_conn
from cutter.axis_timer import axis_timer

os.environ["QT_API"] = "pyside2"

if __name__ == "__main__":
    # guiapp = QtGui.QGuiApplication(sys.argv)
    # dpi = (guiapp.screens()[0]).logicalDotsPerInch()
    # print(f"screen logical dpi: {dpi}")
    #
    # if dpi == 96.0:
    #     QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling)
    # else:
    #     QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

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
    init_plc_conn()
    axis_timer.start()

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
