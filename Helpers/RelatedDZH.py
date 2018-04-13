import struct
import time
import re
import urllib.request
import datetime
from pandas.compat import StringIO
import pandas as pd
import requests

columns=[
        # 'code'                                  # 代码
        'issue_date',                              # 公布日期
        'report_date',                             # 报告日期
        'market_date',                             # 上市日期
        'eps',                                     # 每股收益
        'bvps',                                    # 每股净资产
        'return_on_net_assets',                    # 净资产收益率
        'operating_cash_per_share',                # 每股经营现金
        'provident_fund_per_share',                # 每股公积金
        'per_share_not_assigned',                  # 每股未分配
        'shareholder_equity_ratio',                # 股东权益比
        'net_profit_year_on_year',                 # 净利润同比
        'main_revenue_year_on_year',               # 主营收入同比
        'sales_gross_margin',                      # 销售毛利率
        'the_adjustment_of_net_asset_per_share',   # 调整每股净资
        'total_assets',                            # 总资产  无小数
        'current_assets',                          # 流动资产   无小数
        'fixed_assets',                            # 固定资产
        'intangible_assets',                       # 无形资产  无小数
        'current_liabilities',                     # 流动负债  无小数
        'long_term_liabilities',                   # 长期负债
        'total_liabilities',                       # 总负债
        'shareholder_equity',                      # 股东权益
        'capital_accumulation_fund',               # 资本公积金
        'operating_cash_flow',                     # 经营现金流量
        'investment_cash_flow',                    # 投资现金流量   无小数
        'financing_cash_flow',                     # 筹资现金流量
        'increase_in_cash',                        # 现金增加额
        'main_income',                             # 主营收入
        'main_profit',                             # 主营利润
        'operating_profit',                        # 营业利润
        'income_from_investment',                  # 投资收益
        'nonoperating_revenues_and_expenses',      # 营业外收支
        'gross_profit',                            # 利润总额
        'net_profit',                              # 净利润
        'retained_profit',                         # 未分配利润
        'total_shares',                            # 总股本
        'unlimited_sales_shares',                  # 无限销售股合计
        'a_share',                                 # A股
        'b_share',                                 # B股
        'overseas_listed_shares',                  # 境外上市股
        'other_tradable_shares',                   # 其他流通股
        'total_restricted_shares',                 # 限售股合计
        'state_holding_shares',                    # 国家持股
        'state_owned_legal_person_shares',         # 国有法人股
        'domestic_legal_person_shares',            # 境内法人股
        'domestic_natural_person_shares',          # 境内自然人股
        'other_promoters_shares',                  # 其他发起人股
        'raise_legal_person_shares',               # 募集法人股
        'foreign_legal_person_shares',             # 境外法人股
        'overseas_natural_person_shares',          # 境外自然人股
        'preferred_stock',                         # 优先股
        'other',                                   # 其他
    ]


def get_except_365_net():
    path = 'http://filedown.gw.com.cn/download/PWR/'
    name = ['full_sh.PWR','full_sz.PWR']
    data = []
    for i in name:
        request = requests.get(path+i)
        request = request.content[8:]

        for i in range(0,len(request),120):
            temp = request[i:i+120]
            if temp[:4] == b'\xff\xff\xff\xff':
                code = temp[4:12].decode('gbk')
            else:
                date= struct.unpack("I", temp[:4])[0]
                date= time.localtime(date)
                date= datetime.datetime(date.tm_year,date.tm_mon,date.tm_mday)

                exlist = temp[20:].decode('gbk').split('\x00')[0][2:].split()
                present = 0
                bonus = 0
                rationed = 0
                price = 0

                for i in exlist:
                    if '送' in i:
                        present += float(re.findall(r"\d+\.?\d*",i)[0])
                    if '增' in i:
                        present += float(re.findall(r"\d+\.?\d*",i)[0])
                    if '派' in i:
                        bonus += float(re.findall(r"\d+\.?\d*",i)[0])
                    if '价' in i:
                        price += float(re.findall(r"\d+\.?\d*",i)[0])
                    if '配' in i:
                        rationed += float(re.findall(r"\d+\.?\d*",i)[0]) - price
                data.append(dict(
                    code = code[2:],
                    date = date,
                    present = present,
                    bonus = bonus,
                    price = price,
                    rationed = rationed
                    ))
    return data

# 从网络获取财务数据
def get_finance_365_net():
    path = 'http://filedown.gw.com.cn/download/FIN/'
    name = ['full_sh.FIN','full_sz.FIN']
    data = []
    for i in name:
        request = requests.get(path+i)
        finance = request.content[8:]
        for i in range(0,len(finance),224):
            dicts = {}
            temp = finance[i:i+224]
            code = temp[0:12].decode('gbk')[2:8]
            dicts['code'] = code
            for j in range(0,len(temp[12:]),4):
                if j < 12:
                    date = struct.unpack("i", temp[12+j:12+4+j])[0]
                    date = datetime.datetime.strptime(str(date),'%Y%m%d') if date > 0 else None
                    dicts[columns[int(j/4)]] = datetime.date(date.year,date.month,date.day)

                elif j <= 204:
                    dicts[columns[int(j/4)]] = struct.unpack("f", temp[12+j:12+4+j])[0]
            data.append(dicts)
    return data

def get_finance_365_local():
    data = []
    path='f:/cc/FIN/'
    name = ['full_sh.FIN','full_sz.FIN']
    for i in name:
        exFile=open(path+i ,'rb')
        exFile.seek(8)
        while True:
            code = exFile.read(12)
            if not code:
                break
            dicts = {}
            code = code[:8].decode('gbk')[2:]
            dicts['code'] = code
            for i in range(53):
                if i < 3:
                    date = struct.unpack("i", exFile.read(4))[0]
                    date = datetime.datetime.strptime(str(date),'%Y%m%d') if date > 0 else None
                    dicts[columns[i]] = datetime.date(date.year,date.month,date.day)
                elif 3 <= i <= 51:
                    dicts[columns[i]] = struct.unpack("f", exFile.read(4))[0]
                else:
                    exFile.read(4)
            data.append(dicts)
    return data

if __name__ == '__main__':

    e = get_finance_365_local()
    print(e)
    # for i in e[1]:
    #     print(type(e[1][i]))
    # print(e)
    # print(len(e))
