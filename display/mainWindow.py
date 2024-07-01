import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, \
    QTextBrowser, QPushButton
from control import MainPage
from CompanyStatisticsView import CompanyStatisticsView


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.SetUP()

    def SetUP(self):
        layout = QVBoxLayout(self)
        self.main_page = MainPage()

        # 连接信号与槽，通过 lambda 函数传递 self.main_page
        self.main_page.company_combo.currentIndexChanged.connect(
            lambda index: self.open_company_statistics_view(index, self.main_page))
        self.main_page.product_combo.currentIndexChanged.connect(
            lambda index: self.open_company_statistics_view(index, self.main_page))
        self.main_page.news_combo.currentIndexChanged.connect(
            lambda index: self.open_company_statistics_view(index, self.main_page))

        layout.addWidget(self.main_page)

    def open_company_statistics_view(self, index, main_page):
        combo = main_page.sender()
        text = combo.currentText()

        if text not in main_page.popups or main_page.popups[text] is None:
            company_statistics_view = CompanyStatisticsView()
            company_statistics_view.setWindowTitle(text)
            main_page.popups[text] = company_statistics_view
            company_statistics_view.closed.connect(lambda: self.close_company_statistics_view(text, main_page))
        else:
            company_statistics_view = main_page.popups[text]

        if index > 0:
            company_statistics_view.show()
        else:
            company_statistics_view.hide()

    def close_company_statistics_view(self, text, main_page):
        if text in main_page.popups:
            main_page.popups[text] = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
