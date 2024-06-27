from LoginWIndow import LoginWindow
from DisplayWindow import DisplayWindow
from PyQt5 import QtWidgets


class LoginWindowInit(QtWidgets.QWidget, LoginWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class DisplayWindowInit(QtWidgets.QWidget, DisplayWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
