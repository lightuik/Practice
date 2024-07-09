import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QDesktopWidget
from display.mainWindow import MainWindow  # 假设这是你的 MainPage 类
from display.LoginWindow import LoginWindow  # 假设这是你的 LoginWindow 类
from qt_material import apply_stylesheet
PATH_OF_COMPANY="E:\curriculums\Practice\data_extract\company.txt"
PATH_OF_PRODUCT='E:\curriculums\Practice\data_extract\products.txt'
from PyQt5.QtGui import QFont

class MyAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_window = LoginWindow()
        self.login_window.login_clicked.connect(self.show_main_page)
        self.login_window.show()

    def show_main_page(self):
        self.setWindowTitle("主页")
        self.login_window.close()  # 关闭登录窗口
        # 设置窗口大小
        self.resize(800, 600)
        # 创建主窗口部件
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        # 创建并添加 MainPage 到布局
        main_page = MainWindow(PATH_OF_COMPANY,PATH_OF_PRODUCT)
        layout = QVBoxLayout(main_widget)
        layout.addWidget(main_page)
        # 将窗口居中显示
        window_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    extra = {
        'font_family': 'Roboto',
        'font_size': '12px'  # 设置字号为 12 像素
    }
    apply_stylesheet(app, theme='dark_cyan.xml',extra=extra)
    window = MyAPP()
    sys.exit(app.exec_())