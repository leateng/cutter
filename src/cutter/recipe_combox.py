from PySide6.QtWidgets import QComboBox

class RecipeCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["One", "Two", "Three"])
