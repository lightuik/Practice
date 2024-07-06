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
                stream=False,
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
        except:
            print('传入参数有误')
            return None


if __name__ == "__main__":
    model = TypeClassifier(config_path='config.yaml')
    print(model.predict(mode=1, text='上周双焦震荡盘整。需求端，螺纹钢表需恢复尚可，但热卷受高库存压制，需求恢复缓慢，铁水产量小幅回落，短期压制双焦需求，但3月随着复产推进，需求仍有好转预期。供给端，焦企面对亏损采取减产策略，焦煤关于供给扰动的消息较多，但部分被证伪，上周焦煤产量小幅增加，目前处在煤矿复产期，焦煤供给稳中偏强运行。供需博弈，后市发展还需关注成材表需变动情况', class_type=0))

