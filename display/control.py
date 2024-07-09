from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet  # Assuming you are using the qt_material package for Material Design

class MainPage(QWidget):
    def __init__(self, names, products):
        super().__init__()
        self.setWindowTitle("主页")
        self.names = names
        self.products = products
        self.popups = {}  # Dictionary to store popups
        self.initUI()

    def initUI(self):
        # Apply a dark theme to the MainPage and its children
        self.setFont(QFont("Robot",12))
        self.setStyleSheet("""
            QWidget {
                background-color: #212121;
                color: #FFFFFF;
            }
            QComboBox, QLineEdit, QPushButton {
                background-color: #424242;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox:hover, QLineEdit:hover, QPushButton:hover {
                background-color: #616161;
            }
            QPushButton {
                background-color: #1976D2;
            }
            QPushButton:hover {
                background-color: #FF5722;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # Set widget spacing

        # Dropdown layout
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(15)

        # Company dropdown
        self.company_combo = QComboBox()
        self.company_combo.addItem("公司")
        self.company_combo.addItems(self.names)
        self.company_combo.setFont(QFont('Roboto', 12))
        self.company_combo.setMaximumWidth(200)
        combo_layout.addWidget(self.company_combo)

        # Search box layout
        search_layout = QHBoxLayout()
        self.search_btn = QPushButton("搜索")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索")
        self.search_box.setFont(QFont('Roboto', 12))
        self.search_box.setMaximumWidth(400)
        self.search_box.setAlignment(Qt.AlignCenter)
        search_layout.addStretch(1)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.search_box)
        search_layout.addStretch(1)

        # Add layouts to main layout
        main_layout.addLayout(combo_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(search_layout)
        main_layout.addStretch(2)

        self.setLayout(main_layout)
        self.setGeometry(300, 300, 600, 200)
        self.setWindowTitle('期货系统')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = MainPage(["公司A", "公司B", "公司C"], ["产品1", "产品2", "产品3"])
    ex.show()
    sys.exit(app.exec_())
