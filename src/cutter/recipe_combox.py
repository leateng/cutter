from qtpy.QtWidgets import QComboBox


class RecipeCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["recipe 1", "recipe 2", "recipe 3"])
