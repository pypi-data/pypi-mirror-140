"""
@des: 这个文件仅仅作为views，接口调用访问，归因内部不用这个文件
@des: 调用方法
from tfduck.common.defines import BMOBJ, Et
tdq = ThinkDataQuery("http://xxxxxxx:xxx/querySql", token="xxxxxxxxxx")
try:
    sql = ''' select * from v_user_7 limit 100  '''
    local_file = tdq.get_data_csv({}, sql, block_size=50000)
    df = pandas.read_csv(local_file, header=0)
finally:
    BMOBJ.remove_file(local_file)
"""
import requests
import pandas
import json
import time
import os
import uuid
import urllib3
from tfduck.common.defines import BMOBJ, Et
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED


class ThinkDataQuery(object):
    """
    @des: thinkdata openapi查询基础类----这个只能再thinkdata内网执行
    """

    def __init__(self, query_uri, token):
        """
        @des:初始化类
        """
        self.query_uri = query_uri  # "http://47.90.251.214:8992/querySql"
        self.token = token

    def gen_local_unique_file(self, ext="csv"):
        """
        @des:生成本地文件唯一路径
        """
        # media_root = settings.MEDIA_ROOT
        media_root = "/mydata/media"
        base_dir = os.path.join(media_root, "docs")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        real_name = "%s%s.%s" % (uuid.uuid1().hex, uuid.uuid1().hex, ext)
        file_path = os.path.join(base_dir, real_name)
        return file_path

    def g_to_csv_notmp(self, filepath, df, index=True, compression=None, mode='w', header=True):
        """
        @des: pandas生成csv文件---用于追加文件，不能用临时文件
        compression: 压缩格式 ‘gzip’, ‘bz2’, ‘zip’, ‘xz’. 
        """
        tmp_filepath = filepath
        if index is None:  # 不保存行索引
            if compression is None:  # 不压缩
                df.to_csv(tmp_filepath, index=None, mode=mode, header=header)
            else:
                df.to_csv(tmp_filepath, index=None,
                          compression=compression, mode=mode, header=header)
        else:
            if compression is None:  # 不压缩
                df.to_csv(tmp_filepath, mode=mode, header=header)
            else:
                df.to_csv(tmp_filepath, compression=compression,
                          mode=mode, header=header)
        return True

    def get_data_csv(self, ctx, sql, block_size=100000):
        """
        @des:从thinkdata的openapi获取数据----流式，为了节省内存---配合下面的getquerycsv
        """
        session = requests.session()
        post_data = {'token': self.token, 'sql': sql}
        #
        unique_path = self.gen_local_unique_file()
        #
        BMOBJ.log_error("in query")
        #
        r = session.post(self.query_uri, data=post_data, stream=True,
                         verify=False, timeout=(300, 600))
        datas = []
        i = 0    # 循环引用计数
        icount = 0  # 数据的数量
        cols = []  # 表头
        try:
            # iter_lines iter_content, chunk_size字节, 下面取100M
            for row in r.iter_lines(chunk_size=1024*1024*100):
                if not row:
                    continue
                data = None
                if i == 0:  # 处理header
                    data = json.loads(row)
                    if(data["return_code"] == 0):
                        cols = data["data"]["headers"]
                        df = pandas.DataFrame(data=[], columns=cols)  # 保存表头
                        self.g_to_csv_notmp(unique_path, df, index=None)
                        data = None
                    else:
                        BMOBJ.log_error("sql error:", data)
                        # BMOBJ.log_error(sql)
                        datas = []
                        break  # 表示查询出错，没有消息
                else:
                    if row.strip() not in [b"", ""]:
                        data = json.loads(row)
                if data is not None:
                    datas.append(data)
                i += 1
                if len(datas) == block_size:  # 1000000条保存一次
                    df = pandas.DataFrame(data=datas, columns=cols)  # 保存表头
                    self.g_to_csv_notmp(unique_path, df, index=None,
                                        mode='a', header=False)  # 追加保存
                    icount += block_size
                    datas = []
                if i % block_size == 0:
                    BMOBJ.clog(ctx, i)
            BMOBJ.clog(ctx, f"total: {i}")
            if len(datas) > 0:  # 保存最后收尾的
                df = pandas.DataFrame(data=datas, columns=cols)  # 保存表头
                self.g_to_csv_notmp(unique_path, df, index=None,
                                    mode='a', header=False)  # 追加保存
                icount += len(datas)
                datas = []
        except Exception as e:
            BMOBJ.log_error("get data error", e)
        return unique_path
    
    def get_data_raw_pyhive(self, ctx, sql, block_size=100000, fetch_size=10000):
        '''
        @des:presto直连方式读取
        tobj = ThinkDataQuery("http://queryhost:port/querySql", "查询token",
                          ["presto直连的host", 直连的port])  
        sql = """select * from v_event_7 where "$part_date"='2022-02-24' limit 100 """
        unique_path = tobj.get_data_raw_pyhive({}, sql)
        '''
        from pyhive import presto
        #
        unique_path = self.gen_local_unique_file()
        # unique_path = "./test.csv"
        #
        BMOBJ.log_error("in query")
        #
        datas = []
        i = 0    # 循环引用计数
        icount = 0  # 数据的数量
        cols = []  # 表头
        try:
            conn = presto.connect(host=self.hive_conn_info[0],
                                  port=int(self.hive_conn_info[1]),
                                  username='ta', catalog='hive', 
                                  schema='ta',
                                  requests_kwargs={"timeout":(300,600), "stream":True, "verify":False}
                                  )
            cursor = conn.cursor()
            cursor.execute(sql)
            BMOBJ.clog(ctx, "文件大小")
            if 1:
                cols = [item[0] for item in cursor.description]
                # print(cols)
                df = pandas.DataFrame(data=[], columns=cols)  # 保存表头
                self.g_to_csv_notmp(unique_path, df, index=None)
            # for row in cursor.fetchall():
            rows = []
            rows = cursor.fetchmany(fetch_size)
            while rows:
                for row in rows:
                    if not row:
                        continue
                    datas.append(row)
                    i += 1
                    if len(datas) == block_size:  # 1000000条保存一次
                        df = pandas.DataFrame(data=datas, columns=cols)  # 保存表头
                        self.g_to_csv_notmp(unique_path, df, index=None,
                                            mode='a', header=False)  # 追加保存
                        icount += block_size
                        datas = []
                    if i % block_size == 0:
                        BMOBJ.clog(ctx, i)
                rows = cursor.fetchmany(fetch_size)
            #
            BMOBJ.clog(ctx, f"total: {i}")
            if len(datas) > 0:  # 保存最后收尾的
                df = pandas.DataFrame(data=datas, columns=cols)  # 保存表头
                self.g_to_csv_notmp(unique_path, df, index=None,
                                    mode='a', header=False)  # 追加保存
                icount += len(datas)
                datas = []
        except Exception as e:
            BMOBJ.log_error("get data error", e)
        finally:
            conn.close()
        return unique_path

