import sys
import os

os.environ['QT_API'] = 'pyside6'
# from PySide6.QtWidgets import QApplication
from qtpy.QtWidgets import QApplication, QDialog
from cutter.login import LoginDialog
from cutter.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    if (login_dialog.exec() == QDialog.DialogCode.Accepted):
        # 验证成功，启动程序
        print("Successful login")
        win = MainWindow()
        win.resize(1200, 900)
        win.show()
        app.exec()
    else:
        # 用户取消登录，退出程序
        print("Login cancelled")
        sys.exit()
