from typing import Any, Optional, Union

import pyads
import qtawesome as qta
import qtpy.QtCore
import qtpy.QtWidgets
from qtpy.QtCore import QAbstractTableModel, QModelIndex, QSize, Qt, Slot
from qtpy.QtGui import QBrush, QColor, QIcon, QPixmap
from qtpy.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from cutter.plc import PLC_CONN


class JoyDialog(QDialog):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.joy_pad = JoyPad()
        self.ab_move = ABMoveWidget()
        self.ab_move.resize(200, 200)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.joy_pad)
        main_layout.addWidget(self.ab_move)
        self.setLayout(main_layout)

        self.setWindowTitle("JOY")
        self.setWindowIcon(QIcon(QPixmap(":/images/game-controller.png")))


class JoyButton(QPushButton):
    def __init__(
        self,
        icon: QIcon,
        orientation: bool,
        axis: str,
        parent: Optional[qtpy.QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(icon, parent)

        self.orientation = orientation
        self.axis = axis
        self.press_status = False

        self.setStyleSheet(
            """
            QPushButton{
                font-size: 50px;
                width: 98px;
                height: 98px;
                border-radius: 50px;
                background-color: rgb(255, 170, 127);
                border: 1px solid rgb(255, 170, 127);
                color: white;
            }
            QPushButton:hover{
                border: 1px double rgb(255, 85, 0);
            }
            QPushButton:pressed{
                background-color: rgb(255, 85, 0);
                border: 1px solid rgb(255, 85, 0);
            }
                           """
        )
        self.pressed.connect(self.on_button_pressed)
        self.released.connect(self.on_button_released)

    def send_move_instruction(self, name, value):
        if PLC_CONN.is_open:
            PLC_CONN.write_by_name(name, value, pyads.PLCTYPE_BOOL)
        else:
            if self.press_status:
                QMessageBox.warning(None, "Warning", "PLC 未连接")

    def orientation_name(self):
        if self.orientation:
            return "Forward"
        else:
            return "Backward"

    def instruction_name(self):
        return f"GVL_HMI.bJog{self.orientation_name()}{self.axis}"

    def on_button_pressed(self):
        print("Jog button pressed")
        self.press_status = True
        self.send_move_instruction("GVL_HMI.bJog", True)
        self.send_move_instruction(self.instruction_name(), True)

    def on_button_released(self):
        print("Jog button released")
        self.press_status = False
        self.send_move_instruction("GVL_HMI.bJog", False)
        self.send_move_instruction(self.instruction_name(), False)


class JoyPad(QWidget):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.button_up = JoyButton(qta.icon("ei.arrow-up", color="#525960"), True, "Z")
        self.button_down = JoyButton(
            qta.icon("ei.arrow-down", color="#525960"), False, "Z"
        )

        self.button_right = JoyButton(
            qta.icon("ei.arrow-right", color="#525960"), True, "X"
        )
        self.button_left = JoyButton(
            qta.icon("ei.arrow-left", color="#525960"), False, "X"
        )

        self.button_forward = JoyButton(
            qta.icon("ei.arrow-up", color="#525960"), True, "Y"
        )
        self.button_back = JoyButton(
            qta.icon("ei.arrow-down", color="#525960"), False, "Y"
        )

        self.button_up.setIconSize(QSize(50, 50))
        self.button_down.setIconSize(QSize(50, 50))
        self.button_left.setIconSize(QSize(50, 50))
        self.button_right.setIconSize(QSize(50, 50))
        self.button_forward.setIconSize(QSize(50, 50))
        self.button_back.setIconSize(QSize(50, 50))

        z_button_layout = QVBoxLayout()
        z_button_layout.addWidget(self.button_up)
        z_button_layout.addStretch(1)
        z_button_layout.addWidget(self.button_down)
        z_button_group = QGroupBox("Z")
        z_button_group.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
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
        xy_button_group.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        xy_button_group.setLayout(xy_button_layout)
        xy_button_group_wrapper_layout = QVBoxLayout()
        xy_button_group_wrapper_layout.addWidget(xy_button_group)

        main_layout = QHBoxLayout()
        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        main_layout.addLayout(z_button_group_wrapper_layout)
        main_layout.addLayout(xy_button_group_wrapper_layout)

        self.setLayout(main_layout)


class ABMoveWidget(QWidget):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.x_spinbox = QDoubleSpinBox()
        self.y_spinbox = QDoubleSpinBox()
        self.z_spinbox = QDoubleSpinBox()

        self.align_left = QPushButton("左边对齐")
        self.align_bottom = QPushButton("下边对齐")
        self.align_top = QPushButton("顶部对齐")

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.on_go_button_click)

        xyz_layout = QFormLayout()
        xyz_layout.addRow(QLabel("X"), self.x_spinbox)
        xyz_layout.addRow(QLabel("Y"), self.y_spinbox)
        xyz_layout.addRow(QLabel("Z"), self.z_spinbox)

        align_layout = QHBoxLayout()
        align_layout.addWidget(self.align_left)
        align_layout.addWidget(self.align_bottom)
        align_layout.addWidget(self.align_top)

        go_button_layout = QHBoxLayout()
        go_button_layout.addStretch(1)
        go_button_layout.addWidget(self.go_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(xyz_layout)
        main_layout.addLayout(go_button_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(align_layout)
        # main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        groupbox = QGroupBox("Move")
        groupbox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        groupbox.setLayout(main_layout)
        group_wrapper_layout = QVBoxLayout()
        group_wrapper_layout.addWidget(groupbox)

        self.setLayout(group_wrapper_layout)

    def on_go_button_click(self):
        if PLC_CONN.is_open:
            x = self.x_spinbox.value
            y = self.y_spinbox.value
            z = self.z_spinbox.value
            print(f"absoulute move to: x={x}, y={y}, z={z}")

            PLC_CONN.write_by_name("GVL_HMI.bAutoMove", True, pyads.PLCTYPE_BOOL)
            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosX", x, pyads.PLCTYPE_LREAL)
            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosY", y, pyads.PLCTYPE_LREAL)
            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosZ", z, pyads.PLCTYPE_LREAL)
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")
