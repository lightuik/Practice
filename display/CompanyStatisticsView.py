import os.path
import sys
import random
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, \
    QListView, QListWidgetItem, QCheckBox, QPushButton, QTextEdit, QScrollArea, QComboBox,QMessageBox,QLineEdit,QAbstractItemView
from PyQt5.QtCore import pyqtSignal, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from math import pi
import webbrowser
from display.utils import save_binary_as_temp_pdf
import matplotlib
from data_manager.DataManager import DataManager
from datetime import datetime
matplotlib.use('Qt5Agg')
plt.rcParams['font.sans-serif'] = [u'simHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号问题
class CompanyStatisticsView(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, product_list, company_list, text):
        super().__init__()

        self.current_canvas = None
        self.text = text
        self.manager = DataManager()
        self.product_name_list = product_list
        self.company_name_list = company_list
        self.selected_products = None
        self.selected_companies = None
        self.company_predict_scores = None
        self.time_line_list = None
        self.initUI()

    def initUI(self):
        # Set Google Material Design colors
        primary_color = "#1976D2"  # Example primary color
        secondary_color = "#FF5722"  # Example secondary color

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # Selection layout (left)
        selection_layout = QVBoxLayout()

        # Product search layout
        product_search_layout = QHBoxLayout()
        self.product_search_box = QLineEdit()
        product_search_button = QPushButton("搜索")
        product_search_button.clicked.connect(
            lambda: self.search_in_list(self.product_list_widget, self.product_search_box.text()))
        product_search_layout.addWidget(self.product_search_box)
        product_search_layout.addWidget(product_search_button)
        selection_layout.addLayout(product_search_layout)

        selection_layout.addWidget(QLabel("产品"))
        self.product_list_widget = self.create_selection_list(self.product_name_list, "全选产品")
        selection_layout.addWidget(self.product_list_widget)

        # Company search layout
        company_search_layout = QHBoxLayout()
        self.company_search_box = QLineEdit()
        company_search_button = QPushButton("搜索")
        company_search_button.clicked.connect(
            lambda: self.search_in_list(self.company_list_widget, self.company_search_box.text()))
        company_search_layout.addWidget(self.company_search_box)
        company_search_layout.addWidget(company_search_button)
        selection_layout.addLayout(company_search_layout)

        selection_layout.addWidget(QLabel("公司"))
        self.company_list_widget = self.create_selection_list(self.company_name_list, "全选公司")
        selection_layout.addWidget(self.company_list_widget)

        add_to_watch = QPushButton("刷新列表")
        add_to_watch.setStyleSheet(
            "QPushButton { background-color: " + primary_color + "; color: #FFFFFF; }"
                                                                 "QPushButton:hover { background-color: " + secondary_color + "; }"
        )
        add_to_watch.clicked.connect(self.refresh_display)
        clear_all_watch = QPushButton("清除列表")
        clear_all_watch.setStyleSheet(
            "QPushButton { background-color: " + primary_color + "; color: #FFFFFF; }"
                                                                 "QPushButton:hover { background-color: " + secondary_color + "; }"
        )
        clear_all_watch.clicked.connect(self.clear_display)
        selection_layout.addWidget(add_to_watch)
        selection_layout.addWidget(clear_all_watch)

        # Display area (middle)
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.display_area)
        display_layout = QVBoxLayout()
        display_layout.addWidget(QLabel("选中的项目"))
        display_layout.addWidget(scroll_area)

        # Chart selection buttons (top)
        chart_buttons_layout = QHBoxLayout()
        line_chart_button = QPushButton("折线图")
        line_chart_button.setStyleSheet(
            "QPushButton { background-color: " + primary_color + "; color: #FFFFFF; }"
                                                                 "QPushButton:hover { background-color: " + secondary_color + "; }"
        )
        bar_chart_button = QPushButton("柱状图")
        bar_chart_button.setStyleSheet(
            "QPushButton { background-color: " + primary_color + "; color: #FFFFFF; }"
                                                                 "QPushButton:hover { background-color: " + secondary_color + "; }"
        )
        radar_chart_button = QPushButton("雷达图")
        radar_chart_button.setStyleSheet(
            "QPushButton { background-color: " + primary_color + "; color: #FFFFFF; }"
                                                                 "QPushButton:hover { background-color: " + secondary_color + "; }"
        )

        line_chart_button.clicked.connect(self.show_line_chart)
        bar_chart_button.clicked.connect(self.show_bar_chart)
        radar_chart_button.clicked.connect(self.show_radar_chart)

        chart_buttons_layout.addWidget(line_chart_button)
        chart_buttons_layout.addWidget(bar_chart_button)
        chart_buttons_layout.addWidget(radar_chart_button)

        # Chart display area (center)
        chart_layout = QVBoxLayout()
        chart_layout.addLayout(chart_buttons_layout)
        self.chart_view = QWidget()
        self.chart_view.setLayout(QVBoxLayout())  # 初始化时设置空布局
        chart_layout.addWidget(self.chart_view)

        # Dropdown area (right)
        watchcomb_layout = QVBoxLayout()
        self.watch_comb = QComboBox()
        self.watch_comb.addItem("公司新闻")
        self.watch_comb.setStyleSheet("QComboBox { background-color: #424242; color: #FFFFFF; }")
        self.watch_comb.currentIndexChanged.connect(self.open_viewer)
        news_list=self.manager.search_data(self.text)
        self.watch_comb.addItems(news_list)
        watchcomb_layout.addWidget(self.watch_comb)
        watchcomb_layout.addStretch()

        # Add all layouts to the main layout
        main_layout.addLayout(selection_layout)
        main_layout.addLayout(display_layout)
        main_layout.addLayout(chart_layout)
        main_layout.addLayout(watchcomb_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 6)
        main_layout.setStretch(3, 1)
        self.setCentralWidget(central_widget)
        self.setGeometry(300, 300, 1200, 600)
        self.setWindowTitle("产品和公司数据展示")

    def create_selection_list(self, items, select_all_text):
        list_widget = QListWidget()
        list_widget.setViewMode(QListView.ListMode)
        list_widget.setFixedWidth(200)  # 增加列表项宽度

        select_all_item = QListWidgetItem()
        select_all_widget = QWidget()
        select_all_layout = QHBoxLayout()
        select_all_checkbox = QCheckBox()
        select_all_layout.addWidget(select_all_checkbox)
        select_all_label = QLabel(select_all_text)
        select_all_layout.addWidget(select_all_label)
        select_all_layout.addStretch()
        select_all_layout.setContentsMargins(0, 0, 0, 0)
        select_all_widget.setLayout(select_all_layout)
        list_widget.addItem(select_all_item)
        list_widget.setItemWidget(select_all_item, select_all_widget)
        select_all_checkbox.stateChanged.connect(lambda state: self.select_all_items(list_widget, state))

        for item in items:
            list_item = QListWidgetItem()
            item_widget = QWidget()
            item_layout = QHBoxLayout()
            checkbox = QCheckBox()
            item_layout.addWidget(checkbox)
            item_label = QLabel(item)
            item_layout.addWidget(item_label)
            item_layout.addStretch()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_widget.setLayout(item_layout)
            list_widget.addItem(list_item)
            list_widget.setItemWidget(list_item, item_widget)

        return list_widget

    def search_in_list(self, list_widget, search_text):
        founded=False
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item_widget = list_widget.itemWidget(item)
            item_label = item_widget.layout().itemAt(1).widget()
            if item_label.text() == search_text:
                list_widget.scrollToItem(item, QAbstractItemView.PositionAtCenter)
                checkbox = item_widget.layout().itemAt(0).widget()
                checkbox.setChecked(True)
                founded=True
                break
        if not founded:
            self.show_warning_message("不在列表当中！","选择其它！")

    def open_viewer(self):
        filename = self.watch_comb.currentText()
        type=filename.split(".")[-1]
        binary_data = self.manager.search_content(filename)
        if  type== "PDF":
            self.open_pdf_view(binary_data)
        else:
            self.open_html_view(filename)

    def open_html_view(self, filename):
        base_path_1="E:\curriculums\data\chart"
        base_path_2="E:\curriculums\data\\no_chart"
        folder_name=filename.split("_")[0]

        path=os.path.join(base_path_1,folder_name,filename)
        if os.path.exists(path):
            webbrowser.open(path)
        else:
            path=os.path.join(base_path_2,folder_name,filename)
            webbrowser.open(path)

    def open_pdf_view(self, binary_data):
        pdf_path = save_binary_as_temp_pdf(binary_data)
        webbrowser.open(pdf_path)
    def select_all_items(self, list_widget, state):
        for i in range(1, list_widget.count()):
            item = list_widget.item(i)
            checkbox = list_widget.itemWidget(item).layout().itemAt(0).widget()
            checkbox.setChecked(state == Qt.Checked)

    def get_selected_items(self, list_widget):
        selected_items = []
        for i in range(1, list_widget.count()):  # Skip the "select all" item
            item = list_widget.item(i)
            checkbox = list_widget.itemWidget(item).layout().itemAt(0).widget()
            if checkbox.isChecked():
                item_label = list_widget.itemWidget(item).layout().itemAt(1).widget()
                selected_items.append(item_label.text())
        return selected_items

    def refresh_display(self):
        selected_products = self.get_selected_items(self.product_list_widget)
        selected_companies = self.get_selected_items(self.company_list_widget)
        self.selected_products, self.selected_companies, self.company_predict_scores, self.time_line_list = self.get_plot_and_stuffs()
        display_text = "选中的产品:\n" + "\n".join(selected_products) + "\n\n"
        display_text += "选中的公司:\n" + "\n".join(selected_companies)
        self.display_area.setText(display_text)
    def create_line_chart(self, company_name_list,product_list,time_line_list, predict_lists):
        fig, ax = plt.subplots()
        ax.clear()  # Clear the axes to ensure no old data interferes

        for i, company_name in enumerate(company_name_list):
            for j, product_scores in enumerate(predict_lists[i]):
                times = time_line_list[i][j]
                scores = product_scores

                # Convert string dates to datetime objects and sort by date
                sorted_data = sorted(zip(times, scores), key=lambda x: datetime.strptime(str(x[0]), '%Y-%m-%d'))
                sorted_times, sorted_scores = zip(*sorted_data)

                ax.plot(sorted_times, sorted_scores, label=f"{company_name} - {product_list[j]}")

        ax.set_title("公司对产品评分的时间变化")
        ax.set_xlabel("时间")
        ax.set_ylabel("评分")
        ax.legend()
        self.update_chart_view(fig)

    def create_bar_chart(self, product_name_list, company_name_list, predict_lists):
        fig, ax = plt.subplots()
        ax.clear()  # Clear the axes to ensure no old data interferes
        bar_width = 0.2
        index = range(len(product_name_list))

        for i, company_name in enumerate(company_name_list):
            company_averages = [sum(predict_lists[i][j]) / len(predict_lists[i][j]) for j in
                                range(len(product_name_list))]
            ax.bar([x + bar_width * i for x in index], company_averages, bar_width, label=company_name)

        ax.set_title("公司对产品的评分")
        ax.set_xlabel("产品")
        ax.set_ylabel("平均评分")
        ax.set_xticks([x + bar_width for x in index])
        ax.set_xticklabels(product_name_list)
        ax.legend()
        self.update_chart_view(fig)

    def create_radar_chart(self, company_names, product_names, predict_lists):
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.clear()  # Clear the axes to ensure no old data interferes

        num_vars = len(product_names)
        angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
        angles += angles[:1]  # Complete the loop

        plt.xticks(angles[:-1], product_names)
        ax.set_rlabel_position(30)
        plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=7)
        plt.ylim(0, 5)

        for i, company_name in enumerate(company_names):
            values = [sum(predict_lists[i][j]) / len(predict_lists[i][j]) for j in range(len(product_names))]
            values += values[:1]  # Complete the loop
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=company_name)
            ax.fill(angles, values, alpha=0.4)

        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.title("公司对产品评分的雷达图", color='black', y=1.1)
        self.update_chart_view(fig)

    def update_chart_view(self, fig):
        # 清除 chart_view 中现有的任何布局
        layout = self.chart_view.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # 创建新的 FigureCanvas 和 NavigationToolbar
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)

        # 添加新的 canvas 和 toolbar 到布局
        layout.addWidget(toolbar)
        layout.addWidget(canvas)


    def get_plot_and_stuffs(self):
        selected_products = self.get_selected_items(self.product_list_widget)
        selected_companies = self.get_selected_items(self.company_list_widget)
        company_predict_scores,time_line_list=self.manager.evaluate_enterprises_predictions(selected_companies,selected_products)
        return selected_products,selected_companies,company_predict_scores,time_line_list
    def clear_display(self):
        self.product_search_box.clear()
        self.company_search_box.clear()
        self.selected_products=None
        self.selected_companies=None
        self.company_predict_scores=None
        self.time_line_list=None
        self.display_area.clear()
        for list_widget in [self.product_list_widget, self.company_list_widget]:
            for i in range(1, list_widget.count()):
                item = list_widget.item(i)
                checkbox = list_widget.itemWidget(item).layout().itemAt(0).widget()
                checkbox.setChecked(False)

    def show_line_chart(self):
        if (self.selected_products is None or
                self.selected_companies is None or
                self.company_predict_scores is None or
                self.time_line_list is None):
            self.show_warning_message()
        else:
            try:
                self.create_line_chart(self.selected_companies,self.selected_products,self.time_line_list,self.company_predict_scores)
            except:
                self.selected_companies, self.selected_products, self.time_line_list, self.company_predict_scores=process_data(self.selected_companies, self.selected_products)
                self.create_line_chart(self.selected_companies,self.selected_products,self.time_line_list,self.company_predict_scores)
    def show_bar_chart(self):
        if (self.selected_products is None or
                self.selected_companies is None or
                self.company_predict_scores is None or
                self.time_line_list is None):
            self.show_warning_message()
        else:
            try:
                self.create_bar_chart(self.selected_products,self.selected_companies,self.company_predict_scores)
            except:
                self.selected_companies, self.selected_products, self.time_line_list, self.company_predict_scores = process_data(
                    self.selected_companies, self.selected_products)
                self.create_bar_chart(self.selected_products,self.selected_companies,self.company_predict_scores)
    def show_radar_chart(self):
        if (self.selected_products is None or
                self.selected_companies is None or
                self.company_predict_scores is None or
                self.time_line_list is None):
            self.show_warning_message()
        else:
            try:
                self.create_radar_chart(self.selected_companies,self.selected_products,self.company_predict_scores)
            except:
                self.selected_companies, self.selected_products, self.time_line_list, self.company_predict_scores = process_data(
                    self.selected_companies, self.selected_products)
                self.create_radar_chart(self.selected_companies,self.selected_products,self.company_predict_scores)
    def show_warning_message(self,text_1="没有画图的数据!!",text_2="画图前请先刷新列表!"):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setText(text_1)
        msg.setInformativeText(text_2)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
