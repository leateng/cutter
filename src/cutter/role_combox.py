from cutter.consts import ROLE_NAMES
from qtpy.QtWidgets import QComboBox


class RoleCombox(QComboBox):
    def __init__(self):
        super().__init__()

        for k in ROLE_NAMES:
            self.addItem(ROLE_NAMES[k], k)

        self.currentIndexChanged.connect(self.on_currentIndexChanged)

    def on_currentIndexChanged(self, index):
        key = self.currentData()
        value = self.currentText()
        print("Selected item:", key, value)
