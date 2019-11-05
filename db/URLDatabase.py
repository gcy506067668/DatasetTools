import time

from DBUtils.PooledDB import PooledDB
import pymysql
from pymysql.cursors import DictCursor
from db.dbconfig import DBConfig

"""
urls:flag
0-爬虫已爬取到
1-可以下载
2-下载损坏


download_record:flag
0-已下载未处理
1-无损坏
2-无重复
-1-损坏或者重复图片
"""


class ConnPool:
    __pool = None

    def __new__(cls, *args, **kw):
        """single instance"""
        if not hasattr(cls, '_instance'):
            orig = super(ConnPool, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
            cls.__pool = PooledDB(creator=pymysql,
                                  mincached=DBConfig.mincached,
                                  maxcached=DBConfig.maxcached,
                                  host=DBConfig.host,
                                  port=DBConfig.port,
                                  user=DBConfig.username,
                                  passwd=DBConfig.password,
                                  db=DBConfig.dbname,
                                  use_unicode=False,
                                  charset=DBConfig.charset,
                                  cursorclass=DictCursor)

        return cls._instance

    def getConn(self):
        return self.__pool.connection()
        pass


class DB:
    URL_FLAG_FIND = 0
    URL_FLAG_DOWNLOAD = 1
    URL_FLAG_DAMAGE = 2

    @staticmethod
    def execute(sql):
        dbConn = ConnPool().getConn()
        dbCursor = dbConn.cursor()
        dbCursor.execute(sql)
        dbConn.commit()
        pass

    @staticmethod
    def executeWithReturn(sql, fetchSize=-1):
        dbConn = ConnPool().getConn()
        dbCursor = dbConn.cursor()
        dbCursor.execute(sql)
        if fetchSize == 1:
            return dbCursor.fetchone()
        elif fetchSize == -1:
            return dbCursor.fetchall()
        else:
            return dbCursor.fetchmany(fetchSize)

    @staticmethod
    def findLabel(label_name):
        sql = "select l_id from labels where l_value='" + label_name + "';"
        return DB.executeWithReturn(sql, fetchSize=1)
        pass

    """if lable exist return lable's id then new lable and return lable's id"""

    @staticmethod
    def addLabel(label_name):
        result = DB.findLabel(label_name)
        if result:
            return result['l_id']
        else:
            sql = "insert into labels(l_value) values('" + label_name + "');"
            DB.execute(sql)
            return DB.addLabel(label_name)

    @staticmethod
    def addUrlLabel(url_id, label_id):
        sql = "insert into url_label(ul_url_id, ul_label_id) values(" + str(url_id) + "," + str(label_id) + ");"
        DB.execute(sql)
        pass

    @staticmethod
    def findUrlLabel(url_id, label_id):
        sql = "select ul_id from url_label where ul_url_id='" + str(url_id) + "' and ul_label_id='" + str(
            label_id) + "';"
        fetches = DB.executeWithReturn(sql, 1)
        if fetches:
            return True
        else:
            return False
        pass

    @staticmethod
    def findURL(url):
        sql = "select u_id from urls where u_url='" + url + "';"
        return DB.executeWithReturn(sql, fetchSize=1)
        pass

    @staticmethod
    def findAllPicToDownload():
        sql = "select u_url from urls where u_finder='" + DBConfig.username + "' and u_flag=0;"
        return DB.executeWithReturn(sql)
        pass

    @staticmethod
    def insertURL(url):
        timestamp = str(int(time.time()))
        sql = "insert into urls(u_url, u_flag, u_finder, u_find_time) values('" + url + "',0,'" + DBConfig.username + "'," + timestamp + ");"
        DB.execute(sql)
        res = DB.findURL(url)
        if res:
            return res["u_id"]

        pass

    @staticmethod
    def addUrl(url, label_name):
        url_res = DB.findURL(url)
        label_res = DB.findLabel(label_name)
        if url_res:
            if label_res:
                if DB.findUrlLabel(url_res["u_id"], label_res["l_id"]):
                    return False
                else:
                    DB.addUrlLabel(url_res["u_id"], label_res["l_id"])
                    return True
            else:
                label_id = DB.addLabel(label_name)
                DB.addUrlLabel(url_res["u_id"], label_id)
                return True

        else:
            url_id = DB.insertURL(url)
            label_id = DB.addLabel(label_name)
            DB.addUrlLabel(url_id, label_id)
            return True
        pass

    @staticmethod
    def update(table_name, set_value, where):
        sql = "update " + table_name + " set " + set_value + " " + where + " ;"
        DB.execute(sql)

    @staticmethod
    def addDownloadRecord(url, filepath):
        sql = "insert into download_record(d_file_flag,d_url,d_filepath,d_downloader,d_d_time) values (0,'" + url + "','" + filepath + "','" + DBConfig.username + "'," + str(
            int(
                time.time())) + ");"
        DB.execute(sql)
        pass

    @staticmethod
    def findAllToDeDamage():
        sql = "select d_url,d_filepath from download_record where d_downloader='" + DBConfig.username + "' and d_file_flag=0"
        return DB.executeWithReturn(sql)

    @staticmethod
    def findAllToDeRepeat():
        sql = "select d_url,d_filepath from download_record where d_downloader='" + DBConfig.username + "' and d_file_flag=1"
        return DB.executeWithReturn(sql)

    pass


class DBAPI:

    @staticmethod
    def getDownload():
        urls = []
        images = DB.findAllPicToDownload()
        for item in images:
            urls.append(str(item["u_url"], encoding='utf8'))
        return urls
        pass

    @staticmethod
    def addUrl(url, label):
        return DB.addUrl(url, label)
        pass

    @staticmethod
    def downloadSuccess(url, savepath):
        table_name = "urls"
        set_value = " u_flag=1 "
        where = " where u_url='" + url + "'"
        DB.update(table_name, set_value, where)
        DB.addDownloadRecord(url, savepath)
        pass

    @staticmethod
    def downloadFaild(url):
        table_name = "urls"
        set_value = " u_flag=2 "
        where = " where u_url='" + url + "'"
        DB.update(table_name, set_value, where)
        pass

    @staticmethod
    def getImageToDeDamage():
        return DB.findAllToDeDamage()

    @staticmethod
    def getImageToDerepeat():
        q_res = DB.findAllToDeRepeat()
        filepathes = []
        urls = []
        for item in q_res:
            filepathes.append(str(item["d_filepath"], encoding="utf8"))
            urls.append(str(item["d_url"], encoding='utf8'))
        return urls, filepathes
        pass

    DOWNLOAD_FLAG_DAMAGE = -1
    DOWNLOAD_FLAG_REPEAT = -1
    DOWNLOAD_FLAG_NO_DAMAGE = 1
    DOWNLOAD_FLAG_NO_REPEAT = 2

    @staticmethod
    def setDownloadFlag(url, flag):
        table_name = "download_record"
        set_value = " d_file_flag=" + str(flag)
        where = " where d_url='" + url + "'"
        DB.update(table_name, set_value, where)
        pass

    @staticmethod
    def setDownloadFlagByFilepath(filepath, flag):
        table_name = "download_record"
        set_value = " d_file_flag=" + str(flag)
        where = " where d_filepath='" + filepath + "'"
        DB.update(table_name, set_value, where)
        pass

    @staticmethod
    def selectByLabels(labels, limit=-1):
        if isinstance(labels, str):
            sql = "select l_id from labels where l_value like '%" + labels + "%'"
            res = DB.executeWithReturn(sql, 1)
            if res:
                label_id = res["l_id"]
            else:
                print("no such label name " + labels)
                return []

            sql = "select u_url from urls where u_id in (select ul_url_id from url_label where ul_label_id=" + str(
                label_id) + ")"
            if limit != -1:
                sql += "limit " + str(limit)
            result = DB.executeWithReturn(sql)
            urls = []
            for item in result:
                urls.append(str(item["u_url"], encoding='utf8'))
            return urls

        if isinstance(labels, (list, tuple)):
            sql = "select l_id from labels where "
            where = ""
            for index, label in enumerate(labels):
                if index != 0:
                    where += " or l_value like '%" + label + "%'"
                else:
                    where += " l_value like '%" + label + "%'"
            sql += where
            l_ids = []
            select_ids = DB.executeWithReturn(sql)
            for item in select_ids:
                l_ids.append(item["l_id"])

            result = []

            for l_id in l_ids:
                sql = "select u_url from urls where u_id in (select ul_url_id from url_label where ul_label_id=" + str(
                    l_id) + ")"
                if limit != -1:
                    sql += "limit " + str(limit)
                q_res = DB.executeWithReturn(sql)
                for item in q_res:
                    result.append(str(item["u_url"], encoding='utf8'))

            return result

        pass

    """删除某个标签的所有url和url_label对应关系记录"""

    @staticmethod
    def deleteUrlByLabel(label):
        sql = "select l_id from labels where l_value='%" + label + "%'"
        res = DB.executeWithReturn(sql, 1)
        if res:
            label_id = res["l_id"]
        else:
            print("no such label name " + label)
            return False

        sql = "delete from urls where u_id in (select ul_url_id from url_label where ul_label_id=" + str(label_id) + ")"
        DB.execute(sql)
        sql = "delete from url_label where ul_label_id=" + str(label_id) + ""
        DB.execute(sql)
        return True
        pass
