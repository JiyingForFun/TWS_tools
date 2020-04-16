
import time
import  numpy as np
import requests
import datetime
import json
import twstock
import pandas as pd


def getYear(a):
    return a.year
def getMonth(a):
    return a.month
def getDay(a):
    return a.day
def getStrYearMonthDay(a, b, c):
    return '%d-%d-%d' % (a, b, c)
def getIndexMapper(a):
    vecStrDate = np.vectorize(getStrYearMonthDay)
    row_names = vecStrDate(a[:, 0], a[:,1], a[:,2])
    return dict([[index, name] for index, name in enumerate(row_names)])

def loadHistoryDataSingleSid(filename):
    np_tmp = np.fromfile(filename, dtype=np.float).reshape(-1, 8)
    vecStrDate = np.vectorize(getStrYearMonthDay)
    row_names = pd.to_datetime(np.array(vecStrDate(*np.hsplit(np_tmp[:,:3].astype(np.int), np.array([1,2])))).reshape(-1))
    #indexMapper= getIndexMapper(np_tmp[:,:3].astype(np.int))
    columnNames = ['Open', 'Close', 'High', 'Low', 'Volume']
    datas = pd.DataFrame(np_tmp[:, 3:], index=row_names,  columns=columnNames)
    datas.index.name='Date'
    return datas
   

def getHistoryDateSingleSid(sid,prev_year=2010, prev_month=1, prev_day=1, cur_year=2020, cur_month=4, cur_day=9):
    tostr = '%d/%d/%d' %( prev_day, prev_month, prev_year)
    fromstr = '%d/%d/%d' %( cur_day, cur_month, cur_year)
    _from = str(time.mktime(datetime.datetime.strptime(fromstr, "%d/%m/%Y").timetuple())).split('.')[0]
    _to = str(time.mktime(datetime.datetime.strptime(tostr, "%d/%m/%Y").timetuple())).split('.')[0]
    
    url = 'https://ws.api.cnyes.com/charting/api/v1/history?resolution=D&symbol=TWS:%s:STOCK&from=%s&to=%s&quote=1' % (sid, _from, _to)
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        vecGetYear = np.vectorize(getYear)
        vecGetMonth = np.vectorize(getMonth)
        vecGetDay = np.vectorize(getDay)
        vecGetDate = np.vectorize(datetime.datetime.fromtimestamp)
        obj = json.loads(r.text)
        times = vecGetDate(obj['data']['t'])
        return np.flip(np.c_[vecGetYear(times), vecGetMonth(times), vecGetDay(times), obj['data']['o'], obj['data']['c'], obj['data']['h'], obj['data']['l'], obj['data']['v']], axis=0)
    
def updateAllSid():
    d, m, y = datetime.date.today().strftime("%d/%m/%Y").split('/')
    for sid in twstock.twse:
        saveHistoryDataSingleSid(sid, cur_year=int(y), cur_month=int(m), cur_day=int(d)+1)
        if sid == '9958':
            break

def saveHistoryDataSingleSid(sid,prev_year=2010, prev_month=1, prev_day=1, cur_year=2020, cur_month=4, cur_day=9):
    """ 
    return [year, month, day, price]

    """
 
    outdate = getHistoryDateSingleSid(sid, prev_year, prev_month, prev_day, cur_year, cur_month, cur_day)
    with open('../datas/historyDatas/' + sid + '.bin', 'wb') as f:
        f.write(outdate.tostring())

