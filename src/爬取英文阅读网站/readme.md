关于newspaper表的创建

```sql
CREATE TABLE
  `newspaper` (
    `title` varchar(1024) DEFAULT NULL,
    `detail_url` text,
    `release_time` date DEFAULT NULL,
    `content` text,
    UNIQUE KEY `title` (`title`(255))
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci
```

