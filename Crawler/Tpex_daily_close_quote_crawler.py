# -*- coding: utf-8 -*-
"""
Tpex Daily Daily Close Quote Crawler

Source: http://www.tpex.org.tw/web/index.php?l=zh-tw
"""

### Function
def tpex_daily_close_quote_crawler(date = ''):

    """
    Format:
    1. Input:
        (1) date to cralwer: string, 'year/month/day', such as '2018/10/10'
    2. Output:
        A dataframe in "pandas.core.frame.DataFrame" type, can be saved as a csv file
    """

    ### Load required packages
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import warnings
    warnings.filterwarnings("ignore")
    
    ### Chekc if the date entered is valid
    try:
        if '/' in date:
            if int(date.split('/')[0]) < 1911:
                date = '/'.join([str(int(date.split('/')[0]) + 1911)] + date.split('/')[1:])
        
        date = pd.to_datetime(date)
    ## Exception: invalid date
    except ValueError:
        return 'Please enter the valid date.'
    
    ### Transform the date format
    date_list = str(date.date()).split('-')
    date = '/'.join([str(int(date_list[0]) - 1911), date_list[1], date_list[2]])
    
    ### Set up the header
    header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            }
    
    session = requests.Session()
    
    ### Construct the names for the columns
    url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote.php?l=zh-tw'
    page = session.get(url, headers = header)
    page.encoding = 'utf-8'
    page = BeautifulSoup(page.text)
    colnames = [x.text for x in page.find('table').findAll('th')]
    
    ### Setup th crawling session and get the data

    stock_url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d='
    page = session.get(stock_url + date, headers = header)
    data = page.json()
    
    ordinary_stock = 'aaData'
    manage_stock = 'mmData'
    
    ## Exception: date without stock
    if len(data[ordinary_stock]) == 0:
        return 'There are no stocks on this day specified.'
    
    if len(data[manage_stock]) > 0:
        data_manage = pd.DataFrame(data[manage_stock], columns = colnames)
        data_manage['管理股票'] = 1
    
    data_ordinary = pd.DataFrame(data[ordinary_stock], columns = colnames)
    data_ordinary['管理股票'] = 0
    
    df = pd.concat([data_ordinary, data_manage], axis = 0)

    return df
    
    







###############################################################################