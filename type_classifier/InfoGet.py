from TypeClassifier import TypeClassifier
from data_extract.DataExtract import DataTempStore, DataExtractor
from bs4 import BeautifulSoup
from utils import extract_tables_from_html,concatenate_dataframes,TextGetorHtml

class InformationExtractor:
    def __init__(self):
        self.extractor = DataExtractor()
        self.model = TypeClassifier("config.yaml")

    def parser(self, content, file_type,company_name):
        if file_type == 'html':
            content = self.extractor.decode(content, file_type)
            info_getor=TextGetorHtml(content,company_name)
            texts = info_getor.get_texts()
        else: # text = content

            return
        result=self.model.predict(mode=1, text=texts,class_type=0)
        print(result)
        return result
if __name__ == "__main__":
    info_extractor = InformationExtractor()
    df = DataTempStore("../data_extract/chart")
    df["classification"] = df.apply(lambda row: info_extractor.parser(row["content"], row["filetype"],row['filename'].split("_")[0]), axis=1)
    print(df["classification"])




