from flask import Flask, render_template, request, redirect, url_for
import json
import pandas as pd
import numpy as np
import pickle

with open('df_month.pkl', mode='rb') as f:
    df_month = pickle.load(f)
with open('df_year.pkl', mode='rb') as f:
    df_year = pickle.load(f)
with open('df_future.pkl', mode='rb') as f:
    df_future = pickle.load(f)

colors = [
    ['rgb(  0,   0, 255)', 'rgba(  0,   0, 255, 0.5)'],
    ['rgb(  0, 203, 255)', 'rgba(  0, 203, 255, 0.5)'],
    ['rgb(255, 255,   0)', 'rgba(255, 255,   0, 0.5)'],
    ['rgb(216, 255, 204)', 'rgba(216, 255, 204, 0.5)'],
    ['rgb(  0, 255,   0)', 'rgba(  0, 255,   0, 0.5)'],
    ['rgb(  0, 101,   0)', 'rgba(  0, 101,   0, 0.5)'],
    ['rgb(255,  63,   0)', 'rgba(255,  63,   0, 0.5)'],
    ['rgb( 203,  0, 203)', 'rgba( 203,  0, 203, 0.5)'],
    ['rgb(  0,   0,  50)', 'rgba(  0,   0,  50, 0.5)']
]

app = Flask(__name__)

#########
# 共通用 #
#########
@app.route('/getOut2')
def getOut2():
    return json.dumps(df_month["out2"].columns.tolist(), ensure_ascii=False)
@app.route('/getMonth')
def getMonth():
    return json.dumps(df_month["basic"].index.tolist(), ensure_ascii=False)
@app.route('/getYear')
def getYear():
    return json.dumps(df_year["basic"].index.tolist(), ensure_ascii=False)

################
# index.html用 #
################
@app.route('/getTable_index/<item>')
def getTable_index(item):
    slct, out2Num = item.split(",")
    if slct == "asset":
        df = df_month["basic"].drop(columns=["収入", "支出", "収支"])
    elif slct == "inout":
        df = df_month["basic"].drop(columns="資産")
    elif slct == "out1":
        df = df_month["out1"]
    elif slct == "out2":
        df = df_month["out2"].loc[:, [df_month["out2"].columns[int(out2Num)]]]
    elif slct == "in":
        df = df_month["in"]
    out = []
    out.append([])
    out[-1].append("月")
    for column in df.columns:
        out[-1].append(column)
    for index in reversed(df.index.tolist()):
        out.append([])
        out[-1].append(index)
        for column in df.columns:
            out[-1].append("{:,}".format(df.loc[index, column]))
    return json.dumps(out, ensure_ascii=False)

@app.route('/getGraph_index/<item>')
def getGraph_index(item):
    slct, out2Num, dataLen = item.split(",")
    if slct == "inout":
        df = df_month["basic"].drop(columns="資産")
        if int(dataLen) == 0:
            df = df.loc[df.index[:24], :]
        chartData = {}
        chartData["labels"] = df.index.tolist()
        chartData["datasets"] = []
        for i, column in enumerate(df.columns):
            chartData["datasets"].append({})
            if i == 2:
                chartData["datasets"][-1]["type"] = "bar"
                chartData["datasets"][-1]["backgroundColor"] = colors[i % len(colors)][0]
            else:
                chartData["datasets"][-1]["type"] = "line"
                chartData["datasets"][-1]["fill"] = False
                chartData["datasets"][-1]["borderColor"] = colors[i % len(colors)][0]
            chartData["datasets"][-1]["label"] = column
            chartData["datasets"][-1]["data"] = df.loc[:, column].tolist()
        out = {}
        out["type"] = "bar"
        out["data"] = chartData
        out["options"] = {"responsive": True, "tooltips": {"mode": "index", "intersect": True},
                          "elements": {"line": {"tension": 0.1}},
                          "scales"  : {"yAxes": [{"ticks": {"beginAtZero": True}}]}
                         }
    else:
        if slct == "out1":
            df = df_month["out1"]
        elif slct == "out2":
            df = df_month["out2"].loc[:, [df_month["out2"].columns[int(out2Num)]]]
        elif slct == "in":
            df = df_month["in"]
        elif slct == "asset":
            df = df_month["basic"].drop(columns=["収入", "支出", "収支"])
        if int(dataLen) == 0:
            df = df.loc[df.index[:24], :]
        out = {}
        out["type"] = "line"
        out["options"] = {"elements": {"line": {"tension": 0.1}},
                          "scales"  : {"yAxes":[{"stacked": True, "ticks": {"beginAtZero": True}}]},
                          "legend": {"display": True}
                         }
        out["data"] = {}
        out["data"]["labels"] = df.index.tolist()
        out["data"]["datasets"] = []
        for i, column in enumerate(df.columns):
            out["data"]["datasets"].append({})
            if i == 0:
                out["data"]["datasets"][-1]["fill"] = True
            else:
                out["data"]["datasets"][-1]["fill"] = "-1"
            out["data"]["datasets"][-1]["backgroundColor"] = colors[i % len(colors)][1]
            out["data"]["datasets"][-1]["borderColor"] = colors[i % len(colors)][0]
            out["data"]["datasets"][-1]["label"] = column
            out["data"]["datasets"][-1]["data"] = df.loc[:, column].tolist()
    return json.dumps(out, ensure_ascii=False)

