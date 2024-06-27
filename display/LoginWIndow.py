from PyQt5 import QtCore, QtWidgets


class LoginWindow(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        height = 150
        width = 400
        Form.resize(width, height)  # 窗口大小

        label_width = int(width/5.5)
        label_height = int(height/10)
        button_width = int(width/4)
        button_height = int(height/5)
        lineedit_width = int(width/2)
        lineedit_height = int(height/7.5)

        # 水平方向上的居中位置
        label_x = (400 - label_width) // 2 - 100
        button_x = (400 - button_width) // 2 - (button_width // 2)
        lineedit_x = (400 - lineedit_width) // 2

        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(label_x, 30, label_width, label_height))
        self.label.setObjectName("label")
        self.label.setText("账号：")

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(label_x, 60, label_width, label_height))
        self.label_2.setObjectName("label_2")
        self.label_2.setText("密码：")

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(button_x, 100, button_width, button_height))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("登录")

        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(button_x + button_width + 10, 100, button_width, button_height))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("退出")

        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(lineedit_x, 30, lineedit_width, lineedit_height))
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(lineedit_x, 60, lineedit_width, lineedit_height))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)  # 设置密码输入框的文字显示为密码形式
