from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QLabel, QPushButton
import qtawesome as qta
from cutter.consts import VERSION

class AboutUsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置对话框标题和大小
        self.setWindowTitle("关于我们")
        # self.resize(400, 300)
        self.setFixedSize(480, 290)
        self.setStyleSheet("background-color: #373c41; color: #ffffff;")

        # 创建组件
        image_label = QLabel("About Us")
        image_label.setPixmap(QPixmap(":/images/hc2.png"))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 联系方式
        address_logo_label = QLabel()
        address_logo_label.setPixmap(qta.icon("ei.map-marker", color="white").pixmap(20, 20))
        address_label = QLabel("烟台总部：中国（山东）自贸区烟台片区长江路300号业达智谷\n华北研发中心：河北省保定市涿州市高新技术产业开发区和谷科技产业园B12楼\n西北研发中心：陕西省西安市未央区草滩生态产业园弘业一路远征科技园1幢3楼")

        email_logo_label= QLabel()
        email_logo_label.setPixmap(qta.icon("mdi.email", color="white").pixmap(20, 20))
        email_label = QLabel("邮箱：nancyzhang@pcm-bj.com")
        
        phone_logo_label = QLabel()
        phone_logo_label.setPixmap(qta.icon("ri.phone-fill", color="white").pixmap(20, 20))
        phone_label = QLabel("电话：0535-6388095")
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        form_layout.addRow(address_logo_label, address_label)
        form_layout.addRow(email_logo_label, email_label)
        form_layout.addRow(phone_logo_label, phone_label)

        # copyright
        copyright_label = QLabel(f"v{VERSION} Copyright © 2023 烟台华创智能装备有限公司")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 将组件添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(image_label)
        layout.addLayout(form_layout)
        layout.addWidget(copyright_label)

        self.setLayout(layout)
