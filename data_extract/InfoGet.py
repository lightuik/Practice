from data_extract.DataExtract import  DataExtractor
from type_classifier.TypeClassifier import TypeClassifier
from utils import TextGetorHtml
import yaml
from DataExtract import DocumentProcessor
import os
from utils import find_allpage, pdf2img, check_chart, get_times
import PyPDF2
from bs4 import BeautifulSoup
""" 
all_params_pdf 参数解释
"宝城期货": {'keyword': ['核心观点'], "pages": [], "chart": None, "distance": 15}
keyword为文章中关键句部分的关键词，如果为all则代表没有关键字，如果为NONE启用表格搜索
pages为需要搜索的页数，可以是离散的1,2,3，也可以是连续的，连续的如下
["index",1,8]:从2到8页
["index“,1,-2]从2到最后一页减去2
chart:代表文本中是否存在表格
如果一个文本既有关键字又有表格且在表格页提取到的结果无法得到预测，则使用True代表启用
distance代表表格之间段落合并的距离，即离的有多近可以合并为一段。
"""


class InformationExtractor:
    def __init__(self, use_config=False):
        self.extractor = DataExtractor()
        self.model = TypeClassifier("config.yaml")
        # 是否启用参数配置
        if use_config:
            with open("feature.yaml", 'r', encoding='utf-8') as file:
                self.all_params_pdf = yaml.safe_load(file)
        else:
            self.all_params_pdf = {
                "宝城期货": {'keyword': ['核心观点'], "pages": [], "chart": None, "distance": 15},
                "山金期货": {'keyword': ['操作建议'], "pages": [], "chart": None, "distance": 15},
                "格林大华": {'keyword': ['建议'], "pages": [], "chart": None, "distance": 15},
                "瑞达期货": {'keyword': ['策略'], "pages": [], "chart": None, "distance": 15},
                "大越期货": {'keyword': ['预期'], "pages": [], "chart": None, "distance": 15},
                "广州期货": {'keyword': ['观点&建议'], "pages": [], "chart": None, "distance": 15},
                "广金期货": {'keyword': ['核心观点', '摘要'], "pages": [], "chart": None, "distance": 15},
                "西南期货": {'keyword': ['all'], "pages": [], "chart": None, "distance": 15},
                "金信期货": {'keyword': ['all'], "pages": [], "chart": None, "distance": 15},
                "金石期货": {'keyword': ['展望', '策略'], "pages": [], "chart": None, "distance": 15},
                "铜冠金源": {'keyword': ['预期', '操作建议'], "pages": [], "chart": None, "distance": 15},
                "长安期货": {'keyword': ['小结', '结论', '操作思路'], "pages": [], "chart": None, "distance": 15},
                "长江期货": {'keyword': ['分析'], "pages": [], "chart": None},
                "宏源期货": {'keyword': ['小结', '结论', '策略'], "pages": [], "chart": None, "distance": 15},
                "国联期货": {'keyword': ['观点', '展望', '推荐策略', '策略', '影响因素', '摘要'], "pages": [], "chart": 1, "distance": 15},
                "国金期货": {'keyword': ['all'], "pages": [], "chart": None, "distance": 15},
                "弘业期货": {'keyword': ['核心观点'], "pages": [], "chart": None, "distance": 15},
                "浙江新世纪": {'keyword': ['all'], "pages": [], "chart": None, "distance": 15}
            }
        self.document_check = DocumentProcessor()
        # 存储在yaml文件中，后期完成后将不会在类内修改
        with open('feature.yaml', 'w+', encoding='utf-8') as file:
            yaml.dump(self.all_params_pdf, file)

    # 解析html
    def parser_html(self, data_path):
        """
        :param content: 输入的文本，为二进制
        :param file_type: 输入的文件类型为html
        :param company_name: 输入的所属的公司
        :return: 返回预测结果
        """
        all_paths=self.extractor._get_paths(data_path)
        all_results=[]
        for path in all_paths:
            try:
                with open(path, 'r',
                          encoding='UTF-8') as f:
                    html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')
            except:
                continue
            filename,_=self.extractor.get_name_and_type(path)
            company_name = self.extractor.spilt_company_name(path)
            info_getor = TextGetorHtml(soup, company_name)
            texts = info_getor.get_texts()
            predict = self.model.predict(mode=1, text=texts, class_type=0)
            print(predict)
            try:
                time = get_times(self.extractor.extract(path)[0], "html")
            except:
                print(path)
                time=path
            result={"filename":filename,"content":self.extractor.extract(path),"predict":predict,"filetype":"html","time":time}
            all_results.append(result)
        return all_results

    # 解析pdf
    def parser_pdf(self, path):
        """
        :param path: 输入的为chart和no_chart所在的路径
        :return: 返回预测结果为一个列表，列表中的每个元素为{"filename": i, "content": content_binary, "predict": set(all_result),
                                           "filetype": "PDF"
                                , "time": time}
        """
        data_dir = os.listdir(path)
        all_consequence = []
        # 遍历文件
        for keys in data_dir:
            # 判断是否已经有对应的处理关键字
            if keys in self.all_params_pdf.keys():
                # 找到路径
                for i in os.listdir(path + "\\" + keys):
                    # 检测是否为PDF
                    if 'PDF' in i:
                        # 启用关键字搜索
                        content_binary, file_type = self.extractor.extract(path + "\\" + keys + '\\' + i)
                        try:
                            time = get_times(content_binary, "PDF")
                        except:
                            print(path)
                            time = path
                        if self.all_params_pdf[keys]['keyword'] is not None:
                            # 使用find_allpage的方式查找关键字所在页
                            text, all_page = find_allpage(path + "\\" + keys + '\\' + i,
                                                          words=self.all_params_pdf[keys]['keyword'],
                                                          pages=self.all_params_pdf[keys]['pages'])
                            # 如果返回的文本不是没有则预测，有些时候文本没有说明关键字不准确
                            if text is not None:
                                result = self.model.predict(mode=1, text=text.replace(' ', ''), class_type=0)
                                # model返回的为字符串，如果为空时长度为2，检测是否为空
                                if len(result) != 2:
                                    consequence={"filename": i, "content": content_binary, "predict": result,"filetype":"PDF"
                                     ,"time": time}
                                    all_consequence.append(consequence)
                                # 如果为空说明可能其中有表格没提取到，那么便对含有关键词的页启用表格查找
                                if self.all_params_pdf[keys]['chart'] and len(result) == 2:
                                    # 将表格转化为图像格式
                                    image = pdf2img(os.path.join(path,keys,i), all_page)
                                    # 遍历所有表格图像
                                    all_result = []
                                    for img in image:
                                        # 合并相邻的表格文本
                                        chart_text = self.document_check.ocr_extract_merge(img, distance=
                                        self.all_params_pdf[keys][
                                            'distance'])
                                        # 分隔符送入模型
                                        separator = ':'
                                        text = separator.join(str(x) for x in chart_text)
                                        result = self.model.predict(mode=1, text=text.replace(' ', ''), class_type=0)
                                        all_result.append(result)
                                    # 有些表格可能在描述同一件事，可能得到同一个结果，因此使用集合去除重复
                                    consequence={"filename": i, "content": content_binary, "predict": set(all_result),"filetype":"PDF"
                                     ,"time": time}
                                    all_consequence.append(consequence)
                            else:
                                print(i)  # 定位关键字不正确的文本
                        else:  # 启动表格搜素方式v
                            with open(os.path.join(path, keys, i), 'rb') as file:
                                reader = PyPDF2.PdfFileReader(file)
                                num_pages = reader.numPages
                            pages = self.all_params_pdf[keys]['pages']
                            # 表格参数的检测，如果长度为0说明查所有页，如果第一个为index，第二个和第三个为数字，说明查之间所有页，
                            # 若最后一个数字为负则从最后一页加上负为终止
                            if len(pages) == 0:
                                page_index = range(num_pages)
                            elif pages[0] == 'index' and pages[1] > 0 and 0 < pages[2] < num_pages:
                                page_index = range(pages[1], pages[2])
                            elif pages[0] == 'index' and pages[1] > 0 and pages[2] < 0:
                                page_index = range(pages[1], num_pages + pages[2])
                            else:
                                page_index = range(num_pages)
                            all_result = []
                            for j in page_index:
                                chart_text = check_chart(os.path.join(path, keys, i), j, mode=1)
                                separator = ':'
                                text = separator.join(str(x) for x in chart_text)
                                result = self.model.predict(mode=1, text=text.replace(' ', ''), class_type=0)
                                all_result.append(result)
                            # 有些表格可能在描述同一件事，可能得到同一个结果，因此使用集合去除重复
                            consequence = {"filename": i, "content": content_binary, "predict": set(all_result),
                                           "filetype": "PDF"
                                , "time": time}
                            all_consequence.append(consequence)
        return all_consequence


if __name__ == "__main__":
    info_extractor = InformationExtractor()
    info_extractor.parser_pdf("E:\curriculums\data\chart")
