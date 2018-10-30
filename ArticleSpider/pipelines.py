# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

#用于做数据存储 把数据保存至mysql
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from  twisted.enterprise import  adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        # 打开json文件的打开和写入
        self.file = codecs.open('article.json', 'w', encoding="utf-8")
    def process_item(self, item, spider):
        # 将item写入到文件中
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n" #否则会乱码
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

class MysqlPipeline(object):
    # 对数据库数据量没有那么大的时候
    # 采用同步的机制写入mysql

    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '19961125', 'article_spider', charset = 'utf8')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s, %s)
        """
        # 此处的execute和commit函数是同步的不是异步的
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))
     #   print (self.cursor.rowcount)
        self.conn.commit()

class MysqlTwistedPipline(object):
    # Twisted提供的框架实现mysql插入异步化

    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 自定义主键或者扩展的时候，可以直接从settings中取得内容
    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        # **dbparams 是一种可变参数
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        # 也可以这样写
        #dbpool = adbapi.ConnectionPool("MySQLdb", host=settings["MYSQL_HOST"], db = settings["MYSQL_DBNAME"])

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider) # 也可以不用item和spider 那么底下也不用传入


    def handle_error(self, failure, item, spider):
        # 处理异步插入异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into jobbole_article(title, url, create_date, fav_nums)
                    VALUES (%s, %s, %s, %s)
                """
        # 此处的execute和commit函数是同步的不是异步的
        cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))



class JsonExporterPipleline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb') #wb二进制的方式打开
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 继承 ImagesPipeline类
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item
        # 文件存储路径在results里面

