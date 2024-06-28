from data_extract.DataExtract import DataExtractor
from bs4 import BeautifulSoup
import re

# 数据清晰模块
class DataClean:
    def __init__(self):
        pass

    def data_preparation(self, text):
        pass

    def keyword_extract(self, text):
        pass

    def time_extract(self):
        pass

    def state_extract(self):
        pass

    def product_extract(self):
        pass

    def clean(self, text):
        return


if __name__ == "__main__":
    extract = DataExtractor()
    soup = BeautifulSoup(extract.extract('道通期货_210800_0.html').decode('utf-8'), 'html.parser')
    print(soup)
    text_all = soup.get_text()
    cleaned_text = re.sub(r'\n\s*\n', ' ', text_all)
    print(cleaned_text)
