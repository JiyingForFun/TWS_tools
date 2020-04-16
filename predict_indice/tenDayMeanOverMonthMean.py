
import matplotlib.pyplot as plt
import numpy as np
import twstock
import mplfinance as mpf
from downloadHistoryDatas import *

def movingAverage(list, size):
    if size > len(list):
        size = len(list)
    return [ list[i:i+size].mean() for i in range(len(list)-size)]
        

def predictBuyMA10overMA20(datas, hold_days=3):
    #if ((len(datas) < (25+hold_days))|(datas[-1,1] <= 50)):
    if ((len(datas) < (25+hold_days))|(datas[-1,1] > 50)):
        return False
    
    ma10 = movingAverage(datas[:,1], 10)
    ma20 = movingAverage(datas[:,1], 20)
    buy = True
    diff = 100000
    for i in range (hold_days)[::-1]:
        i += 1

        diff_  = ma20[ -i] - ma10[-i]
        #if i > 1:
        #    buy = buy &(diff_ > 0) & (diff > diff_)
        #else:
        #    buy = buy &(diff_ < 0) & (diff > diff_)
        buy = buy &(diff_ > 0) & (diff > diff_)
        diff = diff_
    return buy

def showPlot(datas):
    size = len(datas) 
    plt.plot(range(size), datas)
    plt.plot(np.arange(10, len(datas), 1), movingAverage(datas, 10), label='10')
    plt.plot(np.arange(20, len(datas), 1), movingAverage(datas, 20), label='20')
    plt.plot(np.arange(60, len(datas), 1), movingAverage(datas, 60), label='60')
    plt.legend()
    plt.show()

def retrieveTargetSid():
    for sid in twstock.twse:
        
        a = loadHistoryDataSingleSid('../datas/historyDatas/%s.bin' %(sid))
        if predictBuyMA10overMA20(a.values[-50:], 5):
            print(sid)
            with open('20200408_predict_better.csv', 'a') as f:
                f.write('%s, %.1f\n' %(sid, a.values[-1, 1]))
            #showPlot(a.values[-30:])
        if sid == '9958':
            break;
def indexMA10MA20():
    for sid in twstock.twse:
        a = loadHistoryDataSingleSid('../datas/historyDatas/%s.bin' %(sid))
        if predictBuyMA10overMA20(a.values[-50:], 1):
            print (sid)
           # showPlot(a.values[-70:, 1])
            mpf.plot(a[-70:], type='candle', mav=(10, 20, 30), volume=True)
        if sid == '9958':
            break;


def verifyIndice(prev_days=2, showWorse=False, showImp=False):
    improve = []
    worse = []
    total = []
    cs = []
    ma10s = []
    ma20s = []
    for sid in twstock.twse:
        a = loadHistoryDataSingleSid('../datas/historyDatas/%s.bin' %(sid))
        if len(a.values) < (prev_days+100):
            continue
        if predictBuyMA10overMA20(a.values[-prev_days-50:-prev_days], 5):
            print (sid)
            diff = a.values[-prev_days, 1] - a.values[-prev_days-1,1]
            total.append(a.values[-prev_days,1])
            cs.append(a.values[-prev_days-50:-prev_days,1])
            ma10s.append(movingAverage(a.values[-prev_days-50:-prev_days,1],10))
            ma20s.append(movingAverage(a.values[-prev_days-50:-prev_days,1],20))
            if diff > 0:
                improve.append(diff)
                if showImp:
                    showPlot(a.values[-prev_days-100:-prev_days, 1])
            else:
                worse.append(diff)
                if showWorse:
                    showPlot(a.values[-prev_days-100:-prev_days, 1])
        if sid == '9958':
            break;
    print('improve number:', len(improve))
    print('worse number:', len(worse))
    print('improve price:', np.sum(improve))
    print('worse price:', np.sum(worse))
    print('total price:', np.sum(total))
    size = len(cs[0]) 
    plt.plot(range(size), np.mean(cs, axis=0), label='day')
    plt.plot(np.arange(10, size, 1), np.mean(ma10s, axis=0), label='10')
    plt.plot(np.arange(20, size, 1), np.mean(ma20s, axis=0), label='20')
    plt.legend()
    plt.show()
    return improve, worse, total

