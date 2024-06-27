from PyQt5.QtWidgets import *
from control import *
import sys


# 数据显示界面
class DataShowWindow:
    def __init__(self):
        pass

    def show_login(self):
        self.login = LoginWindowInit()
        self.login.pushButton.clicked.connect(self.window_display)
        self.login.pushButton_2.clicked.connect(self.quit)
        self.login.show()

    def quit(self):
        self.login.close()

    def window_display(self):
        self.display = DisplayWindowInit()
        self.login.close()
        self.display.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataShowWindow()
    window.show_login()
    sys.exit(app.exec())
