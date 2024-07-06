# 工具函数
from bs4 import BeautifulSoup
import pandas as pd
class TextGetorHtml:
    def __init__(self,soup,company_name):
        self.soup=soup
        self.company_name=company_name
        self.get_from_tabel_list=["上海中期","中泰期货","先锋期货","兴业期货","通道期货"]
    def get_text_from_table(self):
        table_list=extract_tables_from_html(self.soup)
        return concatenate_dataframes(table_list[0])
    def get_text_from_texts(self):
        return self.soup.get_text()
    def get_texts(self):
        if self.company_name not in self.get_from_tabel_list:
            return self.get_text_from_texts()
        elif self.company_name=="华融融达":
            return None
        else:
            return self.get_text_from_table()

def extract_tables_from_html(soup):
    tables = soup.find_all("table")
    # 初始化一个列表来存储所有的表格数据
    df_list = []
    # 提取每个表格的内容并保存到DataFrame中
    for table in tables:
        headers = []
        rows = []
        # 提取表头
        for th in table.find_all('th'):
            headers.append(th.get_text(strip=True))
        # 提取表格行
        for tr in table.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            if len(cells) > 0:
                row = [cell.get_text(strip=True) for cell in cells]
                rows.append(row)
        # 创建DataFrame
        if headers:
            df = pd.DataFrame(rows, columns=headers)
        else:
            df = pd.DataFrame(rows)
        # 添加到列表中
        df_list.append(df)
    return df_list
def concatenate_dataframes(df, separator=","):
    result = []
    for row in df.itertuples(index=False, name=None):  # 去掉表头，并且每行作为元组
        row_str = separator.join(map(str, row))  # 将每个元素转为字符串并用分隔符拼接
        result.append(row_str)
    return "|".join(result)# 每行之间用换行符分隔
if __name__=="__main__":
    with open("E:\curriculums\Practice\data_extract\chart\中泰期货\中泰期货_232471_2.html", 'r', encoding='UTF-8') as f:
        html_content = f.read()
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    extract_tables_from_html(soup)