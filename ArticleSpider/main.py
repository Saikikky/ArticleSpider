#!/usr/bin/env python 
# -*- coding:utf-8 -*-
__author__ = 'Saikikky'

from scrapy.cmdline import execute

import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"]) #运行这个命令