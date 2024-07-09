from pymysql import OperationalError
import pymysql
from data_extract.InfoGet import InformationExtractor
import json
from datetime import datetime


class DataManager:
    """
        完成数据的增删改查
    """

    def __init__(self):
        self.connection = pymysql.Connection(host='DESKTOP-7QS042B', user='root', password='123456',
                                             database='webstock_guest',
                                             port=3306)
        self.cursor = self.connection.cursor()
        self.query = None
        self.all_tables = []

    def tables_query(self):
        self.query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'webstock_guest'"
        self.cursor.execute(self.query)
        self.all_tables = list(self.cursor.fetchall())
        return self.all_tables

    def set_data(self, id, **kwargs):  # 修改
        for key, value in kwargs.items():
            print(key, value)
            try:
                self.query = f"UPDATE redis SET {key}='{value}' WHERE id={id}"
                self.cursor.execute(self.query)
                self.connection.commit()
            except OperationalError:
                pass

    def insert_data(self, **kwargs):  # 插入
        table_name = kwargs.pop('table_name')  # 先移除并获取table_name
        columns = ', '.join(f"`{key}`" for key in kwargs.keys())  # 使用剩余的kwargs
        placeholders = ', '.join(['%s'] * len(kwargs))
        values = tuple(kwargs.values())
        self.query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(self.query, values)
            self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"An error occurred: {e}")

    def search_data(self, keyword):  # 查找
        self.query = f"SELECT filename FROM binary_code WHERE filename LIKE '{keyword}%'"
        try:
            self.cursor.execute(self.query)
            outcome = self.cursor.fetchall()
            documents_list = [document[0] for document in outcome]
            return documents_list
        except:
            return None
    def search_content(self, keyword):  # 查找
        self.query = f"SELECT binary_content FROM binary_code WHERE filename = '{keyword}'"
        try:
            self.cursor.execute(self.query)
            outcome = self.cursor.fetchone()
            return outcome[0]
        except:
            return None
    def delete(self, id):  # 删
        self.query = f"DELETE  from redis WHERE id={id}"
        self.cursor.execute(self.query)
        self.connection.commit()

    def id_MAX_Get(self, table_name):
        self.query = f"SELECT MAX(id) AS max_id FROM {table_name};"
        self.cursor.execute(self.query)
        outcome_id = self.cursor.fetchone()
        if outcome_id[0] is not None:
            return outcome_id
        else:
            return 0

    def filenames_Get(self):
        self.query = "SELECT filename from binary_code"
        self.cursor.execute(self.query)
        file_names = list(self.cursor.fetchall())
        print(file_names)
        if len(file_names) != 0:
            return [item[0] for item in file_names]
        else:
            return []
    def Creat_New_table(self, table_name):
        # 创建一个和样表结构相同的表
        self.query = f"CREATE TABLE {table_name} LIKE exemplify_table;"
        self.cursor.execute(self.query)
        self.connection.commit()
        print(f"存储{table_name}的表创建成功!")

    def score_Get(self, score_x_dict, query_outcome):
        # 更新得分映射字典
        score_predict_dict = {'多': 4, '震荡': 3, '空': 2, '无法预知': 1}

        for data in query_outcome:
            if len(data) == 5:  # 确认数据合法性
                product_name = data[1]
                strategy = data[2]
                time = data[4]
                score = score_predict_dict.get(strategy, 0)
                score_x_dict[product_name].append((score, time))
        return score_x_dict

    def enterprise_product_predict(self, enterprise_name, product_name):
        self.query = f"""
         SELECT LEFT(filename, 4) AS enterprise_name, product_name, current_strategy, COUNT(*) AS predict_category, time 
         FROM redis 
         WHERE LEFT(filename, 4) = '{enterprise_name}' AND product_name = '{product_name}'
         GROUP BY enterprise_name, product_name, current_strategy, time;
         """
        self.cursor.execute(self.query)
        query_outcome = self.cursor.fetchall()
        return query_outcome

    def evaluate_enterprises_predictions(self, enterprise_names, product_names):
        predict_lists = []
        time_line_list = []

        for enterprise_name in enterprise_names:
            enterprise_predict_list = []
            enterprise_time_list = []
            for product_name in product_names:
                query_outcome = self.enterprise_product_predict(enterprise_name, product_name)
                score_dict = {product_name: []}
                scored_outcome = self.score_Get(score_dict, query_outcome)

                scores = [score[0] for score in scored_outcome[product_name]]
                times = [score[1] for score in scored_outcome[product_name]]

                enterprise_predict_list.append(scores)
                enterprise_time_list.append(times)
            predict_lists.append(enterprise_predict_list)
            time_line_list.append(enterprise_time_list)

        return predict_lists, time_line_list


if __name__ == "__main__":
    DataManager_get = DataManager()
    ##############PDF提取#################
    info_extractor = InformationExtractor()
    id_max = DataManager_get.id_MAX_Get('redis')
    all_tables = DataManager_get.tables_query()  # 查询所有的表格
    tables_list = [item[0] for item in all_tables]
    filename_list = DataManager_get.filenames_Get()
    consequence_dict = info_extractor.parser_pdf('C:/Users/25338/PycharmProjects/webstockGuise/chart')
    for file_data in consequence_dict:
        file_name = file_data['filename']
        datas = json.loads(file_data['predict'])
        file_binary_content = file_data['content']
        Binary_content = file_data['content']
        if file_name not in filename_list:
            filename_list.append(file_name)
            id_max_filename_table = 1 if DataManager_get.id_MAX_Get('binary_code')==0 else \
                DataManager_get.id_MAX_Get('binary_code')[0]+1
            DataManager_get.insert_data(table_name='binary_code', id=id_max_filename_table,
                                        filename=file_name, binary_content=Binary_content)

        try:
            file_time = datetime.strptime(file_data['time'], "%Y/%m/%d")
        except Exception as e:
            pass
        file_method = file_data['filetype']
        for data in datas:
            # 将数据存入大表
            try:
                DataManager_get.insert_data(table_name='redis', id=id_max, product_name=data['name'],
                                            time=file_time.strftime('%Y-%m-%d'), current_strategy=data['response'],
                                            method=file_method, filename=file_name)
            except Exception as e:
                DataManager_get.insert_data(table_name='redis', id=id_max, product_name=data['name'],
                                            current_strategy=data['response'],
                                            method=file_method, filename=file_name)
            # 存储到小表中
            if data['name'] not in tables_list:
                tables_list.append(data['name'])
                DataManager_get.Creat_New_table(data['name'])
                try:
                    DataManager_get.insert_data(table_name=data['name'], id=0,
                                                time=file_time.strftime('%Y-%m-%d'), current_strategy=data['response'],
                                                method=file_method, filename=file_name)
                except Exception as e:
                    DataManager_get.insert_data(table_name=data['name'], id=0,
                                                current_strategy=data['response'],
                                                method=file_method, filename=file_name)
            else:
                id_max_category = DataManager_get.id_MAX_Get(data['name'])[0] + 1
                try:
                    DataManager_get.insert_data(table_name=data['name'], id=id_max_category,
                                                time=file_time.strftime('%Y-%m-%d'), current_strategy=data['response'],
                                                method=file_method, filename=file_name)
                except Exception as e:
                    DataManager_get.insert_data(table_name=data['name'], id=id_max_category,
                                                time=file_time.strftime('%Y-%m-%d'), current_strategy=data['response'],
                                                method=file_method, filename=file_name)
            id_max += 1
        print(f'{file_name}的数据导入完毕！')
