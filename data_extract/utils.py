import pdfplumber
import requests
import cv2
import base64
import numpy as np
import fitz
from DataExtract import DocumentProcessor
import re
from data_clean.DataClean import DataClean
import PyPDF2
import pandas as pd
from DataExtract import DataExtractor
from bs4 import BeautifulSoup

cleaner = DataClean()


# 使用百度api请求token
def get_token():
    """
    :return: 返回token
    """
    api_key = ''
    secret_key = ''
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"

    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    access_token = data.get('access_token')
    if not access_token:
        raise "请输入正确的client_id 和 client_secret"
    return access_token


# 调用api对表格识别
def api_detect(path, access_token):
    '''
    :param path: 路径
    :param access_token: 百度所需要的token
    :return: 无返回
    '''
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/table"
    f = open(path, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    print(response)
    if response:
        print(response.json())


# 将pix转换为img
def pix2img(pix):
    """
    :param pix:为pix格式的图片
    :return: 返回numpy形式的图片
    """
    image_data = pix.samples
    image_size = (pix.height, pix.width, 3)
    # 将数据转换为一个NumPy数组并重塑为正确的形状
    image_array = np.frombuffer(image_data, dtype=np.uint8).reshape(image_size)
    # 将RGB转换为BGR
    open_cv_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
    return open_cv_image


# 保存百度api识别的表格
def save_excel(b64_excel, excel_name):
    """
    :param b64_excel:b64的文件内容
    :param excel_name: 保存的文件名
    :return: 无返回
    """
    # 将base64编码的excel文件解码并保存为本地文件
    excel = base64.b64decode(b64_excel)
    with open(excel_name, 'wb') as f:
        f.write(excel)


# 整体调用百度api
def to_excel(file_path, excel_name, file_num=1):
    '''
    :param file_path:文件路径
    :param excel_name: 保存的excel名
    :param file_num: 所提取的页
    :return:
    '''
    access_token = get_token()
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/table"

    # 以二进制方式打开图片文件，并将其转换为base64编码
    with open(file_path, 'rb') as f:
        file = base64.b64encode(f.read())
    ext = file_path.split('.')[-1]
    if ext in ['jpg', 'jpeg', 'png', 'bmp']:
        # 图片格式
        data = {
            "image": file,
            "return_excel": 'true',
        }
    elif ext == 'PDF':
        # pdf格式
        data = {
            "pdf_file": file,
            "return_excel": 'true',
            "pdf_file_num": file_num
        }
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    # 发送POST请求进行表格文字识别
    response = requests.post(request_url, params={'access_token': access_token}, data=data, headers=headers)
    if response.ok:
        data = response.json()
        if data.get('table_num') > 0:
            # 将返回的excel文件保存到本地
            save_excel(data.get('excel_file', ''), excel_name)
            print('转换完成')
    else:
        print('转换失败')


# 表格检测方法一使用了fitz
def check_method_1(path, page_nums):
    '''
    :param path:路径
    :param page_nums: 提取的页数
    :return: 返回表中数据
    '''
    document_check = DocumentProcessor()
    doc = fitz.open(path)
    page = doc.load_page(page_nums)
    pix = page.get_pixmap()
    image = pix2img(pix)
    img, layout = document_check.layout_extract(image)
    data = document_check.layout_analysis(img, layout, table_flag=True)
    if len(data) != 0:
        print(data)
        return data
    return None


# 表格检测方法2使用了pdfplumber
def check_method_2(path, page_nums):
    """
    :param path: 文件路径
    :param page_nums: 提取的页数
    :return: 返回的表格数据
    """
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_nums]
        tables = page.extract_tables()
        if tables:
            print(True)
            print(tables)
            return tables
        else:
            return None


# 总的表格检测方法
def check_chart(path, page_nums, mode):
    """
    :param path: 文件的路径
    :param page_nums: 所需要检测的页
    :param mode: 所启用的检测模式
    :return: 返回的为表格数据，如果启用的为mode2则将表格数据保存为excel，返回mode_2
    """
    if mode == 0:
        return check_method_1(path, page_nums)
    elif mode == 1:
        return check_method_2(path, page_nums)
    elif mode == 2:
        to_excel(path, 'temp.xlsx', page_nums)
        return 'mode_2'


