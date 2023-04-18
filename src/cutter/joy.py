from typing import Any, Optional, Union
import qtpy.QtCore
import qtpy.QtWidgets
from qtpy.QtCore import QModelIndex, Qt, QAbstractTableModel, Slot, QSize
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QAbstractItemView, QApplication, QDialog, QHBoxLayout, QHeaderView, QMessageBox, QPushButton, QTableView, QVBoxLayout, QSizePolicy, QLayout, QWidget, QGroupBox, QGridLayout
import qtawesome as qta

class JoyDialog(QDialog):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.joy_pad = JoyPad()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.joy_pad)
        self.setLayout(main_layout)


class JoyPad(QWidget):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.setStyleSheet("""
            QPushButton{
                font-size: 50px;
                width: 100px;
                height: 100px;
                border-radius: 50px;
                background-color: rgb(255, 170, 127);
                border: 2px solid rgb(255, 85, 0);
                color: white;
            }
            QPushButton:hover{
                border: 4px double rgb(0, 255, 0);
            }
            QPushButton:checked{
                background-color: rgb(255, 170, 255);
            }
                           """)

        self.button_up      = QPushButton(qta.icon("ei.caret-up", color="#525960"), "")
        self.button_down    = QPushButton(qta.icon("ei.caret-down", color="#525960").pixmap(100, 100), "")
        self.button_left    = QPushButton(qta.icon("ei.caret-left", color="#525960").pixmap(50, 50), "")
        self.button_right   = QPushButton(qta.icon("ei.caret-right", color="#525960").pixmap(50, 50), "")
        self.button_forward = QPushButton(qta.icon("ei.caret-up", color="#525960").pixmap(50, 50), "")
        self.button_back    = QPushButton(qta.icon("ei.caret-down", color="#525960").pixmap(50, 50), "")

        z_button_layout = QVBoxLayout()
        z_button_layout.addWidget(self.button_up)
        z_button_layout.addStretch(1)
        z_button_layout.addWidget(self.button_down)
        z_button_group = QGroupBox("Z")
        z_button_group.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        z_button_group.setLayout(z_button_layout)
        z_button_group_wrapper_layout = QVBoxLayout()
        # z_button_group_wrapper_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        z_button_group_wrapper_layout.addWidget(z_button_group)

        xy_button_layout = QGridLayout()
        # xy_button_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        xy_button_layout.addWidget(self.button_left, 1, 0)
        xy_button_layout.addWidget(self.button_right, 1, 2)
        xy_button_layout.addWidget(self.button_forward, 0, 1)
        xy_button_layout.addWidget(self.button_back, 2, 1)
        xy_button_group = QGroupBox("X/Y")
        xy_button_group.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        xy_button_group.setLayout(xy_button_layout)
        xy_button_group_wrapper_layout = QVBoxLayout()
        xy_button_group_wrapper_layout.addWidget(xy_button_group)

        main_layout = QHBoxLayout()
        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        main_layout.addLayout(z_button_group_wrapper_layout)
        main_layout.addLayout(xy_button_group_wrapper_layout)

        self.setLayout(main_layout)
