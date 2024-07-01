from data_extract.DataExtract import DataExtractor
import re
import jieba

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
    text, document_type = extract.extract('华融融达_211217.PDF')
    # text, document_type = extract.extract('道通期货_210800_0.html')
    print(document_type)
    decode_document = extract.decode(text, document_type)
    cleaned_text = None
    with open('stragery.txt', 'r', encoding='utf-8') as file:
        stragery = file.readlines()
    with open('products.txt','r',encoding='utf-8') as file:
        product = file.readlines()
    for i in range(len(stragery)):
        stragery[i] = stragery[i].replace('\n', '')
    for i in range(len(product)):
        product[i] = product[i].replace('\n', '')
    print(product)
    keyword_stragery = re.compile(r'([^。]*\b(?:' + '|'.join(map(re.escape, stragery)) + r')\b[^。]*。)')
    keyword_product = re.compile(r'([^。]*\b(?:' + '|'.join(map(re.escape, product)) + r')\b[^。]*。)')
    if document_type == 'html':
        # print(decode_document)
        text_all = decode_document.get_text()
        cleaned_text = re.sub(r'\n\s*\n', ' ', text_all)
        # print(cleaned_text)
    elif document_type == 'PDF':
        cleaned_text = re.sub(r'\n\s*\n', ' ', decode_document)
        # print(cleaned_text)
    key_sentences = keyword_stragery.findall(cleaned_text)
    key_sentences_product = keyword_product.findall(cleaned_text)

    for sentence in key_sentences:
        print(sentence)
    for sentence in key_sentences_product:
        print('product:')
        print(sentence)
