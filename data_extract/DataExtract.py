import pandas as pd
import PyPDF2
from bs4 import BeautifulSoup
import shutil
import pdfplumber
import os
from tqdm import tqdm
import tempfile
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = [u'simHei']  # 显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决负号问题
from paddleocr import PaddleOCR
import cv2
import layoutparser as lp
class DataExtractor:
    def __init__(self, path=None):
        if path is not None:
            self.paths = self._get_paths(path)

    def _get_paths(self, base_path):
        """
        获取指定基础路径下所有文件的路径。
        :param base_path: 基础路径，例如 'datas' 在工作目录下的路径
        :return: 包含所有文件路径的列表
        """
        file_paths = []
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths

    def extract_PDF(self, path):
        with open(path, 'rb') as pdf_bin_file:
            binary_data = pdf_bin_file.read()
        return binary_data

    def extract_html(self, path):
        with open(path, 'rb') as html_file:
            binary_data = html_file.read()
        return binary_data

    def decode_html(self, binary_html):
        html_content = binary_html.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def decode_PDF(self,binary_pdf):
        all_text=""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(binary_pdf)
                temp_file_path = temp_file.name
            # 打开临时文件并读取内容
            with open(temp_file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                # 检查PDF文件是否损坏
                if pdf_reader.isEncrypted:
                    pdf_reader.decrypt('')  # 尝试解密
                num_pages = pdf_reader.getNumPages()

                # 遍历每一页并提取文本
                for page_num in range(num_pages):
                    page = pdf_reader.getPage(page_num)
                    page_text = page.extract_text()
                    all_text += page_text
            # 删除临时文件
            os.remove(temp_file_path)
            return all_text
        except PyPDF2.utils.PdfReadError as e:
            return f"Error reading PDF file: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def decode(self, content, type):
        decode_method_name = f"decode_{type}"
        if hasattr(self, decode_method_name):
            extract_method = getattr(self, decode_method_name)
            content = extract_method(content)
            return content
        else:
            raise ValueError(f"No decoding method defined for {type}")

    def extract(self, path):
        file_type = path.split(".")[-1]
        extract_method_name = f"extract_{file_type}"
        if hasattr(self, extract_method_name):
            extract_method = getattr(self, extract_method_name)
            content = extract_method(path)
            return content, file_type
        else:
            raise ValueError(f"No extraction method defined for {file_type}")
    def get_company(self):
        """
         获取所有公司的名称，储存在一个txt中
         """

        all_data=[self.spilt_company_name(path) for path in self.paths]
        with open('company.txt', 'w', encoding='utf-8') as f:
            for i in set(all_data):
                f.write(f'{i}\n')
    def get_name_and_type(self,path):
        """
         获取完整路径的文件名称和扩展名称
         :param path:例如"E:\curriculums\datas\20240302\保诚期货_210098.PDF"
         :return: 文件名称和扩展，例如返回：保诚期货_210098，.PDF
         """
        file_name = os.path.basename(path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        return file_name_without_extension, file_extension

    def spilt_company_name(self,path):
        filename, file_extension = self.get_name_and_type(path)
        company_name = filename.split("_")[0]
        return company_name
    def check_chart(self):
        """
        检测路径中的文件是否包含表格，并将包含表格的文件路径保存到 chart.txt 文件中。
        """
        all_data = []
        for file_path in tqdm(self.paths):
            try:
                if 'PDF' in file_path:
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            tables = page.extract_tables()
                            if tables:
                                all_data.append(file_path)
                                break
                elif 'html' in file_path:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    tables = soup.find_all('table')
                    if tables:
                        all_data.append(file_path)
            except:
                continue
        with open('chart.txt', 'w', encoding='utf-8') as f:
            for file_path in set(all_data):
                f.write(f'{file_path}\n')
        return all_data
def DataTempStore(directory_path):
    extractor = DataExtractor(directory_path)
    df = pd.DataFrame(columns=["filename", "content", "filetype"])
    for path in extractor.paths:
        try:
            content, _ = extractor.extract(path)
            filename, filetype = extractor.get_name_and_type(path)
            df = df.append({"filename": filename, "content": content, "filetype": filetype}, ignore_index=True)
        except ValueError as e:
            print(e)
    return df
def plot_png(company, values, name):
    # 按顺序设置 x 位置
    x_positions = range(len(company))
    # 设置图的大小，根据真实情况调整 figsize 参数
    plt.figure(figsize=(20, 7))  # 这里设置宽度大一些
    # 绘制条形图；条形宽度设置得较小，如：width=0.8
    plt.bar(x_positions, values, width=0.8, tick_label=company)
    # 旋转 x 轴标签以避免文本重叠
    plt.xticks(rotation=90)  # 将标签旋转成垂直方向
    # 添加额外的样式参数，如间隔、对齐等
    plt.tight_layout()  # 自动调整子图参数，使之填充整个图像区域
    # 给图表添加标题和轴标签
    plt.title('Companies Statisics')
    plt.xlabel('Company')
    plt.ylabel('Value')
    # 展示图表
    plt.gcf().set_size_inches(20, 7)
    plt.savefig(name + '_plot.png', dpi=300, bbox_inches='tight', transparent=False)
    plt.clf()
# 将无表格的和有表格的分类
def classify(path):
    try:
        if not os.path.exists('chart/'):
            os.mkdir('chart/')
        if not os.path.exists('no_chart/'):
            os.mkdir('no_chart/')
    except:
        print('error')
    try:
        with open('company.txt', 'r', encoding='utf-8') as f:
            company = f.readlines()
        for i in range(len(company)):
            company[i] = company[i].replace('\n', '')
        for i in range(len(company)):
            if not os.path.exists('chart/' + company[i]):
                os.mkdir('chart/' + company[i])
            if not os.path.exists('no_chart/' + company[i]):
                os.mkdir('no_chart/' + company[i])
    except:
        print('error')
    extract=DataExtractor(path)
    file_paths =extract.paths
    with open('chart.txt', 'r', encoding='utf-8') as file:
        all_file = file.readlines()
    for i in range(len(all_file)):
        all_file[i] = all_file[i].replace('\n', '')

    chart_values = [0] * len(company)
    no_chart_values = [0] * len(company)

    for i in file_paths:
        if 'PDF' not in i and 'html' not in i:
            continue
        file_name = (i.split('\\'))[len(i.split('\\')) - 1]
        print(file_name)
        if i in all_file:
            shutil.copy2(i, 'chart/' + file_name.split('_')[0] + '/' + file_name)
            chart_values[company.index(file_name.split('_')[0])] += 1
        else:
            shutil.copy2(i, 'no_chart/' + file_name.split('_')[0] + '/' + file_name)
            no_chart_values[company.index(file_name.split('_')[0])] += 1
    plot_png(company, chart_values, 'chart')
    plot_png(company, no_chart_values, 'no_chart')
def delete_corrupt_pdfs(file_paths):
    """
    检查列表中的 PDF 文件是否损坏，并删除损坏的文件。
    :param file_paths: 包含 PDF 和 HTML 文件路径的列表
    :return: 删除的损坏 PDF 文件数量
    """
    extractor=DataExtractor()
    corrupt_files = []
    corrupt_count = 0
    try:
        with open('company.txt', 'r', encoding='utf-8') as f:
            company = [line.strip() for line in f.readlines()]
            company_dict = {company_name: 0 for company_name in company}
    except:
        print('error')
    for file_path in file_paths:
        company_name=extractor.spilt_company_name(file_path)
        if file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                    if pdf_reader.isEncrypted:
                        pdf_reader.decrypt('')
                    pdf_reader.getNumPages()
            except Exception as e:
                print(f"File {file_path} is corrupt: {e}")
                corrupt_files.append(file_path)
                company_dict[company_name]+=1
                corrupt_count += 1

    for file_path in corrupt_files:
        try:
            os.remove(file_path)
            print(f"Deleted corrupt file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    values=list(company_dict.values())
    plot_png(company,values,"invalid PDFs")
    print(f"Total corrupt PDF files deleted: {corrupt_count}")
    return corrupt_count

# ocr 识别图片



class DocumentProcessor:
    def __init__(self, ocr_lang='ch'):
        self.ocr = PaddleOCR(use_angle_cls=True, lang=ocr_lang)
        self.model = lp.PaddleDetectionLayoutModel(
            config_path="lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet/config",
            threshold=0.3,
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
            enforce_cpu=False,
            enable_mkldnn=True
        )

    def ocr_extract(self, img):
        text = []
        raw_data = []
        result = self.ocr.ocr(img, cls=True)
        for idx in range(len(result)):
            res = result[idx]
            if res is not None:
                for line in res:
                    text.append(line[1])
                    raw_data.append(line)
        return text, raw_data

    def layout_extract(self, image):
        img = image[..., ::-1]
        layout = self.model.detect(image)
        return img, layout

    def layout_analysis(self, img, layout, table_flag=False, text_flag=False, figura_flag=False):
        all_text = []
        try:
            for block in layout:
                if table_flag and block.type == "Table":
                    x1, y1, x2, y2 = map(int, block.coordinates)
                    segment_image = img[y1:y2, x1:x2]
                    text, raw_data = self.ocr_extract(segment_image)
                    all_text.append(text)
                elif text_flag and block.type == "Text":
                    x1, y1, x2, y2 = map(int, block.coordinates)
                    segment_image = img[y1:y2, x1:x2]
                    text, raw_data = self.ocr_extract(segment_image)
                    all_text.append(text)
                elif figura_flag and block.type == "Figure":
                    x1, y1, x2, y2 = map(int, block.coordinates)
                    segment_image = img[y1:y2, x1:x2]
                    text, raw_data = self.ocr_extract(segment_image)
                    all_text.append(text)
        except Exception as e:
            print('数据错误:', e)
        return all_text


# Example usage:
# processor = DocumentProcessor()
# img = cv2.imread('path_to_image')
# img, layout = processor.layout_extract(img)
# extracted_text = processor.layout_analysis(img, layout, table_flag=True, text_flag=True, figura_flag=True)

if __name__ == "__main__":
    extract=DataExtractor('E:\curriculums\datas')
    delete_corrupt_pdfs(extract.paths)
    extract.get_company()
    extract.check_chart()
    classify('E:\curriculums\datas')


