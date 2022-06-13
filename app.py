#!/usr/bin/python
# coding:utf-8
from flask import Flask
from flask import render_template
from flask import jsonify
from utils import getTime,getTotalData,getDetailsData,getChinaTrendOption,getChinaAddTrendOption,getContents
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route("/time")
def get_time():
    return getTime()

@app.route('/totaldata')
def get_TotalData():
    data = getTotalData()
    return jsonify({"localConfirm":data[1],"confirm":data[2],"heal":data[3],"noInfect":data[4]})

@app.route("/citys")
def get_details():
    data = []
    for i in getDetailsData():
        item = {}
        item['name'] = i[0]
        item['value'] = i[1]
        data.append(item)
    return jsonify({'cityData':data})

@app.route("/getchinatrend")
def get_ChinaTrend():
    getData = getChinaTrendOption()
    todayTime = [i[0].strftime("%m-%d") for i in getData]
    localConfirm = [i[1] for i in getData]
    confirm = [i[2] for i in getData]
    heal = [i[3] for i in getData]
    noInfect = [i[4] for i in getData]
    data = [todayTime, localConfirm, confirm, heal, noInfect]
    return jsonify({"todayTime":data[0],"localConfirm": data[1], "confirm": data[2], "heal": data[3],"noInfect": data[4]})

@app.route("/getTrend")
def get_trends():
    getData = getChinaAddTrendOption()
    todayTime = [i[0].strftime("%m-%d") for i in getData]
    localConfirmH5 = [i[1] for i in getData]
    localConfirm = [i[2] for i in getData]
    data = [todayTime, localConfirmH5,localConfirm]
    return jsonify({"todayTime": data[0], "localConfirmH5": data[1], "localConfirm": data[2]})

@app.route("/content")
def get_Content():
    data = []
    getData = getContents()
    list_data = [list(i) for i in getData]
    for i in list_data:
        i[0] = i[0].strftime("%m-%d %H:%M")
        data.append(i)
    return jsonify(data)

if __name__ == '__main__':
    app.run( )
