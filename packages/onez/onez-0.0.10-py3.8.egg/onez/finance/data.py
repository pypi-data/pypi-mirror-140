# import libraries
from datetime import datetime
import lxml
from lxml import html
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

url = "http://127.0.0.1:5000/api"

def getIndustry(name,type,startDate='',endDate=''):
    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    page = requests.get(url+'/industry2?name='+name+'&type='+type+'&startDate='+startDate+'&endDate='+endDate, headers)
    return page.json()

def getData(name,type,startDate='',endDate=''):
    if not startDate:
        startDate = ''
    if not endDate:
        endDate = ''
    page = requests.get(url+'/code?name='+name+'&type='+type+'&startDate='+startDate+'&endDate='+endDate, headers)
    return page.json()

def getDataByName(name,type,startDate='',endDate=''):

    page = requests.get(url+'/code?name='+name+'&type='+type+'&startDate='+startDate+'&endDate='+endDate, headers)
    return page.json()
