import requests
import json

headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
}


def getStockTickData(code):
    url ='http://hq.cs.ecitic.com/cssweb?type=GET_TICK&exchange=%s&stockcode=%s' % (code[:2],code[2:])
    r = requests.get(url, headers = headers)
    return json.loads(r.text)


def getStockGridData(codes):
    if type(codes) is not list: return
    url = 'http://hq.cs.ecitic.com/cssweb?type=GET_GRID_QUOTE&stockcode=%s' % ','.join(codes)
    r = requests.get(url, headers = headers)
    return json.loads(r.text)


if __name__ == '__main__': 
    p1 = getStockTickData('sh603938')
    for key,val in p1.items():
        print(key)
        print(val)