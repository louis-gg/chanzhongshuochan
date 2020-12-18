from numpy.lib.function_base import select
from numpy.lib.shape_base import tile
import pandas as pd
import  numpy as np
from pyecharts.charts import  Kline,Bar,Grid
from pyecharts import options as opts
from pyecharts.options.series_options import LabelOpts
from dataqoute import DataQoute
import json





'''
缠中说禅分析
'''


        

'''
笔 分型
'''
class ChanAnalyze:

    def __init__(self,klines):
        self.klines_orig = klines #原始K线
        self.klines_merge=[] #合并后的K线
        self.fxs=[] #分型
        self.fbs=[] #笔列表
        self.status="未确定"
        self.merge()
        self.check_merge()
        self.klinefx()
        self.klinefb()
        self.update_status()
        #self.draw()
    
    '''
    数据绘制分段
    '''
    def split_data_part(self) :
        mark_line_data = []
        idx = 0
        for i in range(len(self.klines_merge)):
            for bi in self.fbs:
                if bi['fx']["k2"]["date"] == self.klines_merge[i]['date']:
                    mark_line_data.append(
                        [
                        {
                            "xAxis":idx,
                            "yAxis":self.klines_merge[idx]['high'] if bi["mark"] == 'l' else self.klines_merge[idx]['low'],
                        },
                        {
                            "xAxis":i,
                            "yAxis":bi['price'],
                        }
                        ]
                    )
                    idx=i
                    break
        return mark_line_data
    
    '''
    绘制
    '''
    def draw(self,freq=""):
        kdata=[]
        ktime=[]
        kvol=[]
        for i in range(len(self.klines_merge)):
            current_kline = self.klines_merge[i]
            onedata=[]
            onedata.append(current_kline['open'])
            onedata.append(current_kline['close'])
            onedata.append(current_kline['low'])
            onedata.append(current_kline['high'])
            kdata.append(onedata)
            ktime.append(current_kline['date'])
            kvol.append(current_kline['volume'])
        kline=(Kline().add_xaxis(ktime)
               .add_yaxis(series_name= self.klines_merge[0]['code'],y_axis= kdata,
                          markline_opts=opts.MarkLineOpts(label_opts=opts.LabelOpts(position="middle", color="blue", font_size=15),
                                                          data=self.split_data_part(),
                                                          symbol=["circle", "none"],),
                          )
               .set_global_opts(xaxis_opts=opts.AxisOpts(is_scale=True),
                                yaxis_opts=opts.AxisOpts(is_scale=True,
                                                         splitarea_opts=opts.SplitAreaOpts(is_show=True,areastyle_opts=opts.AreaStyleOpts(opacity=1)),
                                                         ),
                                datazoom_opts = [opts.DataZoomOpts()],
                                title_opts=opts.TitleOpts(title=self.klines_merge[0]['code']) ,
                                ) 
               .set_series_opts(
                   markarea_opts=opts.MarkAreaOpts(is_silent=True, data=self.split_data_part())
                   )
               )
        
        bar = (Bar().add_xaxis(ktime).add_yaxis("",kvol))
        path =self.klines_merge[0]['code']+"-"+freq+".html";
        kline.render(path)

  
        
    '''
    检查函数
    '''
    def check_merge(self):
        for i in range(len(self.klines_merge)-1,-1,-1):
            if i <1:
                return
            curent_kline=self.klines_merge[i]
            second_kline = self.klines_merge[i-1]
            if (curent_kline['low'] <= second_kline['low'] and curent_kline['high'] >= second_kline['high']) or \
                (curent_kline['low'] >= second_kline['low'] and curent_kline['high'] <= second_kline['high']):
                    print("wrong merge")
                    print(curent_kline)
                    print(second_kline)
    
    def has_kine(self,begin,end):
        b_start = False
        for i in range (self.klines_merge):
            current_kline = self.klines_merge[i]
            if current_kline['date'] == begin:
                b_start=True
                continue
            if b_start and current_kline['date'] < end:
                return True
        return False
    
    '''
    更新状态为上涨、分型、下跌
    '''
    def update_status(self):
        if len(self.fbs) > 0:
            if self.fbs[-1]['fx']['k3']['date'] == self.klines_merge[-1]['date']:
                if self.fbs[-1]['fx']['mark'] =='h' :
                    self.status="顶分型"
                else:
                    self.status="底分型"
            else:
                if self.fbs[-1]['fx']['mark'] =='h' :
                    self.status="下降笔"
                else:
                    self.status="上升笔"
                           
    '''
    笔划分
    {'fx': {'mark': 'h', 'low': 16.54, 'high': 18.1,
    'k1': {'date': '2020-10-16', 'code': 'sz.000001', 'open': 16.56, 'high': 17.37, 'low': 16.54, 'close': 17.1, 'volume': 209561419, 'amount': 3589229558.57, 'adjustflag': 2}, 
    'k2': {'date': '2020-10-19', 'code': 'sz.000001', 'open': 17.3, 'high': 18.1, 'low': 17.3, 'close': 17.48, 'volume': 201610552, 'amount': 3571336006.25, 'adjustflag': 2}, 
    'k3': {'date': '2020-10-20', 'code': 'sz.000001', 'open': 17.48, 'high': 17.6, 'low': 17.25, 'close': 17.54, 'volume': 96007195, 'amount': 1673173355.65, 'adjustflag': 2}, 
    'date': '2020-10-19'}, 
    'mark': 'h', 'price': 18.1}
    '''
    def klinefb(self,bold=False):
        fxlen = len(self.fxs)
        if fxlen < 2:
            print("fx is less then 2")
        fx_count= len(self.fxs)
        for i in range (fx_count):
            current_fx = self.fxs[i]
            if len(self.fbs)==0:
                current_bi = {}
                current_bi['fx']= current_fx
                current_bi['mark']=current_fx['mark']
                current_bi['price']=current_fx['k2']['low'] if current_fx['mark']== 'l' else current_fx['k2']['high']
                self.fbs.append(current_bi)
            else:
                last_bi = self.fbs[-1]
                current_bi={}
                if last_bi['mark'] == "l":
                    #延续
                    if current_fx['mark'] == 'l':
                        if  current_fx['k2']['low'] <last_bi['price']:
                            self.fbs[-1]['fx']=current_fx
                            self.fbs[-1]['price']=current_fx['k2']['low']
                    if current_fx['mark']=='h':
                        #不共用K线
                        if current_fx["k1"]['date'] > last_bi['fx']['k3']['date']:
                            #老笔必须有独立k
                            if bold == True and self.has_kine(last_bi['fx']['k3']['date'],current_fx["k1"]['date']):
                                current_bi = {}
                                current_bi['fx']= current_fx
                                current_bi['mark']=current_fx['mark']
                                current_bi['price']=current_fx['k2']['high'] 
                                self.fbs.append(current_bi)
                            else:
                                current_bi = {}
                                current_bi['fx']= current_fx
                                current_bi['mark']=current_fx['mark']
                                current_bi['price']=current_fx['k2']['high'] 
                                self.fbs.append(current_bi)
                if last_bi['mark'] == "h":
                    #延续
                    if current_fx['mark'] == 'h':
                        if  current_fx['k2']['high'] >last_bi['price']:
                            self.fbs[-1]['fx']=current_fx
                            self.fbs[-1]['price']=current_fx['k2']['high']
                    if current_fx['mark']=='l':
                        #不共用K线
                        if current_fx["k1"]['date'] > last_bi['fx']['k3']['date']:
                            #老笔必须有独立k
                            if bold == True and self.has_kine(last_bi['fx']['k3']['date'],current_fx["k1"]['date']):
                                current_bi = {}
                                current_bi['fx']= current_fx
                                current_bi['mark']=current_fx['mark']
                                current_bi['price']=current_fx['k2']['low'] 
                                self.fbs.append(current_bi)
                            else:
                                current_bi = {}
                                current_bi['fx']= current_fx
                                current_bi['mark']=current_fx['mark']
                                current_bi['price']=current_fx['k2']['low'] 
                                self.fbs.append(current_bi)                
                    
    '''
    分型
    {'fx': {'mark': 'l', 'low': 15.12, 'high': 15.27, 
    'k1': {'date': '2020-09-24', 'code': 'sz.000001', 'open': 15.59, 'high': 15.61, 'low': 15.12, 'close': 15.12, 'volume': 106101124, 'amount': 1623376200.81, 'adjustflag': 2}, 
    'k2': {'date': '2020-09-25', 'code': 'sz.000001', 'open': 15.2, 'high': 15.27, 'low': 14.76, 'close': 15.19, 'volume': 61408700, 'amount': 933035044.47, 'adjustflag': 2}, 
    'k3': {'date': '2020-10-09', 'code': 'sz.000001', 'open': 15.3, 'high': 15.55, 'low': 15.13, 'close': 15.18, 'volume': 90042593, 'amount': 1376995906.6, 'adjustflag': 2},
    'date': '2020-10-09'
    }
    '''      
    def klinefx(self):
        if len(self.klines_merge) <3:
            print("kline_merge is less")
            return
        
        for i in range (len(self.klines_merge)):
            if i < 2:
                continue
            first_k = self.klines_merge[i-2]
            second_k= self.klines_merge[i-1]
            third_k=self.klines_merge[i]
 
            if (second_k['high'] > first_k['high'] and second_k['high'] > third_k['high'] )and \
                (second_k['low'] > first_k['low'] and second_k['low'] > third_k['low']):

                    fx={}
                    fx['mark']='h'
                    fx['low']=first_k['low']
                    fx['high']=second_k['high']
                    fx['k1']=first_k
                    fx['k2']=second_k
                    fx['k3']=third_k
                    fx['date']=second_k['date']
                    self.fxs.append(fx)
            if (second_k['low'] < first_k['low'] and second_k['low'] < third_k['low']) and \
                (second_k['high'] < first_k['high'] and second_k['high'] < third_k['high']):

                    fx={}
                    fx['mark']='l'
                    fx['low']=first_k['low']
                    fx['high']=second_k['high']
                    fx['k1']=first_k
                    fx['k2']=second_k
                    fx['k3']=third_k
                    fx['date']=third_k['date']                    
                    self.fxs.append(fx)
            
            
    '''
    合并
    ''' 
    def merge(self):
        """
        docstring
        """
        if len(self.klines_orig) <=2:
             self.klines_merge=self.klines_orig
             return
        direct="unkonw"
        for i in range(len(self.klines_orig)):
            curent_kline = self.klines_orig[i]
            if len(self.klines_merge) < 3 :
                #为了防止开始的K线合并，所以去掉合并的K线再进行
                if len(self.klines_merge) >0:
                    second_kline = self.klines_merge[-1]
                    if (curent_kline['low'] <= second_kline['low'] and curent_kline['high'] >= second_kline['high']) or \
                        (curent_kline['low'] >= second_kline['low'] and curent_kline['high'] <= second_kline['high']):  
                            continue
              
                self.klines_merge.append(curent_kline)                  
            else:                
                first_kline = self.klines_merge[-2]
                second_kline = self.klines_merge[-1]
                if first_kline['high'] < second_kline['high'] and first_kline['low'] < second_kline['low']:
                    direct = "up"
                if first_kline['high'] > second_kline['high'] and first_kline['low'] > second_kline['low']:
                    direct = "down"
                if  direct=="unkonw":
                    print("erro direct")
                    continue
                if (curent_kline['low'] <= second_kline['low'] and curent_kline['high'] >= second_kline['high']) or \
                    (curent_kline['low'] >= second_kline['low'] and curent_kline['high'] <= second_kline['high']):
                    if direct == 'up':
                        maxhigh = max(curent_kline['high'], second_kline['high'])
                        maxlow = max(curent_kline['low'], second_kline['low'])
                        self.klines_merge[-1]['high']=maxhigh
                        self.klines_merge[-1]['low']=maxlow
                    if direct =="down":   
                        minhigh = min(curent_kline['high'], second_kline['high'])
                        minlow = min(curent_kline['low'], second_kline['low'])
                        self.klines_merge[-1]['high']=minhigh
                        self.klines_merge[-1]['low']=minlow
                else:
                     self.klines_merge.append(curent_kline)                       
    
    
    '''
    底分型买点
    '''
    def lfxbuy(self):
        fx_count=len(self.fxs)
        if fx_count >0:
            fx_tail = self.fxs[-1]
            if fx_tail['mark'] == 'l' and fx_tail['k3']['date'] == self.klines_merge[-1]['date']:
                return True,fx_tail['high'],fx_tail['low']
        return False,0,0
    
    '''
    强底分型
    '''
    def stronglfxbuy(self):
        blfx,high,low = self.lfxbuy()
        if blfx:
            fx_tail = self.fxs[-1]
            if fx_tail['k3']['low'] >= high:
                return True,high,low
        return False,0,0
                
    '''
    笔三买判断
    '''
    def thirdbuy(self,bstrong= True):
        if len(self.fbs) > 6:
            bilist = self.fbs[-6:]
            if bilist[-1]['mark'] == 'l':
                gg_max=max([x["price"] for x in bilist[:4] if x["mark"] =='h'])
                dd_min = min([x['price'] for x in bilist[:4] if x['mark']=='l'])
                zs_max = min([x["price"] for x in bilist[:4] if x["mark"] =='h'])
                zs_min= max([x['price'] for x in bilist[:4] if x['mark']=='l'])
                if bstrong:
                    if bilist[-1]['price'] > gg_max and zs_max >= zs_min and self.klines_merge[-1]["low"] > bilist[-1]['price'] and bilist[0]['price'] < zs_min :
                        return True,zs_max
                    
                else:
                    if bilist[-1]['price'] > zs_max and zs_max >= zs_min and self.klines_merge[-1]["low"] > bilist[-1]['price']  and bilist[0]['price'] < zs_min:
                        return True,zs_max               
        return False,0  
        
             
            
        
    

if __name__ == "__main__":
    
    
    

    '''
    数据格式
    {'date': '2020-10-16', 'code': 'sz.000001', 'open': 16.56, 'high': 17.37, 
    'low': 16.54, 'close': 17.1, 'volume': 209561419, 'amount': 3589229558.57, 'adjustflag': 2}
  
    '''
    dataqout = DataQoute()
    dataqout.GetHkCodes()
    hk_codes = dataqout.hk_codes
    for code in hk_codes.keys():
        dataqout.SetCode(code)
        kline_day=dataqout.GetHkKData("day")
        if len(kline_day) > 0 :
            chan_day=ChanAnalyze(kline_day)
            bthird_buy,price=chan_day.thirdbuy(bstrong=False)
            if bthird_buy:
                chan_day.draw(code+"_"+hk_codes[code]['name'])

   