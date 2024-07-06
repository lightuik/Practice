import requests
from openai import OpenAI
import yaml


# http://101.227.51.107:7112/AIAnalysis/ReportAnalysis/GetAnalysis
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
                stream=False
            )
        raw_data = response.choices[0].message.content
        return raw_data

    def expert_chat(self, text, class_type):
        params = {
            'content': text,
            'type': class_type
        }
        response = requests.post('http://101.227.51.107:7112/AIAnalysis/ReportAnalysis/GetAnalysis', json=params)
        count = 0
        while response.status_code != 200 and count < 4:
            count += 1
            response = requests.post('http://101.227.51.107:7112/AIAnalysis/ReportAnalysis/GetAnalysis', json=params)
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
        except Exception as e:
            print('传入参数有误:', e)
            return None


if __name__ == "__main__":
    model = TypeClassifier(config_path='config.yaml')
    print(model.predict(mode=1, text='铜价格将继续受到降息预期以及避险情绪的影响', class_type=0))
