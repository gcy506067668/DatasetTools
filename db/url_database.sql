CREATE TABLE urls(
    u_id            INT NOT NULL AUTO_INCREMENT,
    u_url           TEXT NOT NULL,
    u_label         TEXT,
    u_flag          INT DEFAULT 0,
    u_finder        VARCHAR(10),
    PRIMARY KEY (u_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;




