CREATE TABLE urls(
    u_id            INT NOT NULL AUTO_INCREMENT,
    u_url           TEXT NOT NULL,
    u_flag          INT NOT NULL,
    u_finder        VARCHAR(10),
    u_find_time     LONG NOT NULL,
    PRIMARY KEY (u_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;

CREATE TABLE url_label(
    ul_id            INT NOT NULL AUTO_INCREMENT,
    ul_url_id           INT NOT NULL,
    ul_label_id          INT NOT NULL,
    PRIMARY KEY (ul_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;

CREATE TABLE labels(
    l_id            INT NOT NULL AUTO_INCREMENT,
    l_value         VARCHAR(10),
    PRIMARY KEY (l_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;

CREATE TABLE download_record(
    d_id            INT NOT NULL AUTO_INCREMENT,
    d_file_flag     INT DEFAULT 0,
    d_label_id      INT DEFAULT 0,
    d_url           TEXT,
    d_filepath      TEXT,
    d_downloader    VARCHAR(10),
    d_d_time        LONG NOT NULL,
    PRIMARY KEY (d_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;