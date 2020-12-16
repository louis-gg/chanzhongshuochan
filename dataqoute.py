# coding:utf8
from re import split
from pyecharts.charts.basic_charts.kline import Kline
import requests
from requests.api import head, request
import json
import datetime


'''
日：
kline_dayqfq={"code":0,"msg":"","data":{"hk01082":{"qfqday":[["2019-09-03","0.810","0.820","0.820","0.810","304000.000",{},"0.000","24.628"],["2019-09-04","0.780","0.790","0.790","0.780","1400000.000",{},"0.000","109.208"],["2019-09-05","0.760","0.770","0.780","0.760","472000.000",{},"0.000","36.276"],
https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_dayqfq&param=hk01082,day,,,320,qfq&r=0.740469290856042

周：
kline_weekqfq={"code":0,"msg":"","data":{"hk01082":{"qfqweek":[["2014-10-17","1.586","1.464","1.586","1.450","520726000.000",{},"0.000","9857.681"],["2014-10-24","1.468","1.361","1.486","1.336","183536000.000",{},"0.000","2871.940"],["2014-10-31","1.361","1.364","1.418","1.325","280686000.000",{},"0.000","4111.772"],["2014-11-07","1.350","1.371","1.407","1.318","108458000.000",{},"0.000","1559.885"],["2014-11-14","1.371","1.375","1.411","1.346","122104000.000",
https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_weekqfq&param=hk01082,week,,,320,qfq&r=0.005481024716898597

月：
kline_monthqfq={"code":0,"msg":"","data":{"hk01082":{"qfqmonth":[["2011-07-29","6.754","5.539","6.861","5.396","118660051.000",{},"0.000","16862.541"],["2011-08-31","5.539","4.325","5.539","4.075","13322700.000",{},"0.000","1547.295"],["2011-09-30","4.325","3.539","4.325","3.075","1244000.000",{},"0.000","100.408"],
https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_monthqfq&param=hk01082,month,,,320,qfq&r=0.6635249910650687

实时：
v_r_hk01082="100~香港教育国际~01082~1.300~1.300~0.000~0.0~0~0~1.300~0~0~0~0~0~0~0~0~0~1.300~0~0~0~0~0~0~0~0~0~0.0~2020/12/16 09:20:17~0.000~0.00~1.300~1.300~1.300~0.0~0.000~0~-7.05~~0~0~0.00~7.5539~7.5539~HK EDU INTL~0.00~1.390~0.610~0.00~39.29~0~0~0~0~0~-7.05~7.00~0.00~4000~62.50~~GP~-12.82~-9.19";
https://web.sqt.gtimg.cn/q=r_hk01082?r=0.07942820340450552

'''

class DataQoute:
    def __init__(self,code):
        #实时价格
        '''
        http://hq.sinajs.cn/list=sh601006
        '''
        self.time_data_api = 'http://hq.sinajs.cn/list='
        '''
        最近二十天左右的每5分钟数据
        http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000001&scale=5&ma=5&datalen=1023
       （参数：股票编号、分钟间隔（5、15、30、60、240、1200）、均值（5、10、15、20、25）、查询个数点（最大值242））
        '''
        #历史数据
        self.mink_data_api= 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?'
        
        
        self.hk_day_api='https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_dayqfq&param=%s,day,,,1000,qfq&r=0.740469290856042'
        self.hk_week_api='https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_weekqfq&param=%s,week,,,1000,qfq&r=0.005481024716898597'
        self.hk_month_api ='https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_monthqfq&param=%s,month,,,320,qfq&r=0.6635249910650687'
        
        self.header = {
            'Accept-Encoding':
            'gzip, deflate, sdch',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
        }
        self.code = code
        self.name =""
        self.session = requests.session()
    
    def GetTimeData(self):
        request_url = self.time_data_api +self.code
        r = self.session.get(request_url,headers = self.header)
        #sh601006=大秦铁路,6.600,6.600,6.550,6.610,6.530,6.540,6.550,16365460,107231427.000,214838,6.540,859590,6.530,689800,6.520,10359
        splits=r.text.split("=")[1].replace('"','').split(",")
        self.name=splits[0]
        time_data=dict(
                code=self.code,
                name=splits[0],
                open=float(splits[1]),
                close=float(splits[2]),
                now=float(splits[3]),
                high=float(splits[4]),
                low=float(splits[5]),
                buy=float(splits[6]),
                sell=float(splits[7]),
                turnover=int(splits[8]),
                volume=float(splits[9]),
                bid1_volume=int(splits[10]),
                bid1=float(splits[11]),
                bid2_volume=int(splits[12]),
                bid2=float(splits[13]),
                bid3_volume=int(splits[14]),
                bid3=float(splits[15]),
                bid4_volume=int(splits[16]),
                bid4=float(splits[17]),
                bid5_volume=int(splits[18]),
                bid5=float(splits[19]),
                ask1_volume=int(splits[20]),
                ask1=float(splits[21]),
                ask2_volume=int(splits[22]),
                ask2=float(splits[23]),
                ask3_volume=int(splits[24]),
                ask3=float(splits[25]),
                ask4_volume=int(splits[26]),
                ask4=float(splits[27]),
                ask5_volume=int(splits[28]),
                ask5=float(splits[29]),
                date=splits[30],
                time=splits[31],
            )
        print(time_data)
        print(r.text)
        
    '''
    5
    15
    30
    60
    240 日
    1200 周
    '''
    def GetKData(self,freq):
        param = 'symbol=%s&scale=%s&ma=5&datalen=1000'%(self.code,freq)
        time_fomart ='%Y-%m-%d %H:%M:%S'
        if freq =='240' or freq == '1200':
            time_fomart='%Y-%m-%d'
        request_url = self.mink_data_api+param
        r=self.session.get(request_url,headers=self.header)
        klines =json.loads(r.text)
        for i in range(len(klines)):
            klines[i]["date"]=klines[i]["day"] #datetime.datetime.strptime(klines[i]["day"],time_fomart) 
            klines[i]['code']=self.code
            del klines[i]["day"]
        return klines
    
    '''
    day 日
    week 周
    month 月
    '''
    def GetHkKData(self,freq):
        request_url = ""
        data_key=""
        if freq=="day":
            request_url=self.hk_day_api%(self.code)
            data_key="qfqday"
        elif freq=="week":
            request_url = self.hk_week_api%(self.code)
            data_key="qfqweek"
        elif freq=="month":
            request_url = self.hk_month_api%(self.code)
            data_key='qfqmonth'
        else:
            print("error,freq is error")
            return []
        r=self.session.get(request_url,headers = self.header)
        data_text = r.text.split("=")[1]
        data=json.loads(data_text)
        kdatas = data['data'][self.code][data_key]
        '''
        ['2020-12-16', '7.700', '7.770', '7.830', '7.580', '142194865.00', {}, '0', '110189.61']
        '''
        klines =[]
        for  i in range (len(kdatas)):
            current_kdata= kdatas[i]
            kline={}
            kline['date']= current_kdata[0]
            kline['code']=self.code
            kline['open']=float(current_kdata[1])
            kline['close']=float(current_kdata[2])
            kline['high']=float(current_kdata[3])
            kline['low']=float(current_kdata[4])
            kline['amount']=float(current_kdata[5])
            kline['volume']=float(current_kdata[8])
            klines.append(kline)
            
        return klines
        
        
            
            
          
        
if __name__ == "__main__":
    code ='hk01093'
    data_qoute=DataQoute(code)
    klines=data_qoute.GetHkKData("day")
    print(len(klines))
    print('==========================')

    data_qoute.GetKData("240")
        
        
        
        
        