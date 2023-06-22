import qtawesome as qta
from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from cutter.gcode import GCode


class GCodeDialog(QDialog):
    def __init__(self, parent=None, gcode_text=None):
        super().__init__(parent)

        # 设置对话框标题和大小
        self.setWindowTitle("gcode")
        self.resize(800, 480)

        self.gcode_edit = QTextEdit(self)
        self.gcode_edit.setPlainText(gcode_text)
        # 将组件添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.gcode_edit)

        self.setLayout(layout)
