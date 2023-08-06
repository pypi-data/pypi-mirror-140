# coding=utf-8
# @Time    : 2022/2/21 11:21
# @Author  : kang.yang@qizhidao.com
# @File    : mongo_util.py
import pymongo


class BaseDB(object):
    def __init__(self, ip, db_name, table_name):
        self.client = pymongo.MongoClient(f"mongodb://{ip}:27017/")
        self.db = self.client[db_name]
        self.table = self.db[table_name]

    def insert_one(self, data: dict):
        print(f'插入数据: {data}')
        try:
            result = self.table.insert_one(data)
        except Exception as e:
            print(e)
        else:
            print('插入成功')
            print(result.inserted_id)
        finally:
            self.client.close()

    def insert_list(self, data: list):
        print(f'插入数据: {data}')
        try:
            result = self.table.insert_many(data)
        except Exception as e:
            print(e)
        else:
            print('插入成功')
            print(result.inserted_ids)
        finally:
            self.client.close()

    def select_all(self):
        print('查询表中所有数据')
        try:
            result = list(self.table.find())
        except Exception as e:
            print(e)
        else:
            print('查询成功')
            # print(result)
            return result
        finally:
            self.client.close()

    def select(self, query_data: dict):
        print(f'查询满足 {query_data} 条件的数据')
        try:
            result = list(self.table.find(query_data))
        except Exception as e:
            print(e)
        else:
            print('查询成功')
            # print(result)
            return result
        finally:
            self.client.close()

    def delete_all(self):
        print(f'删除所有数据')
        try:
            result = self.table.delete_many({})
        except Exception as e:
            print(e)
        else:
            print(result.deleted_count, "个文档已删除")
        finally:
            self.client.close()


class ApiSchema(BaseDB):
    def __init__(self):
        super().__init__(ip='172.16.3.247',
                         db_name='api_test',
                         table_name='schema')

    def get_schema_by_path(self, path: str):
        query = {'path': path}
        return self.select(query)

    def insert_schema(self, data: dict):
        self.insert_one(data)


if __name__ == '__main__':
    data = {'data': {'code': 'Beneficiary', 'name': '疑似最终受益人', 'job': '', 'children': [{'code': 'Beneficiary', 'enterpriseUrl': '/company/companyDetail?keyNo=540b1ed3fb30a4449b2893232fcb25f9&name=深圳市腾讯计算机系统有限公司', '_enterpriseId': '540b1ed3fb30a4449b2893232fcb25f9', 'name': '马化腾', 'enterpriseLogoUrl': 'https://qxb-logo-url.oss-cn-hangzhou.aliyuncs.com/OriginalUrl/618ffc1f7600438ae58a1c1b3dcdef5b.jpg', 'enterpriseName': '深圳市腾讯计算机系统有限公司', 'job': '', 'stockPercent': '54.2857%', 'type': 1, 'lineText': {'stockPercent': '54.2857%'}, 'headLabel': '疑似最终受益人', 'pathDesc': '控制路径(占比54.2857%)', 'pathChains': [{'pathChainName': '马化腾', 'pathChainValue': '54.2857%', 'pathChainType': 1}, {'pathChainName': '深圳市腾讯计算机系统有限公司', 'pathChainType': 2}], 'beneficiaryShare': '54.2857%', 'stockPercentRation': 54.2857, 'beneficiaryCode': ''}], 'stockPercentRation': 0.0}, 'code': 0, 'status': 0, 'success': True, 'msg': '成功', 'hasUse': 0}
    ApiSchema().insert_schema(data)



