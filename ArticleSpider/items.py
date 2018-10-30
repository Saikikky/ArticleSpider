# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime
from  scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def add_jobbole(value):
    return value + "-jobbole"


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义itemLoader
    default_output_processor = TakeFirst()

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # 会把title里的值传给value 对title进行预处理
        # MapCompose里面也可以调用两个函数
        # MapCompose(lambda x:x+"-saikikky", add_jobbole)
        # 可以在title后面同时加上-saikikky和-jobbole
      #  input_processor = MapCompose(add_jobbole)
    ) #赋值类似于字典 Field是数据类型
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
      #  output_processor = TakeFirst() # 只取第一个
    )
    url = scrapy.Field() #url是变长的 对其进行md5使其变成固定长度
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        out_processor = Join(", ")
    )
    content = scrapy.Field()