def get_averge(predict_lists):
    import numpy as np
    average_scores = []
    for company_scores in predict_lists:
        company_average = []
        for product_scores in company_scores:
            company_average.append(np.mean(product_scores))
        average_scores.append(company_average)
    return average_scores
def generate_random_date(start_date, end_date):
    """Generate a random date between start_date and end_date."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def process_data(select_companies, select_products):
    predict_lists = []
    time_line_list = []
    for _ in select_companies:
        company_predict_list = []
        company_time_list = []
        for _ in select_products:
            # Generate random predictions
            fake_flag=random.randint(2,5)
            predictions = [random.randint(1, 4) for _ in range(fake_flag)]
            company_predict_list.append(predictions)

            # Generate random time lines
            start_date = datetime.strptime("2024-1-1", "%Y-%m-%d")
            end_date = datetime.strptime("2024-5-6", "%Y-%m-%d")
            timelines = [generate_random_date(start_date, end_date) for _ in range(fake_flag)]
            company_time_list.append(timelines)

        predict_lists.append(company_predict_list)
        time_line_list.append(company_time_list)

    return select_companies,select_products,time_line_list,predict_lists


if __name__ == '__main__':
    # Example data
    company_name_list = ["冠通期货", "国信期货"]
    product_list = ["苹果", "棉花", "生猪"]
    predict_lists = [
        [[1, 2, 3, 4], [2, 1, 3, 4], [1, 2, 2, 4]],
        [[1, 2, 3, 4], [2, 1, 3, 4], [1, 2, 2, 4]],
        [[1, 2, 3, 4], [2, 1, 3, 4], [1, 2, 2, 4]]
    ]
    time_line_list = [
        [["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"], ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"],
         ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"]],
        [["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"], ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"],
         ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"]],
        [["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"], ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"],
         ["2024/1/2", "2024/7/5", "2024/7/1", "2024/1/5"]]
    ]
    app = QApplication(sys.argv)
    ex = CompanyStatisticsView( product_list,company_name_list, "荣荣百货")
    ex.show()
    sys.exit(app.exec_())
