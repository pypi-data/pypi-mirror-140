#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
作者： bartoncheng
日期：2022年02月28日
"""
import sys

PY3 = (sys.version_info[0] >= 3)

INDEX_LABELS = ['sh', 'sz', 'hs300', 'sz50', 'cyb', 'zxb', 'zx300', 'zh500']
NETWORK_URL_ERROR_MSG = '获取失败，请检查网络.'
K_LABELS = ['D', 'W', 'M']
DAY_PRICE_URL = '%sapi.finance.%s/%s/?code=%s&type=last'
P_TYPE = {'http': 'http://', 'ftp': 'ftp://'}
DOMAINS = {'sina': 'sina.com.cn', 'sinahq': 'sinajs.cn',
           'ifeng': 'ifeng.com', 'sf': 'finance.sina.com.cn',
           'vsf': 'vip.stock.finance.sina.com.cn',
           'idx': 'www.csindex.com.cn', '163': 'money.163.com',
           'em': 'eastmoney.com', 'sseq': 'query.sse.com.cn',
           'sse': 'www.sse.com.cn', 'szse': 'www.szse.cn',
           'oss': 'file.tushare.org', 'idxip': '115.29.204.48',
           'shibor': 'www.shibor.org', 'mbox': 'www.cbooo.cn',
           'tt': 'gtimg.cn', 'gw': 'gw.com.cn',
           'v500': 'value500.com', 'sstar': 'stock.stockstar.com',
           'dfcf': 'nufm.dfcfw.com'}

K_TYPE = {'D': 'akdaily', 'W': 'akweekly', 'M': 'akmonthly'}

K_MIN_LABELS = ['5', '15', '30', '60']
DAY_PRICE_MIN_URL = '%sapi.finance.%s/akmin?scode=%s&type=%s'
INX_DAY_PRICE_COLUMNS = ['date', 'open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change',
                         'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']
DAY_PRICE_COLUMNS = ['date', 'open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change',
                     'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20', 'turnover']


def _code_to_symbol(code):
    '''
        生成代码标志symbol
    '''

    if code in INDEX_LABELS:
        return INDEX_LABELS[code]
    elif code[:3] == 'gb_':
        return code
    else:
        if len(code) != 6:
            return code
        else:
            return 'sh%s' % code if code[:1] in ['5', '6', '9'] or code[:2] in ['11', '13'] else 'sz%s' % code
