# Practice
v 1.0.0
1. 合并了data_manage和data_extract，修改了其中部分代码
2. display部分简单完成了登录界面和界面之间的切换
3. 数据清洗部分封装了关键词提取

v 2.0.0
1. 完善了各模块
2. 更新了预测模块

v3.0.0
1. 完善了各个提取模块

v3.1.0
1. 进一步解决了bug，并增加了时间提取

v3.1.2
1. 修改了parse_html和parse_pdf的返回值，返回值更方便构建dataframe
2. 优化了部分路径表示，使用os.path.join代替硬编码
3. 解决了get_time的bug
   soup.get_text()有可能不包含时间信息，因为有的html文件时间被放在之前的宏定义里，所以直接传入str(soup)
4. 删除函数DataExtract.DataTempStore，修改后的文件读取方式不再需要它构建dataframe。
5. 在parse_pdf中添加：
   ```python
   if keys not in self.all_params_pdf.keys():
       self.all_params_pdf[keys]={'keyword': ['all'], "pages": [], "chart": None, "distance": 15}
   ```
   把没提取的关键字的公司设置成上述。
6. 将parse_pdf提取内容进行封装
