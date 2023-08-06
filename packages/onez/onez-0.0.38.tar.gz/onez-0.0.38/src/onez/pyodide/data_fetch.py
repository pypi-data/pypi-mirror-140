# import libraries
import pandas as pd
from js import fetch
from io import StringIO
from io import BytesIO
from src import config

#url = "http://127.0.0.1:5000/api"
url = config.url
#"https://finance.99onez.com/api"

def getData(name,type,startDate='',endDate=''):
    if isinstance(name, int):
        return getDataByType(name,type)

#兼容大数据工具平台获得后台数据   pyodide 单独使用
async def getDataByType(type,content):
    response = await fetch( url + '/bigDataCentre/getDataByType?content=' + content + '&type=' +str(type));
    js_buffer = await response.arrayBuffer()
    img =pd.DataFrame(BytesIO(js_buffer.to_py()))
    s=str(img[0][0],'utf-8')
    data = StringIO(s)
    df=pd.read_json(data)
    return df