################
# month.html用 #
################
@app.route('/getGraph_snapMonth/<slct>/<my>')
def getGraph_snapMonth(slct, my):
    if len(my) == 6:
        df = df_month
    elif len(my) == 4:
        df = df_year
    if slct == "out":
        df = df["out1"]
    elif slct == "in":
        df = df["in"]
    con = {}
    con["type"] = "pie"
    con["options"] = {"responsive": True}
    con["data"] = {}
    con["data"]["datasets"] = [{}]
    con["data"]["datasets"][0]["data"] = df.loc[my, :].values.tolist()
    con["data"]["datasets"][0]["backgroundColor"] = [colors[i % len(colors)][0] for i in range(len(df.columns))]
    con["data"]["labels"] = df.columns.tolist()
    return json.dumps(con, ensure_ascii=False)

@app.route('/getTable_snapMonth/<slct>/<my>')
def getTable_snapMonth(slct, my):
    if len(my) == 6:
        df = df_month
    elif len(my) == 4:
        df = df_year
    if slct == "in":
        df = df["in"]
    elif slct == "out":
        df = df["out2"]
    elif slct == "inout":
        df = df["basic"].drop(columns="資産")
    out = []
    out.append([])
    out[-1].append("項目")
    out[-1].append("費用")
    for col in df.columns:
        out.append([])
        out[-1].append(col)
        out[-1].append("{:,}".format(int(df.loc[my, col])))
    return json.dumps(out, ensure_ascii=False)

#################
# future.html用 #
#################
@app.route('/getTable_future')
def getTable_future():
    out = []
    out.append([])
    out[-1].append("月")
    out[-1].append("実績")
    out[-1].append("予測")
    for month in reversed(df_future.index):
        out.append([])
        out[-1].append(month)
        out[-1].append("{:,}".format(int(df_future.loc[month, "実績"])))
        out[-1].append("{:,}".format(int(df_future.loc[month, "予測"])))
    return json.dumps(out, ensure_ascii=False)

@app.route('/getGraph_future')
def getGraph_future():
    out = {}
    out["type"] = "line"
    out["options"] = {"elements": {"line": {"tension": 0.1}},
                      "scales"  : {"yAxes":[{"stacked": True, "ticks": {"beginAtZero": True}}]},
                      "legend": {"display": True}
                      }
    out["data"] = {}
    out["data"]["labels"] = df_future.index.tolist()
    out["data"]["datasets"] = []
    for i, column in enumerate(df_future.columns):
        out["data"]["datasets"].append({})
        if i == 0:
            out["data"]["datasets"][-1]["fill"] = True
        else:
            out["data"]["datasets"][-1]["fill"] = "-1"
        out["data"]["datasets"][-1]["backgroundColor"] = colors[i % len(colors)][1]
        out["data"]["datasets"][-1]["borderColor"] = colors[i % len(colors)][0]
        out["data"]["datasets"][-1]["label"] = column
        out["data"]["datasets"][-1]["data"] = df_future.loc[:, column].tolist()
    return json.dumps(out, ensure_ascii=False)

#####################
# render_template用 #
#####################
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/future')
def future():
    return render_template('future.html')

@app.route('/month')
def month():
    return render_template('month.html')

if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)