#--coding:utf-8--
import re
import requests

from Quotation.Base import Base
from Helpers.RelatedCode import get_all_codes,get_code_list,perfectCode

class Sina(Base):
    max_num = 800
    Realtime_API = 'http://hq.sinajs.cn/?format=text&list='
    HistData_API = 'http://money.finance.sina.com.cn/quotes_service/api/jsonp_v2.php/var=/CN_MarketData.getKLineData?symbol=%s&scale=%s&ma=no&datalen=%s'

    grep_detail = re.compile(r'(\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))
    grep_detail_with_prefix = re.compile(r'(\w{2}\d+)=([^\s][^,]+?)%s%s' % (r',([\.\d]+)' * 29, r',([-\.\d:]+)' * 2))

    def formatRealtimeData(self, rep_data, prefix=False):
        stocks_detail = ''.join(rep_data)
        grep_str = self.grep_detail_with_prefix if prefix else self.grep_detail
        result = grep_str.finditer(stocks_detail)
        stock_dict = dict()
        for stock_match_object in result:
            stock = stock_match_object.groups()
            stock_dict[stock[0]] = dict(
                name=stock[1],
                open=float(stock[2]),
                close=float(stock[3]),
                now=float(stock[4]),
                high=float(stock[5]),
                low=float(stock[6]),
                buy=float(stock[7]),
                sell=float(stock[8]),
                turnover=int(stock[9]),
                volume=float(stock[10]),
                bid1_volume=int(stock[11]),
                bid1=float(stock[12]),
                bid2_volume=int(stock[13]),
                bid2=float(stock[14]),
                bid3_volume=int(stock[15]),
                bid3=float(stock[16]),
                bid4_volume=int(stock[17]),
                bid4=float(stock[18]),
                bid5_volume=int(stock[19]),
                bid5=float(stock[20]),
                ask1_volume=int(stock[21]),
                ask1=float(stock[22]),
                ask2_volume=int(stock[23]),
                ask2=float(stock[24]),
                ask3_volume=int(stock[25]),
                ask3=float(stock[26]),
                ask4_volume=int(stock[27]),
                ask4=float(stock[28]),
                ask5_volume=int(stock[29]),
                ask5=float(stock[30]),
                date=stock[31],
                time=stock[32],
            )
        return stock_dict

    def getHistoryData(self, code, unit='d', datalen = 0):
        code = code if len(code) > 6 else perfectCode(code)+code
        datelen = {'d':'240','h':'60','i':'1'}
        datalen = datalen if datalen is None or datalen > 0 else 3000000
        url = self.HistData_API%(code,datelen[unit],str(datalen))
        try:
            r = requests.get(url, timeout=3)
        except:
            pass
        else:
            r = r.text
            if 'null' not in r:
                data = r[7:-3].split('},{')
                datas = []
                for i in range(0,len(data)):
                    column = {}
                    dayData = data[i].split(',')
                    for j in range(0,len(dayData)):
                        field = dayData[j].split(':"')
                        if field[0] == 'day':
                            column['date'] = field[1].replace('"', '')
                        else:
                            column[field[0]] = field[1].replace('"', '')
                    column['code'] = code[2:]
                    column['amount'] = 0
                    datas.append(column)
                return datas
        finally:
            pass

if __name__ == '__main__':

    a=Sina()
    import datetime
    s=datetime.datetime.now()
    # print(a.all)
    # print(len(a.all))
    # b=a.getHistoryData('sh600960',datalen=10)
    # b=a.getRealtimeData('sh000016')
    b=a.getRealtimeData(['sh000016','sz399005'])
    print(b)
    e=datetime.datetime.now()
    print(s,e,e-s)
