from data_extract.DataExtract import DataExtractor
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
    text, document_type = extract.extract('宝城期货_210704.PDF')
    # text, document_type = extract.extract('道通期货_210800_0.html')
    print(document_type)
    decode_document = extract.decode(text, document_type)
    if document_type == 'html':
        print(decode_document)
        text_all = decode_document.get_text()
        cleaned_text = re.sub(r'\n\s*\n', ' ', text_all)
        print(cleaned_text)