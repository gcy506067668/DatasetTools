class DBConfig:
    #pool config
    dbapi = None  # 数据库接口
    mincached = 1  # 启动时开启的空连接数量
    maxcached = 20  # 连接池最大可用连接数量
    maxshared = 5  # 连接池最大可共享连接数量
    maxconnections = 20  # 最大允许连接数量
    blocking = None  # 达到最大数量时是否阻塞
    maxusage = None  # 单个连接最大复用次数

    #mysql config
    host = "10.25.0.246"
    port = 3306
    username = "gcy"
    password = "12345678"
    dbname = "url_db"
    charset = "utf8"