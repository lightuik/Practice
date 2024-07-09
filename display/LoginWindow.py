from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
class LoginWindow(QtWidgets.QWidget):
    login_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Login")
        self.resize(400, 150)
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()
        self.label = QtWidgets.QLabel("账号：")
        self.lineEdit = QtWidgets.QLineEdit()
        form_layout.addRow(self.label, self.lineEdit)
        self.label_2 = QtWidgets.QLabel("密码：")
        self.lineEdit_2 = QtWidgets.QLineEdit()
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(self.label_2, self.lineEdit_2)

        layout.addLayout(form_layout)
        button_layout = QtWidgets.QHBoxLayout()
        self.pushButton = QtWidgets.QPushButton("登录")
        self.pushButton.clicked.connect(self.login_clicked.emit)
        self.pushButton_2 = QtWidgets.QPushButton("退出")
        self.pushButton_2.clicked.connect(QtCore.QCoreApplication.instance().quit)
        button_layout.addWidget(self.pushButton)
        button_layout.addWidget(self.pushButton_2)

        layout.addLayout(button_layout)

        self.setLayout(layout)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
