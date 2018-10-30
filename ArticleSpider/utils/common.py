#!/usr/bin/env python 
# -*- coding:utf-8 -*-
__author__ = 'Saikikky'
import hashlib

def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest() #抽取摘要

if __name__ == "__main__":
    print (get_md5("http://jobbole.com".encode("utf-8")))
