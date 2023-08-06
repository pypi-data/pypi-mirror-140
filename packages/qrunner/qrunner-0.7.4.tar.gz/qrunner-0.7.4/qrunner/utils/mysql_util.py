# @Time    : 2022/2/11 16:52
# @Author  : kang.yang@qizhidao.com
# @File    : mysql_util.py
import pymysql


class BaseDB(object):
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.con = pymysql.connect(host=self.host,
                                   user=self.username,
                                   password=self.password,
                                   database=self.database,
                                   charset='utf8',
                                   )
        # cursorclass=pymysql.cursors.DictCursor
        self.cursor = self.con.cursor()

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'插入失败: {e}')
            self.con.rollback()
        else:
            print('插入成功')
        finally:
            self.close()

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'删除失败: {e}')
            self.con.rollback()
        else:
            print('删除成功')
        finally:
            self.close()

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(f'更新失败: {e}')
            self.con.rollback()
        else:
            print('更新成功')
        finally:
            self.close()

    def select(self, sql, one=True):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(f'查询失败: {e}')
        else:
            print('查询成功,', end=' ')
            if one:
                items = list(self.cursor.fetchone())
                print(f'共查询出: 1 行数据, 第一行数据如下:')
                print(f'{items}\n')
            else:
                items = list(self.cursor.fetchall())
                print(f'共查询出: {len(items)} 行数据, 第一行数据如下:')
                print(f'{items[0]}\n')
            return items
        finally:
            self.close()

    def close(self):
        self.cursor.close()
        self.con.close()


class ApiDB(BaseDB):
    def __init__(self):
        super().__init__(
            host='172.16.3.247',
            username='root',
            password='Wz@888888',
            database='apitest',
        )
        self.table_api = 'api'

    def get(self, one=False):
        sql = f"select * from {self.table_api}"
        print(sql)
        result = self.select(sql, one=one)
        print(result)
        return result

    def set(self, api_info: list):
        project = api_info[0]
        moduleName = api_info[1]
        moduleDesc = api_info[2]
        apiPath = api_info[3]
        apiDesc = api_info[4]
        sql = f"insert into {self.table_api}(project, moduleName, moduleDesc, apiPath, apiDesc) " \
              f"values('{project}', '{moduleName}', '{moduleDesc}', '{apiPath}', '{apiDesc}')"
        print(sql)
        self.insert(sql)


if __name__ == '__main__':
    pass