# 某一页的pdf转换为图片
def pdf2img(path, page_nums):
    """
    :param path: 文件路径
    :param page_nums: 转换页的列表
    :return: 返回转换图片的列表
    """
    all_image = []
    doc = fitz.open(path)
    for i in page_nums:
        page = doc.load_page(i)
        pix = page.get_pixmap()
        pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # 如果pix对象中的颜色空间是CMYK，转换成RGB
        if pix.colorspace.name == "CMYK":
            pixels = cv2.cvtColor(pixels, cv2.COLOR_CMYK2RGB)

        # 如果pix对象是灰阶图，扩展它成为三个通道的图像
        elif pix.n == 1:  # Grayscale
            pixels = cv2.cvtColor(pixels, cv2.COLOR_GRAY2RGB)

        # 如果pix对象是带有alpha通道(RGBA)，我们需要删除alpha通道
        elif pix.n == 4:
            pixels = cv2.cvtColor(pixels, cv2.COLOR_RGBA2RGB)
        all_image.append(pixels)
    doc.close()
    return all_image


# 通过关键词查找所有需要检测的页并进行清洗
def find_allpage(path, words, pages):
    """
    :param path: 文件路径
    :param words: 关键词列表
    :param pages: 所需要检测页的列表
    :return: 返回提取得到的文本
    """
    text_all = ''
    count = 0
    raw_text = ''
    all_page = []
    with open(path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages
        if len(pages) == 0:
            page_index = range(num_pages)
        elif pages[0] == 'index':
            if pages[1] > 0 and 0 < pages[2] < num_pages:
                page_index = range(pages[1], pages[2])
            elif pages[1] > 0 and pages[2] < 0:
                page_index = range(pages[1], num_pages + pages[2])
        else:
            page_index = pages
        for page_num in page_index:
            # 获取页面对象
            page = pdf_reader.getPage(page_num)
            # 提取当前页面的文本
            text = page.extract_text()
            text = re.sub(r'(?<! ) (?! )', '', text)
            raw_text += text
            if text:
                for word in words:  # 对于关键词的三种检测模式
                    if word == 'all':
                        count += 1
                        text_all += text + '\n'
                        all_page.append(page_num)
                    elif "&" in word:
                        word = word.split('&')
                        if word[0] in text and word[1] in text:  # 检查目标词语是否在文本中
                            count += 1
                            text_all += text + '\n'
                            all_page.append(page_num)
                    else:
                        if word in text:
                            count += 1
                            text_all += text + '\n'
                            all_page.append(page_num)
        if count >= 1:
            text_all = cleaner.clean(text_all)
            return text_all, set(all_page)
        else:
            return None, None


class TextGetorHtml:
    def __init__(self, soup, company_name):
        self.soup = soup
        self.company_name = company_name
        self.get_from_tabel_list = ["上海中期", "中泰期货", "先锋期货", "兴业期货", "通道期货", "弘业期货", "宏源期货"]

    def get_text_from_table(self):
        table_list = extract_tables_from_html(self.soup)
        return concatenate_dataframes(table_list[0])

    def get_text_from_texts(self):
        return self.soup.get_text()

    def get_texts(self):
        if self.company_name not in self.get_from_tabel_list:
            return self.get_text_from_texts()
        elif self.company_name == "华融融达":
            return None
        else:
            return self.get_text_from_table()


# 从html中提取表格
def extract_tables_from_html(soup):
    """
    :param soup:HTMl的soup解析
    :return: 返回表格中的内容
    """
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


def extract_times(text):
    # 定义正则表达式模式，匹配年份、任意字符、月份、任意字符和日期
    date_pattern = r'(2024)(.{1})(\d{1,2})(.{1})(\d{1,2})'
    # 使用re.findall来查找所有匹配的日期
    matches = re.findall(date_pattern, text)
    # 将匹配的结果格式化为日期字符串
    dates = ["{}{}{}{}{}".format(year, '/', month, '/', day) for year, _, month, __, day in matches]
    return dates[0]


def get_times(content, type):
    extractor = DataExtractor()
    content = extractor.decode(content, type)
    if type == "html":
        return extract_times(str(content))
    else:
        return extract_times(content.replace('\n', '').replace(' ', ''))


# 拼接表
def concatenate_dataframes(df, separator=","):
    """
    :param df: 输入的数据dataframe
    :param separator:分隔符
    :return:进行分割拼接后的数据
    """
    result = []
    for row in df.itertuples(index=False, name=None):  # 去掉表头，并且每行作为元组
        row_str = separator.join(map(str, row))  # 将每个元素转为字符串并用分隔符拼接
        result.append(row_str)
    return "|".join(result)  # 每行之间用换行符分隔
if __name__=="__main__":
    with open("E:\curriculums\data\\no_chart\华安期货\华安期货_233493_2.html", 'r', encoding='UTF-8') as f:
        html_content = f.read()
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    extract_times(str(soup))