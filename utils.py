#!/usr/bin/python
# coding:utf-8
import json
import time
import pymysql
import requests
from pymysql import OperationalError

def getTime():
    '''获取当前日期时间'''
    return time.strftime("%Y{}%m{}%d{} %X").format("年","月","日")
def getconn():
    '''通用封装连接mysql'''
    conn = pymysql.connect(host='#', port=,user='#', password='#',db='Cov', charset="utf8")
    while True:
        try:
            conn.ping()
            break
        except OperationalError:
            conn.ping(True)
    # 创建游标
    cursor = conn.cursor()
    return conn, cursor
def closeconn(cursor,conn):
    '''通用关闭游标，数据库'''
    cursor.close()
    conn.close()
def getquery(sql,*args):
    '''通用查询sql,得到结果集
    return 返回查询到d的结果，((),(),)的形式
    '''
    conn,cursor = getconn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    closeconn(cursor,conn)
    return res

def getTotalData():
    """读取total_data表"""
    sql = 'select todayTime as 日期时间,localConfirm as 现有本土,confirm as 累计确诊,heal as 累计治愈,noInfect as 无症状现有 from total_data ORDER BY todayTime DESC'
    df_dict = getquery(sql)
    return df_dict[1]
def getDetailsData():
    """ 读取中国地图数据now_details表"""
    sql = 'select name as 省份,nowConfirm as 现有本土 from now_details;'
    return getquery(sql)
def getChinaTrendOption():
    """ 读取趋势图总数据total_data表"""
    sql = 'select todayTime as 日期时间,localConfirm as 现有本土,confirm as 累计确诊,heal as 累计治愈,noInfect as 无症状现有 from total_data ORDER BY todayTime ASC'
    return getquery(sql)
def getChinaAddTrendOption():
    '''读取趋势图全国本土病例 chinaAddTrend表'''
    sql = 'select todayTime as 日期时间,localConfirm as 现有本土,localConfirmH5 as 新增本土 from chinaAddTrend ORDER BY todayTime ASC'
    return getquery(sql)
def getContents():
    '''读取最新信息'''
    sql = 'select publicTime as 日期时间,title as 标题,source as 来源,titleUrl as 链接 from contents ORDER BY publicTime DESC'
    return getquery(sql)

def request_get_data():
    '''爬取数据'''
    url = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=statisGradeCityDetail,diseaseh5Shelf'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.44'
    }
    res = requests.post(headers=headers, url=url).text
    get_data = json.loads(res)['data']
    return get_data['diseaseh5Shelf']
def todayData():
    '''获取疫情总数据'''
    data = request_get_data()
    lastUpdateTime = data['lastUpdateTime'] #上次更新时间
    localConfirm = data['chinaTotal']['localConfirm'] #本土现有
    noInfect = data['chinaTotal']['noInfect']  # 无症状现有
    confirm =  data['chinaTotal']['confirm'] #累计确诊
    heal = data['chinaTotal']['heal'] #累计治愈
    return lastUpdateTime,localConfirm,confirm,heal,noInfect
def detailsData():
    '''获取疫情详情数据'''
    areaTree =request_get_data()['areaTree']
    detailsList = []
    for i in areaTree[0]['children']:
        # 省份数据
        for j in i['children']:
            city_name = j['name']  # 城市
            city_confirm = j['today']['confirm']  # 现有确诊
            detailsList.append([city_confirm,city_name])#返回更新语句
        province_name = i['name']  # 省份
        province_nowConfirm = i['total']['nowConfirm']  # 现有确诊
        detailsList.append([province_nowConfirm, province_name]) #返回更新语句
    return detailsList
def requestGetContent():
    '''爬取最新信息数据'''
    url = 'https://wechat.wecity.qq.com/api/THPneumoniaService/getAreaContents'
    headers = {
        ########}}
    get_contents_data = json.loads(requests.post(url=url, json=data, headers=headers).text)
    Data = []
    i=0 # id
    for contents in get_contents_data['args']['rsp']['contents']:
        i+=1
        publicTime = contents['publicTime']  # 公布时间
        title = contents['title']  # 内容
        source = contents['from']  # 来源
        titleUrl = contents['jumpLink']['url']  # 链接
        Data.append((i,publicTime,title,source,titleUrl))
    return Data
def insertSQL(sql,data):
    '''通用写入MySQL只一行'''
    conn, cursor = getconn()
    cursor.execute(sql, data)
    conn.commit()
    closeconn(cursor, conn)
def insertSQLexecutemany(sql,data):
    '''通用写入MySQL多行'''
    conn, cursor = getconn()
    cursor.executemany(sql,data)
    conn.commit()
    closeconn(cursor, conn)
def PyUpdateDetailsData():
    '''更新地区数据'''
    data = detailsData()
    sql = "UPDATE now_details SET nowConfirm=%s WHERE `name`=%s"
    insertSQLexecutemany(sql, [tuple(dataList) for dataList in data])
def PyTotalInsertData():
    """每日写入total_data表"""
    sql = 'insert into total_data(todayTime,localConfirm,confirm,heal,noInfect) values(%s,%s,%s,%s,%s);'
    insertSQL(sql,todayData())
def PyInsertChinaAddTrend():
    """每日写入chinaAddTrend表"""
    data = request_get_data()
    lastUpdateTime = data['lastUpdateTime']  # 上次更新时间
    localConfirm = data['chinaTotal']['localConfirm']
    localConfirmH5 = data['chinaAdd']['localConfirmH5']
    sql = 'insert into chinaAddTrend(todayTime,localConfirmH5,localConfirm) values(%s,%s,%s)'
    insertSQL(sql, (lastUpdateTime, localConfirmH5, localConfirm))
def pyWriteTotalContents():
    """写入contents表"""
    sql ='''
    insert into `contents` (id, publicTime, title,source,titleUrl)
    VALUES(%s, %s,%s,%s,%s)
    on duplicate key update
    publicTime=values(publicTime),
    title=values(title),
    source=values(source),
    titleUrl=values(titleUrl);
    '''
    insertSQLexecutemany(sql,requestGetContent())

if __name__ == '__main__':
    # 设置定时器
    PyUpdateDetailsData()
    PyTotalInsertData()
    PyInsertChinaAddTrend()
    pyWriteTotalContents()


