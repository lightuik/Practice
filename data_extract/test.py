import re
from bs4 import BeautifulSoup
from data_extract.DataExtract import DataTempStore, DataExtractor
from bs4 import BeautifulSoup
def extract_dates(text):
    # 定义正则表达式模式，匹配年份、任意字符、月份、任意字符和日期
    date_pattern = r'(2024)(.{1})(\d{1,2})(.{1})(\d{1,2})'
    # 使用re.findall来查找所有匹配的日期
    matches = re.findall(date_pattern, text)
    # 将匹配的结果格式化为日期字符串
    dates = ["{}{}{}{}{}".format(year,'/', month, '/', day) for year,_ ,month,__ ,day in matches]
    return dates[0]
def get_dates(content,type):
    extractor = DataExtractor()
    content = extractor.decode(content, type)
    if type=="html":
        return extract_dates(content.get_text())
    else:
        return extract_dates(content.replace('\n', '').replace(' ', ''))
if __name__=="__main__":
    df = DataTempStore("E:\curriculums\datas")
    df["date"] = df.apply(lambda row: get_dates(row["content"],row["filetype"]), axis=1)
    a=0