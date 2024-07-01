from pymysql import OperationalError
import pymysql


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
        columns = ', '.join(f"`{key}`" for key in kwargs.keys())
        placeholders = ', '.join(['%s'] * len(kwargs))
        values = tuple(kwargs.values())
        self.query = f"INSERT INTO redis ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(self.query, values)
            self.connection.commit()
        except pymysql.MySQLError as e:
            pass

    def search_data(self, id):  # 查找
        self.query = f"SELECT * from redis WHERE id={id}"
        try:
            self.cursor.execute(self.query)
            outcome = self.cursor.fetchone()
            columns = ['id', 'product_name', 'time', 'current_strategy', 'later_strategy', 'product_state',
                       'binary_code', 'methed']
            return dict(zip(columns, list(outcome)))
        except:
            return None

    def delete(self, id):  # 删
        self.query = f"DELETE  from redis WHERE id={id}"
        self.cursor.execute(self.query)
        self.connection.commit()


if __name__ == "__main__":
    test = DataManager()
    test.delete(id=3120)
