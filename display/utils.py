import pymysql
import tempfile


def get_news(company_name):
    company_file_list = []
    return ["新闻1", "新闻2"]


def save_binary_as_temp_pdf(binary_data):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(binary_data)
    temp_file.close()
    return temp_file.name


def get_content_binary(db_config, filename, filetype):
    """
    根据 filename 和 filetype 从 MySQL 数据库中查找 content_binary。

    参数:
        db_config (dict): 包含数据库连接信息的字典，包括 host, user, password, 和 database。
        filename (str): 文件名。
        filetype (str): 文件类型。

    返回:
        bytes: 如果找到匹配记录，返回 content_binary 数据。
        None: 如果未找到匹配记录。
    """
    # 连接数据库
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # 定义查询语句
            sql_query = "SELECT content_binary FROM mytable WHERE filename = %s AND filetype = %s"

            # 执行查询
            cursor.execute(sql_query, (filename, filetype))

            # 获取结果
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return None

    finally:
        # 关闭数据库连接
        connection.close()


# 示例使用
if __name__ == "__main__":
    db_config = {
        'host': 'your_mysql_host',
        'user': 'your_mysql_user',
        'password': 'your_mysql_password',
        'database': 'mydatabase'
    }

    filename = 'example_filename'
    filetype = 'example_filetype'

    content_binary = get_content_binary(db_config, filename, filetype)

    if content_binary:
        print("Content binary data retrieved successfully.")
    else:
        print("No matching record found.")
