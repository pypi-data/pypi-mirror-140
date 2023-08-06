# import libraries
import requests
import numpy as np
import pandas as pd

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}
#url = "http://127.0.0.1:5000/api"
url = "https://finance.99onez.com/api"

def getIndustry(name,type,startDate=None,endDate=None):

    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    page = requests.get(url+'/industry2?name='+name+'&type='+type+'&startDate='+str(startDate)+'&endDate='+str(endDate), headers)
    return page.json()

def getConcept(name,type,startDate=None,endDate=None):
    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    #print(url)
    page = requests.get(url+'/concept?name='+name+'&type='+type+'&startDate='+str(startDate)+'&endDate='+str(endDate), headers)
    return page.json()

def getConceptArr(nameArr,type,startDate=None,endDate=None):
    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    #print(url)
    page = requests.get(url+'/conceptArr?&type='+type+'&startDate='+str(startDate)+'&endDate='+str(endDate), params={"name":nameArr} )
    return page.json()

def getData(name,type,startDate='',endDate=''):
    if isinstance(name, int):
        return getDataByType(name,type)
    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    page = requests.get(url+'/code?name='+name+'&type='+type+'&startDate='+str(startDate)+'&endDate='+str(endDate), headers)
    return page.json()

#兼容大数据工具平台获得后台数据
def getDataByType(type,content):
    page = requests.get( url + '/bigDataCentre/getDataByType?content=' + content + '&type=' +str(type)  ,headers)
    df = pd.DataFrame(page.json())
    return df


def getDataByName(name,type,startDate='',endDate=''):
    page = requests.get(url+'/code?name='+name+'&type='+type+'&startDate='+str(startDate)+'&endDate='+str(endDate), headers)
    return page.json()


#获得财务报表的数据
def getAnnalReportData(industry,yearArr,companyList):
    #industry,yearArr,companyList
    page = requests.get(url+'/getAnnalReportAuditKeyData?industry='+industry, params={"yearArr":yearArr,"companyList":companyList})
    return page.json()
