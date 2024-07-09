import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, \
    QTextBrowser, QPushButton
from display.control import MainPage
from display.CompanyStatisticsView import CompanyStatisticsView


class MainWindow(QWidget):
    def __init__(self,path_of_company,path_of_product):
        super().__init__()
        self.setWindowTitle("主页")
        with open(path_of_company, 'r', encoding='utf-8') as file:
            self.names= file.readlines()
            self.names = [name.strip() for name in self.names]
        with open(path_of_product, 'r', encoding='utf-8') as file:
            self.products= file.readlines()
            self.products = [p.strip() for p in self.products]
        self.SetUP()
    def SetUP(self):
        layout = QVBoxLayout(self)
        self.main_page = MainPage(self.names,self.products)
        # 连接信号与槽，通过 lambda 函数传递 self.main_page
        self.main_page.company_combo.currentIndexChanged.connect(
            lambda index: self.open_company_statistics_view(index, self.main_page))
        layout.addWidget(self.main_page)
        self.main_page.search_btn.clicked.connect(lambda: self.search(self.main_page.search_box.text(), self.main_page))
        self.main_page.search_box.returnPressed.connect(lambda: self.search(self.main_page.search_box.text(), self.main_page))
    def open_company_statistics_view(self, index, main_page):
        combo = main_page.sender()
        try:
            text = combo.currentText()
        except:
            text=index
            index=1
        if text not in main_page.popups or main_page.popups[text] is None:
            company_statistics_view = CompanyStatisticsView(self.products,self.names,text)
            company_statistics_view.setWindowTitle(text)
            main_page.popups[text] = company_statistics_view
            company_statistics_view.closed.connect(lambda: self.close_company_statistics_view(text, main_page))
        else:
            company_statistics_view = main_page.popups[text]

        if index > 0:
            company_statistics_view.show()
        else:
            company_statistics_view.hide()
    def search(self,name,main_page):
        if name in self.names:
            self.open_company_statistics_view(name,main_page)

    def close_company_statistics_view(self, text, main_page):
        if text in main_page.popups:
            main_page.popups[text] = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    PATH_OF_COMPANY = "E:\curriculums\Practice\data_extract\company.txt"
    PATH_OF_PRODUCT = 'E:\curriculums\Practice\data_extract\products.txt'
    window = MainWindow(PATH_OF_COMPANY,PATH_OF_PRODUCT)
    window.show()
    sys.exit(app.exec_())
