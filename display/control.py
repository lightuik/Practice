from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.popups = {}  # 用于存储弹出窗口的字典
        self.initUI()
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 设置控件间距

        # 创建下拉框布局
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)  # 设置下拉框间距

        # 创建下拉框
        self.company_combo = QComboBox()
        self.company_combo.addItem("公司")
        self.company_combo.addItems(["公司1", "公司2", "公司3"])
        self.company_combo.setFont(QFont('Arial', 12))

        self.product_combo = QComboBox()
        self.product_combo.addItem("产品")
        self.product_combo.addItems(["产品1", "产品2", "产品3"])
        self.product_combo.setFont(QFont('Arial', 12))

        self.news_combo = QComboBox()
        self.news_combo.addItem("新闻")
        self.news_combo.addItems(["新闻1", "新闻2", "新闻3"])
        self.news_combo.setFont(QFont('Arial', 12))

        # 设置下拉框最大宽度
        self.company_combo.setMaximumWidth(200)
        self.product_combo.setMaximumWidth(200)
        self.news_combo.setMaximumWidth(200)

        # 将下拉框添加到布局
        combo_layout.addWidget(self.company_combo)
        combo_layout.addWidget(self.product_combo)
        combo_layout.addWidget(self.news_combo)

        # 创建搜索框布局
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索")
        self.search_box.setFont(QFont('Arial', 12))
        self.search_box.setMaximumWidth(400)
        self.search_box.setAlignment(Qt.AlignCenter)

        search_layout.addStretch(1)
        search_layout.addWidget(self.search_box)
        search_layout.addStretch(1)

        # 将下拉框布局和搜索框布局添加到主布局
        main_layout.addLayout(combo_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(search_layout)
        main_layout.addStretch(2)

        # 设置主布局为窗口布局
        self.setLayout(main_layout)
        self.setGeometry(300, 300, 600, 200)
        self.setWindowTitle('谷歌风格界面')

        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
        """)
    def show_popup(self, index):
        if index > 0:  # 避免显示默认选项
            combo = self.sender()
            text = combo.currentText()

            if text not in self.popups:  # 检查页面是否已经存在
                popup = PopupWindow(text)
                popup.show()
                self.popups[text] = popup


class PopupWindow(QWidget):
    def __init__(self, title):
        super().__init__()
        self.initUI(title)

    def initUI(self, title):
        layout = QVBoxLayout()
        label = QLabel(f'你选择了: {title}')
        layout.addWidget(label)
        self.setLayout(layout)
        self.setWindowTitle('弹出页面')
        self.setGeometry(400, 400, 300, 200)
def main():
    app = QApplication(sys.argv)
    main_page = MainPage()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

