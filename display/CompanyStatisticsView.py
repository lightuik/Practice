import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QPushButton, QLabel, \
    QListView
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, pyqtSignal


class CompanyStatisticsView(QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建中央部件和主布局
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # 添加工具按钮
        tool_button1 = QPushButton("工具1")
        tool_button2 = QPushButton("工具2")
        tool_button3 = QPushButton("工具3")

        toolbar.addWidget(tool_button1)
        toolbar.addWidget(tool_button2)
        toolbar.addWidget(tool_button3)

        # 创建图表显示区域
        chart_layout = QVBoxLayout()
        chart_view = self.create_chart()
        chart_area = QWidget()
        chart_area.setLayout(chart_layout)
        chart_layout.addWidget(chart_view)

        # 创建 Watchlist
        watchlist_layout = QVBoxLayout()
        watchlist = QListView()
        watchlist_label = QLabel("Watchlist")
        watchlist_layout.addWidget(watchlist_label)
        watchlist_layout.addWidget(watchlist)
        watchlist_layout.addStretch(1)  # Watchlist 底部添加一个弹性空间
        watchlist_area = QWidget()
        watchlist_area.setLayout(watchlist_layout)

        # 将所有部件添加到主布局
        main_layout.addWidget(chart_area)
        main_layout.addWidget(watchlist_area)
        main_layout.setStretch(0, 4)  # 设置图表显示区域的伸展系数
        main_layout.setStretch(1, 1)  # 设置 Watchlist 的伸展系数

        self.setCentralWidget(central_widget)
        self.setGeometry(300, 300, 800, 600)

    def create_chart(self):
        # 创建示例图表
        series = QLineSeries()
        series.append(0, 6)
        series.append(2, 4)
        series.append(3, 8)
        series.append(7, 4)
        series.append(10, 5)

        chart = QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("示例图表")

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)  # 使用 QPainter.Antialiasing

        return chart_view

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CompanyStatisticsView()
    sys.exit(app.exec_())
