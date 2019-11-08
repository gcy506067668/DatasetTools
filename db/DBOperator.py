from db.URLDatabase import ConnPool
from db.dbconfig import DBConfig


class DBBase:
    def __init__(self):
        self.conn = ConnPool().getConn()
        self.cursor = self.conn.cursor()
        pass

    def execute(self, sql):

        self.cursor.execute(sql)
        self.conn.commit()
        pass

    def executeWithReturn(self, sql, fetchSize=-1):
        self.cursor.execute(sql)
        if fetchSize == 1:
            return self.cursor.fetchone()
        elif fetchSize == -1:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchmany(fetchSize)

    pass


class DBUrl(DBBase):
    URL_FLAG_UNDOWNLOAD = 0
    URL_FLAG_DOWNLOAD_SUCCESS = 1
    URL_FLAG_DOWNLOAD_ERROR = 2

    def __init__(self, label=""):
        self.label = label
        self.conn = ConnPool().getConn()
        self.cursor = self.conn.cursor()
        pass

    def addURL(self, url):
        u_id = self.isUrlExists(url)
        if u_id != -1:
            return False
        sql = "insert into urls(u_url,u_label,u_finder) values ('" + url + "','" + self.label + "','" + DBConfig.username + "');"
        self.execute(sql)
        return True
        pass

    def updateFlag(self, url, flag):
        sql = "update urls set u_flag=" + str(flag) + " where u_url='" + url + "';"
        self.execute(sql)
        pass

    def isUrlExists(self, url):
        sql = "select u_id from urls where u_url='" + url + "';"
        result = self.executeWithReturn(sql, 1)
        if result:
            return result['u_id']
        else:
            return -1
        pass

    def findAllToDownload(self):
        sql = "select u_id, u_url,u_label from urls where u_finder='" + DBConfig.username + "' and u_flag=0;"
        return self.executeWithReturn(sql)
        pass


class DBDownload(DBBase):
    DOWNLOAD_FLAG_UNDO = 0
    DOWNLOAD_FLAG_NODAMAGE = 1
    DOWNLOAD_FLAG_NOREPEAT = 2
    DOWNLOAD_FLAG_DAMAGE = 3
    DOWNLOAD_FLAG_REPEAT = 4
    DOWNLOAD_FLAG_NO_SELFREPEAT = 5

    def __init__(self):
        self.conn = ConnPool().getConn()
        self.cursor = self.conn.cursor()
        pass

    def addDownload(self, url, savepath, label):
        sql = "insert into downloads(d_label,d_url,d_filepath,d_downloader) values ('" + label + "','" + url + "','" + savepath + "','" + DBConfig.username + "');"
        self.execute(sql)
        pass

    def updateFlag(self, flag, filepath):
        sql = "update downloads set d_flag=" + str(
            flag) + " where d_filepath='" + filepath + "' and d_downloader='" + DBConfig.username + "';"
        self.execute(sql)

        pass

    def findAllToDeDamage(self):
        sql = "select d_filepath from downloads where d_flag=0 and d_downloader='" + DBConfig.username + "';"
        res = self.executeWithReturn(sql)
        urls = []
        if res:
            for item in urls:
                urls.append(str(item["d_filepath"], encoding='utf8'))
        return urls
        pass

    def findAllToDerepeat(self):
        sql = "select d_filepath from downloads where d_flag=1 and d_downloader='" + DBConfig.username + "';"
        res = self.executeWithReturn(sql)
        urls = []
        if res:
            for item in urls:
                urls.append(str(item["d_filepath"], encoding='utf8'))
        return urls
        pass

    def findAllDerepeated(self):
        sql = "select d_filepath from downloads where d_flag=2 and d_downloader='" + DBConfig.username + "';"
        res = self.executeWithReturn(sql)
        urls = []
        if res:
            for item in urls:
                urls.append(str(item["d_filepath"], encoding='utf8'))
        return urls
        pass

    def findAllToDelete(self):
        sql = "select d_filepath from downloads where d_flag=4 and d_downloader='" + DBConfig.username + "';"
        res = self.executeWithReturn(sql)
        urls = []
        if res:
            for item in urls:
                urls.append(str(item["d_filepath"], encoding='utf8'))
        return urls
        pass

    def findAllNoSelfRepeat(self):
        sql = "select d_filepath from downloads where d_flag=5 and d_downloader='" + DBConfig.username + "';"
        res = self.executeWithReturn(sql)
        urls = []
        if res:
            for item in urls:
                urls.append(str(item["d_filepath"], encoding='utf8'))
        return urls
        pass

    def setAllNoRepeat(self):
        sql = "update downloads set d_flag=2 where d_flag=5 and d_downloader='" + DBConfig.username + "';"
        self.execute(sql)
        pass