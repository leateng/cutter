from qtpy.QtCore import QSize
from qtpy.QtWidgets import QWidget, QLabel, QHBoxLayout
import qtawesome as qta
from cutter.error_codes import get_error_msg


class ErrorInfo(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        icon_size = QSize(24, 24)
        self.green_icon = qta.icon("mdi6.check-circle", color="green").pixmap(icon_size)
        self.red_icon = qta.icon("mdi6.close-circle", color="red").pixmap(icon_size)
        self.state = QLabel()
        self.state.setPixmap(self.green_icon)
        self.message = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.state)
        layout.addWidget(self.message)
        self.setLayout(layout)

    def update_error_info(self, has_error, error_code):
        # print(f"update errorinfo: {has_error}")
        if has_error is True:
            msg = get_error_msg(error_code)
            self.state.setPixmap(self.red_icon)
            self.message.setText(msg)
        else:
            self.state.setPixmap(self.green_icon)
            self.message.setText("No Error")
