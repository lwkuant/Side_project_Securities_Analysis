# -*- coding: utf-8 -*-
"""
TWSE Stock Day Trading Data Crawler
http://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html
"""


def Day_trading_crawler(start_date = '', end_date = '', ticker_number = ''):
    
    """
    Format:
        (1) start_date, string, end_date: 'year/month/day', such as '2018/10/10'
        (2) ticker_number: string, valid ticker for TWSE, such as '2330'
    """
    
    
    ### Load required packages
    import json
    import requests
    import urllib
    import re
    import time
    import pandas as pd
    import numpy as np
    from itertools import chain
    
    ### Load required packages
    if ticker_number == '':
        return 'Please enter the valid ticker number.'
    
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except ValueError:
        return 'Please enter the valid date.'
        
    
    header = ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
    date_list = sorted(list(set([''.join([str(int(str(x).split('-')[0])), str(x).split('-')[1]])+'01' for x in pd.date_range(start_date, end_date)])))
    
    data_list = []
    
    
    for date in date_list:
        page = requests.get('http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=' + date + '&stockNo=' + ticker_number).text
        page = json.loads(page)
        time.sleep(1)
        
        if page['stat'] == '查詢日期小於81年1月4日，請重新查詢!':
            next
        
        if page['stat'] == '查詢日期大於今日，請重新查詢!':
            break
        
        if page['stat'] == '很抱歉，沒有符合條件的資料!':
            return 'Please enter the valid ticker number.'
        
        data_list.append(page['data'])
    
    if len(data_list) == 0:
        return 'Please enter the valid time period'
        
    data = pd.DataFrame(list(chain(*data_list)))
    data.columns = header
    
    data['日期'] = pd.to_datetime([str(int(x.split('/')[0])+1911) + x[3:] for x in data['日期']])
    
    data = data.ix[(data['日期'] >= start_date)&(data['日期'] <= end_date), :]
    
    for col in list(data.columns)[1:]:
        data.ix[:, col] = data.ix[:, col].apply(lambda x: float(re.sub(',', '', x) if x[0].isdigit() else np.nan))
    
    return data
    
    
