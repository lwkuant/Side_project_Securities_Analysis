# -*- coding: utf-8 -*-
"""
Stock price crawler for specific stock within specific time period

Source: http://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html
"""

### Function
def stock_price_crawler(start_date = '', end_date = '', ticker_number = ''):
    
    """
    Format:
        1. Input:
            (1) start_date, end_date: string, 'year/month/day', such as '2018/10/10'
            (2) ticker_number: string, valid ticker for TWSE, such as '2330'
        2. Output:
            A dataframe in "pandas.core.frame.DataFrame" type, can be saved as a csv file
    """
    
    
    ### Load required packages
    import sys
    import json
    import requests
    import urllib
    import re
    import time
    import pandas as pd
    import numpy as np
    from itertools import chain
    import warnings
    warnings.filterwarnings("ignore")
    
    ### Helper function: Checking if a string is a valid float
    def float_checker(string):
        try:
            float(string)
            return True
        except ValueError:
            return False
    
    ### Check if the ticker number is entered
    if ticker_number == '':
        return 'Please enter the valid ticker number.'
    
    ### Chekc if the date entered is valid
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except ValueError:
        return 'Please enter the valid date.'
        
    ### Get the date list for each month involved
    date_list = sorted(list(set([''.join([str(int(str(x).split('-')[0])), str(x).split('-')[1]])+'01' for x in pd.date_range(start_date, end_date)])))
    
    ### Initialize the list for putting data crawled
    data_list = []
    
    ### Set up the header
    header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            }
    
    ### Set up the crawling session and get data for each month involved
    colnames = ["日期","成交股數","成交金額","開盤價","最高價","最低價","收盤價","漲跌價差","成交筆數"]
    bar_length = 100
    session = requests.Session()
    for ind, date in enumerate(date_list):
        page = session.get('http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=' + date + '&stockNo=' + ticker_number, headers = header).text
        page = json.loads(page)
        time.sleep(5)
        
        progress_length = int(np.round((ind+1)/len(date_list), 2)*bar_length)
        
        if page['stat'] == '查詢日期小於81年1月4日，請重新查詢!':
            sys.stdout.write('\r')
            sys.stdout.write('Progress: ' + '[' + '='*progress_length + ' '*(bar_length - progress_length) + '] ' + str(progress_length) + '%')
            sys.stdout.flush()
            continue
        
        if page['stat'] == '查詢日期大於今日，請重新查詢!':
            sys.stdout.write('\r')
            sys.stdout.write('Progress: ' + '[' + '='*bar_length + '] ' + str(100) + '%\n')
            sys.stdout.flush()
            break
        
        if page['stat'] == '很抱歉，沒有符合條件的資料!':
            return 'Please enter the valid ticker number.'
        
        data_list.append(page['data'])
        
        sys.stdout.write('\r')
        sys.stdout.write('Progress: ' + '[' + '='*progress_length + ' '*(bar_length - progress_length) + '] ' + str(progress_length) + '%')
        sys.stdout.flush()
        
        
    if len(data_list) == 0:
        return 'Please enter the valid time period'
        
    data = pd.DataFrame(list(chain(*data_list)))
    data.columns = colnames
    
    data['日期'] = pd.to_datetime([str(int(x.split('/')[0])+1911) + x[3:] for x in data['日期']])
    data.index = data['日期']
    
    for col in list(data.columns)[1:]:
        data.ix[:, col] = data.ix[:, col].apply(lambda x: float(re.sub(',', '', x)) if float_checker(re.sub(',', '', x)) else np.nan)
    
    data = data.ix[(data['日期'] >= start_date)&(data['日期'] <= end_date), :]
    data = data.ix[:, 1:]
    
    if data.shape[0] == 0:
        print('There is no data during the time period specified')
    
    return data

df_tsmc = stock_price_crawler('1994/09/01', '2018/03/23', '2330')
df_tsmc.to_csv('D:/Google雲端硬碟/Project/Side_project_Securities_Analysis/data/TSMC_to_20180323.csv')
