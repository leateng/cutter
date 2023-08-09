from qtpy.QtWidgets import QWidget, QLabel, QFormLayout


class MachineInfo(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.state_label = QLabel("断开")
        self.axis_label = QLabel("X: 0.00, Y: 0.00, Z: 0.00")
        self.rotate_speed_label = QLabel("0")

        machine_info_layout = QFormLayout()
        # plc_status = "已连接" if PLC_CONN.is_open else "断开"
        machine_info_layout.addRow(QLabel("连接状态"), self.state_label)
        machine_info_layout.addRow(QLabel("坐标"), self.axis_label)
        machine_info_layout.addRow(QLabel("转速"), self.rotate_speed_label)
        self.setLayout(machine_info_layout)

    def update(self, state):
        print(f"update MachineInfo: {state}")
        x = state["x"]
        y = state["y"]
        z = state["z"]
        is_open = state["is_open"]

        if is_open is True:
            self.state_label.setText("已连接")
        else:
            self.state_label.setText("断开")

        self.axis_label.setText("X: {:.2f}, Y: {:.2f}, Z: {:.2f}".format(x, y, z))
