import pandas as pd
import PyPDF2
from bs4 import BeautifulSoup
import os
import tempfile


class DataExtractor:
    def __init__(self, path):
        self.paths = self._get_paths(path)

    def _get_paths(self, base_path):
        """
        获取指定基础路径下所有文件的路径。
        :param base_path: 基础路径，例如 'datas' 在工作目录下的路径
        :return: 包含所有文件路径的列表
        """
        file_paths = []

        # 遍历基础路径下的所有文件和文件夹
        for root, _, files in os.walk(base_path):
            # 拼接文件的完整路径并添加到列表中
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

    def decode_PDF(self, binary_pdf):
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
            # 删除临时文件
            os.remove(temp_file_path)
            return pdf_reader
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
            return content
        else:
            raise ValueError(f"No extraction method defined for {file_type}")


def get_name_and_type(path):
    file_name = os.path.basename(path)
    file_name_without_extension, file_extension = os.path.splitext(file_name)
    return file_name_without_extension, file_extension


def DataTempStore(directory_path):
    extractor = DataExtractor(directory_path)
    df = pd.DataFrame(columns=["filename", "content", "filetype"])
    for path in extractor.paths:
        try:
            content = extractor.extract(path)
            filename, filetype = get_name_and_type(path)
            df = df.append({"filename": filename, "content": content, "filetype": filetype}, ignore_index=True)
        except ValueError as e:
            print(e)
    return df


if __name__ == "__main__":
    DataTempStore("datas")
