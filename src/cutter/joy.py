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
from cutter.plc import PLC_CONN, read_axis
from cutter.axis_timer import axis_timer
from cutter.machine_info import MachineInfo
from cutter.consts import ALIGNMENT


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
        self.setFixedSize(1100, 590)


class JoyButton(QPushButton):
    def __init__(
        self,
        icon: QIcon,
        orientation: bool,
        axis: str,
        slow_speed: bool = False,
        parent: Optional[qtpy.QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(icon, parent)

        self.orientation = orientation
        self.axis = axis
        self.press_status = False
        if slow_speed is True:
            self.speed = 1.0
        else:
            self.speed = 10.0

        self.setIconSize(QSize(50, 50))

        self.setStyleSheet(
            """
            QPushButton{
                font-size: 50px;
                width: 100px;
                height: 100px;
                border-radius: 50px;
                image: url(:/images/button-bg.png);
                border: 0px;
                
            }
            QPushButton:hover{
                image: url(:/images/button-bg2.png);
                border: 0px;
            }
            QPushButton:pressed{
                image: url(:/images/button-bg.png);
                border: 0px;
            }
                           """
        )
        self.pressed.connect(self.on_button_pressed)
        self.released.connect(self.on_button_released)

        # Styling
        # iconsstyling_icon=qta.icon('fa5s.music',active='fa5s.balance-scale',color='blue',color_active='orange')
        # music_button=QtGui.QPushButton(styling_icon,'Styling')

    def send_move_instruction(self, name, value, val_type):
        if PLC_CONN.is_open:
            print(f"write: {name}={value}")
            PLC_CONN.write_by_name(name, value, val_type)
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

    def speed_instruction_name(self):
        return f"GVL_HMI.lrJogVlct{self.axis}"

    def on_button_pressed(self):
        print("Jog button pressed")
        self.press_status = True

        self.send_move_instruction(
            self.speed_instruction_name(), self.speed, pyads.PLCTYPE_LREAL
        )
        self.send_move_instruction(self.instruction_name(), True, pyads.PLCTYPE_BOOL)
        self.send_move_instruction("GVL_HMI.bJog", True, pyads.PLCTYPE_BOOL)

    def on_button_released(self):
        print("Jog button released")
        self.press_status = False

        self.send_move_instruction(self.instruction_name(), False, pyads.PLCTYPE_BOOL)
        self.send_move_instruction("GVL_HMI.bJog", False, pyads.PLCTYPE_BOOL)


class JoyPad(QWidget):
    def __init__(self, parent: Optional[qtpy.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        # icon_text_color = "#525960"
        icon_text_color = "#1C1C1B"

        self.button_up = JoyButton(
            qta.icon("fa.angle-double-up", color=icon_text_color),
            True,
            "Z",
        )
        self.button_down = JoyButton(
            qta.icon("fa.angle-double-down", color=icon_text_color), False, "Z"
        )

        self.button_slow_up = JoyButton(
            qta.icon("fa.angle-up", color=icon_text_color), True, "Z", True
        )
        self.button_slow_down = JoyButton(
            qta.icon("fa.angle-down", color=icon_text_color), False, "Z", True
        )

        self.button_right = JoyButton(
            qta.icon("fa.angle-double-right", color=icon_text_color), True, "X"
        )
        self.button_left = JoyButton(
            qta.icon("fa.angle-double-left", color=icon_text_color), False, "X"
        )

        self.button_slow_right = JoyButton(
            qta.icon("fa.angle-right", color=icon_text_color), True, "X", True
        )
        self.button_slow_left = JoyButton(
            qta.icon("fa.angle-left", color=icon_text_color), False, "X", True
        )

        self.button_forward = JoyButton(
            qta.icon("fa.angle-double-up", color=icon_text_color), True, "Y"
        )
        self.button_back = JoyButton(
            qta.icon("fa.angle-double-down", color=icon_text_color), False, "Y"
        )

        self.button_slow_forward = JoyButton(
            qta.icon("fa.angle-up", color=icon_text_color), True, "Y", True
        )
        self.button_slow_back = JoyButton(
            qta.icon("fa.angle-down", color=icon_text_color), False, "Y", True
        )

        z_button_layout = QVBoxLayout()
        z_button_layout.addWidget(self.button_up)
        z_button_layout.addWidget(self.button_slow_up)
        z_button_layout.addStretch(1)
        z_button_layout.addWidget(self.button_slow_down)
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
        xy_button_layout.addWidget(self.button_left, 2, 0)
        xy_button_layout.addWidget(self.button_right, 2, 4)
        xy_button_layout.addWidget(self.button_forward, 0, 2)
        xy_button_layout.addWidget(self.button_back, 4, 2)

        xy_button_layout.addWidget(self.button_slow_left, 2, 1)
        xy_button_layout.addWidget(self.button_slow_right, 2, 3)
        xy_button_layout.addWidget(self.button_slow_forward, 1, 2)
        xy_button_layout.addWidget(self.button_slow_back, 3, 2)
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
        self.x_spinbox.setMaximum(9999)
        self.x_spinbox.setMinimum(-9999)

        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setMaximum(9999)
        self.y_spinbox.setMinimum(-9999)

        self.z_spinbox = QDoubleSpinBox()
        self.z_spinbox.setMaximum(9999)
        self.z_spinbox.setMinimum(-9999)

        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.on_go_button_click)

        self.machine_info = MachineInfo(self)

        xyz_layout = QFormLayout()
        xyz_layout.addRow(QLabel("X"), self.x_spinbox)
        xyz_layout.addRow(QLabel("Y"), self.y_spinbox)
        xyz_layout.addRow(QLabel("Z"), self.z_spinbox)

        # 对刀
        self.align_x_button = QPushButton("左边对齐")
        self.align_x_button.clicked.connect(self.confirm_alignment_x)
        self.align_x = QDoubleSpinBox()
        self.align_x.setMaximum(9999)
        self.align_x.setMinimum(-9999)
        self.align_x.setEnabled(False)
        if ALIGNMENT["x"] is not None:
            self.align_x.setValue(ALIGNMENT["x"])

        self.align_y_button = QPushButton("下边对齐")
        self.align_y_button.clicked.connect(self.confirm_alignment_y)
        self.align_y = QDoubleSpinBox()
        self.align_y.setMaximum(9999)
        self.align_y.setMinimum(-9999)
        self.align_y.setEnabled(False)
        if ALIGNMENT["y"] is not None:
            self.align_y.setValue(ALIGNMENT["y"])

        self.align_z_button = QPushButton("顶部对齐")
        self.align_z_button.clicked.connect(self.confirm_alignment_z)
        self.align_z = QDoubleSpinBox()
        self.align_z.setMaximum(9999)
        self.align_z.setMinimum(-9999)
        self.align_z.setEnabled(False)
        if ALIGNMENT["z"] is not None:
            self.align_z.setValue(ALIGNMENT["z"])

        align_layout_x = QHBoxLayout()
        align_layout_x.addWidget(QLabel("X: "))
        align_layout_x.addWidget(self.align_x)
        align_layout_x.addWidget(self.align_x_button)

        align_layout_y = QHBoxLayout()
        align_layout_y.addWidget(QLabel("Y: "))
        align_layout_y.addWidget(self.align_y)
        align_layout_y.addWidget(self.align_y_button)

        align_layout_z = QHBoxLayout()
        align_layout_z.addWidget(QLabel("Z: "))
        align_layout_z.addWidget(self.align_z)
        align_layout_z.addWidget(self.align_z_button)

        align_layout = QVBoxLayout()
        align_layout.addLayout(align_layout_x)
        align_layout.addLayout(align_layout_y)
        align_layout.addLayout(align_layout_z)

        go_button_layout = QHBoxLayout()
        go_button_layout.addStretch(1)
        go_button_layout.addWidget(self.go_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(xyz_layout)
        main_layout.addLayout(go_button_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(align_layout)
        main_layout.addWidget(self.machine_info)
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
            x = self.x_spinbox.value()
            y = self.y_spinbox.value()
            z = self.z_spinbox.value()
            print(f"absoulute move to: x={x}, y={y}, z={z}")

            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosX", x, pyads.PLCTYPE_LREAL)
            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosY", y, pyads.PLCTYPE_LREAL)
            PLC_CONN.write_by_name("GVL_HMI.lrAutoMovePosZ", z, pyads.PLCTYPE_LREAL)
            PLC_CONN.write_by_name("GVL_HMI.bAutoMove", True, pyads.PLCTYPE_BOOL)
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def confirm_alignment_x(self):
        if PLC_CONN.is_open:
            x, y, z = read_axis()
            ALIGNMENT["x"] = x
            self.align_x.setValue(ALIGNMENT["x"])
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def confirm_alignment_y(self):
        if PLC_CONN.is_open:
            x, y, z = read_axis()
            ALIGNMENT["y"] = y
            self.align_y.setValue(ALIGNMENT["y"])
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")

    def confirm_alignment_z(self):
        if PLC_CONN.is_open:
            x, y, z = read_axis()
            ALIGNMENT["z"] = z
            self.align_z.setValue(ALIGNMENT["z"])
        else:
            QMessageBox.warning(self, "Warning", "PLC 未连接")
