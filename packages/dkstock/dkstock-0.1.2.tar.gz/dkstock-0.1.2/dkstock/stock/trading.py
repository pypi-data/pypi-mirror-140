#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
作者： bartoncheng
日期：2022年02月28日
"""

from __future__ import division

import time
import json
import pandas as pd
import numpy as np
import datetime
import os

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlopen, Request

from dkstock.stock import exchange as ec


def get_hist_data(code=None, start=None, end=None, ktype='D', retry_count=3, pause=0.001):
    """
        获取个股历史交易记录
    Parameters
    ------
      code:string
                  股票代码 e.g. 600848
      start:string
                  开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
      end:string
                  结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
      ktype：string
                  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
      retry_count : int, 默认 3
                 如遇网络等问题重复执行的次数
      pause : int, 默认 0
                重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    return
    -------
      DataFrame
          属性:日期 ，开盘价， 最高价， 收盘价， 最低价， 成交量， 价格变动 ，涨跌幅，5日均价，10日均价，20日均价，5日均量，10日均量，20日均量，换手率
    """
    symbol = ec._code_to_symbol(code)
    url = ''
    if ktype.upper() in ec.K_LABELS:
        url = ec.DAY_PRICE_URL % (ec.P_TYPE['http'], ec.DOMAINS['ifeng'], ec.K_TYPE[ktype.upper()], symbol)
    elif ktype in ec.K_MIN_LABELS:
        url = ec.DAY_PRICE_MIN_URL % (ec.P_TYPE['http'], ec.DOMAINS['ifeng'], symbol, ktype)
    else:
        raise TypeError('ktype input error.')

    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(url)
            lines = urlopen(request, timeout=10).read()
            if len(lines) < 15:  # no data
                return None
        except Exception as e:
            print(e)
        else:
            js = json.loads(lines.decode('utf-8') if ec.PY3 else lines)
            cols = []
            if (code in ec.INDEX_LABELS) & (ktype.upper() in ec.K_LABELS):
                cols = ec.INX_DAY_PRICE_COLUMNS
            else:
                cols = ec.DAY_PRICE_COLUMNS
            if len(js['record'][0]) == 14:
                cols = ec.INX_DAY_PRICE_COLUMNS

            df = pd.DataFrame(js['record'], columns=cols)

            if ktype.upper() in ['D', 'W', 'M']:
                df = df.applymap(lambda x: x.replace(u',', u''))
                df[df == ''] = 0
            for col in cols[1:]:
                df[col] = df[col].astype(float)
            if start is not None:
                df = df[df.date >= start]
            if end is not None:
                df = df[df.date <= end]
            if (code in ec.INDEX_LABELS) & (ktype in ec.K_MIN_LABELS):
                df = df.drop('turnover', axis=1)
            df = df.set_index('date')
            df = df.sort_index(ascending=False)
            return df
    raise IOError(ec.NETWORK_URL_ERROR_MSG)
