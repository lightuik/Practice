import PyPDF2
import os
import numpy as np
from openai import OpenAI
import re
import yaml


def is_positive_integer(judge):
    try:
        # 尝试将字符串转换为整数
        return abs(int(judge)) >= 0
    except ValueError:
        # 无法转换为整数（可能是浮点数或包含非数字字符）
        return False


class BuildKeyword:
    def __init__(self, config_yaml):
        self.keyword = []
        self.keyword_label = []
        with open(config_yaml, 'r', encoding='utf-8') as file:
            params = yaml.safe_load(file)
        self.path = params['path']
        self.data_path = os.listdir(self.path)
        self.api_key = params['api_key']
        self.base_url = params['base_url']
        self.rules = params['rules']
        build_flag = params['build_flag']
        if build_flag:
            self.build()

    # 大模型提取
    def chat(self, text):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"{self.rules}"},
                {"role": "user", "content": text},
            ],
            stream=False,
            temperature=0.7  # 0.7更加偏向信息的提取
        )
        raw_data = response.choices[0].message.content
        datas = raw_data.split(',')
        try:
            for i in datas:
                pattern = r'\((.*?)\)'
                matches = re.findall(pattern, i)
                match = matches[0].split(':')
                if '期货策略' in i:
                    self.keyword.extend(match)
                    self.keyword_label.extend(['期货策略'] * len(match))
                elif '产品状况' in i:
                    self.keyword.extend(match)
                    self.keyword_label.extend(['产品状况'] * len(match))
        except Exception as e:
            print(f'数据解析失败:{e}')
        print(raw_data)
        return raw_data

    def build(self):
        # 路径的遍历
        for i in range(len(self.data_path)):
            if 'PDF' in self.data_path[i]:
                try:
                    with open(self.path + '/' + self.data_path[i], 'rb') as file:
                        pdf_reader = PyPDF2.PdfFileReader(file)
                        num_pages = len(pdf_reader.pages)
                        print(f"Total pages: {num_pages}")
                        if num_pages >= 4:
                            num_pages = int(num_pages / 2)
                        for j in range(num_pages - 1):
                            page = pdf_reader.pages[j]
                            text = page.extract_text()
                            text = text.replace('，', ' ')
                            text = text.replace('。', ' ')
                            _ = self.chat(text)
                except:
                    continue
        # 提取对应关键词
        keyword = np.array(self.keyword)
        keyword_label = np.array(self.keyword_label)
        strategy = keyword[np.where(keyword_label == '期货策略')]
        state = keyword[np.where(keyword_label == '产品状况')]
        # 清洗大语言模型中的特殊情况
        for i in range(len(strategy)):
            if '等' in str(strategy[i]):
                strategy[i] = strategy[i].replace('等', '')
        for i in range(len(state)):
            if '等' in str(state[i]):
                state[i] = state[i].replace('等', '')
        # 去重
        strategy = set(strategy)
        state = set(state)
        # 数据保存为两个文件
        with open('stragery.txt', 'w', encoding='utf-8') as file:
            for item in set(strategy):
                file.write(f"{item}\n")
        with open('state.txt', 'w', encoding='utf-8') as file:
            for item in set(state):
                if not isinstance(item, (int, float)):
                    if not is_positive_integer(item):
                        file.write(f"{item}\n")


if __name__ == "__main__":
    BuildKeyword(config_yaml='config.yaml')
