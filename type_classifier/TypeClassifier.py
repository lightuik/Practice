import requests
from openai import OpenAI
import yaml


# http://101.227.51.107:7112/AlAnalvsis/ReportAnalvsis/GetAnalysis
class TypeClassifier:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            params = yaml.safe_load(file)
        self.api_key = params['api_key']
        self.base_url = params['base_url']
        self.rules = params['rules']
        self.temperature = params['temperature']

    def norm_chat(self, text):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        if self.temperature is not None:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{self.rules}"},
                    {"role": "user", "content": text},
                ],
                stream=False,
                temperature=self.temperature  # 0.7 更加偏向信息的提取
            )
        else:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"{self.rules}"},
                    {"role": "user", "content": text},
                ],
                stream=False,
            )
        raw_data = response.choices[0].message.content
        return raw_data

    def expert_chat(self, text, class_type):
        params = {
            'content': text,
            'type': class_type
        }
        response = requests.post('http://101.227.51.107:7112/AIAnalysis/ReportAnalysis/GetAnalysis', data=params)
        count = 0
        while response.status_code != 200 and count < 4:
            count += 1
            response = requests.post('http://101.227.51.107:7112/AIAnalysis/ReportAnalysis/GetAnalysis', data=params)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None

    def predict(self, **kwargs):
        try:
            if kwargs['mode'] == 0:
                print('norm')
                return self.norm_chat(text=kwargs['text'])
            elif kwargs['mode'] == 1:
                print('expert')
                return self.expert_chat(text=kwargs['text'], class_type=kwargs['class_type'])
            else:
                print('不合法参数')
        except:
            print('传入参数有误')
            return None


if __name__ == "__main__":
    model = TypeClassifier(config_path='config.yaml')
    print(model.predict(mode=1, text='【铜】美国2月Markit制造业PMI超预期，为近17个月新'
                                     '高，1月成屋销售创近一年来最大增幅。盘面偏强，但节后下游需求恢复缓慢，现货成交有限，仍贴'
                                     '水期货。美联储官员再为降息预期降温，警告通胀改善仍不能过度宽松。美国经济数据偏强，铜价向上攀升'
                                     '，降息预期被降温，上方有限，沪铜03预计仍于67000-70000元/吨震荡。', class_type=1))
