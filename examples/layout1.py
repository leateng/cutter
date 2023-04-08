from PySide6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QSplitter, QVBoxLayout

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("left"))
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("right"))

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)


        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        # self.setFixedSize(self.size())

        hbox.addWidget(splitter)
        self.setLayout(hbox)

        # 设置左侧宽度
        sizes = [300, 800]
        splitter.setSizes(sizes)

         # 禁止主窗口随着调整而自动放大

        # 使QSplitter右侧自适应大小
        splitter.setStretchFactor(1, 1)

        self.resize(1100, 900)

if __name__ == '__main__':
    app = QApplication([])
    ex = Example()
    ex.show()
    app.exec()
