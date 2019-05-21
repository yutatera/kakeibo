from flask import Flask, render_template, request, redirect, url_for
import json
import yaml
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from pprint import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-config', default="sample/config.yaml")
parser.add_argument('-data', default="sample/kakeibo.xlsx")
args = parser.parse_args()

def none2int(val):
    if val is None:
        output = 0
    else:
        output = int(val)
    return output


def calcMonthList(startMonth, finishMonth):
    y = startMonth[0]
    m = startMonth[1]
    yearList = []
    monthList = []
    while True:
        if len(yearList) == 0 or yearList[-1][0] != str(np.int(np.floor((100 * y + m - 4) / 100))):
            yearList.append([str(np.int(np.floor((100 * y + m - 4) / 100))), [str(100 * y + m)]])
        else:
            yearList[-1][1].append(str(100 * y + m))
        monthList.append(str(100 * y + m))
        if [y, m] == [finishMonth[0], finishMonth[1]]:
            break
        y, m = nextMonth(y, m)
    return {"月": monthList, "年度+月": yearList}

def nextMonth(y, m):
    m = m + 1
    if m == 13:
        m = 1
        y = y + 1
    return (y, m)


with open(args.config, "r", encoding="utf-8") as f:
    config = yaml.load(f)
print("--reading config--")
pprint(config)

sishutuItemList = [item for _, items in config["支出項目"] for item in items]
sishutuCategoryList = [category for category, _ in config["支出項目"] if category != "NA"]

print('--reading xlsx data--')
df_origin = pd.read_excel(args.data, sheet_name=None)
sheetNameList = list(df_origin.keys())
for i, sheetName in enumerate(sheetNameList):
    df_tmp = df_origin[sheetName]
    # "項目チェック"
    assert  "yyyymm" in df_tmp.columns and\
            "分類" in df_tmp.columns and\
            "入金" in df_tmp.columns and\
            "出金" in df_tmp.columns and\
            "残高" in df_tmp.columns, "error"
    for j, x in enumerate(df_tmp["分類"].values):
        if j == 0:
            assert np.isnan(x), "error"
        else:
            assert x == "移動" or x in config["収入項目"] + sishutuItemList, "error"
    # ---
    df_tmp["sheet"] = sheetNameList[i]
    if i == 0:
        df_data = df_tmp
    else:
        df_data = pd.concat([df_data, df_tmp])


df_item = pd.DataFrame([(y, x[0]) for x in config["支出項目"] for y in x[1]], columns=["分類", "大分類"])
df_data = pd.merge(df_data, df_item, on="分類", how="left")   # 元のエクセルデータ
# 移動のチェック
for month in calcMonthList(config["開始月"], config["現在月"])["月"]:
    nyukin = int(df_data.query('yyyymm==@month & 分類=="移動"')["入金"].sum())
    shukkin = int(df_data.query('yyyymm==@month & 分類=="移動"')["出金"].sum())
    assert nyukin == shukkin, "移動エラー"

print( "--calculating--")
columns = [("収入", "収入"), ("支出", "支出"), ("収支", "収支")]
columns.extend([("収入項目", x) for x in config["収入項目"]])
columns.extend([("支出小項目", x) for x in sishutuItemList])
columns.extend([("支出大項目", x) for x in sishutuCategoryList if x != "NA"])
columns.extend([('資産', '資産')])
df_month = pd.DataFrame(0, index=calcMonthList(config["開始月"], config["現在月"])["月"], columns=columns)
for sheetName in sheetNameList:
    zandakaOld = 0
    for month in df_month.index:
        zan = df_data.query('yyyymm==@month and sheet==@sheetName')["残高"].values
        if len(zan) == 0:
            df_month.loc[month, [("資産", "資産")]] += zandakaOld
        else:
            df_month.loc[month, [("資産", "資産")]] += int(zan[-1])
            zandakaOld = int(zan[-1])
for month in tqdm(df_month.index):
    nyukin = (df_data.query('yyyymm==@month & 分類!="移動"')["入金"].sum())
    shukkin = (df_data.query('yyyymm==@month & 分類!="移動"')["出金"].sum())
    df_month.loc[month, ("収入", "収入")] = none2int(nyukin)
    df_month.loc[month, ("支出", "支出")] = none2int(shukkin)
    df_month.loc[month, ("収支", "収支")] = none2int(nyukin) - none2int(shukkin)
    for item in config["収入項目"]:
        nyukin = df_data.query('分類==@item and yyyymm==@month')['入金'].sum()
        df_month.loc[month, ("収入項目", item)] = none2int(nyukin)
    for item in sishutuItemList:
        shukkin = df_data.query('分類==@item and yyyymm==@month')['出金'].sum()
        df_month.loc[month, ("支出小項目", item)] = none2int(shukkin)
    for item in [x for x in sishutuCategoryList if x != "NA"]:
        if item != "NA":
            shukkin = df_data.query('大分類==@item and yyyymm==@month')["出金"].sum()
            df_month.loc[month, ("支出大項目", item)] = none2int(shukkin)

# 収支のチェック
monthOld = None
for month in calcMonthList(config["開始月"], config["現在月"])["月"]:
    if monthOld != None:
        print(month)
        print(df_month[("資産", "資産")][month])
        print(df_month[("資産", "資産")][monthOld])
        print(df_month[("収支", "収支")][month])
        assert df_month[("資産", "資産")][month] - df_month[("資産", "資産")][monthOld] == df_month[("収支", "収支")][month], "error"
    monthOld = month
print(df_month.head())

# 年毎用
yearList = calcMonthList(config["開始月"], config["現在月"])["年度+月"]
df_year = pd.DataFrame(0, index=[year[0] for year in yearList], columns=df_month.columns)
for col in df_year.columns:
    for year in yearList:
        x = 0
        for month in year[1]:
            x += int(df_month[col][month])
        df_year.loc[str(year[0]), (col[0], col[1])] = x
print(df_year.tail())

# 予測
futureMonth = config["現在月"]
for _ in range(60):
    futureMonth = nextMonth(futureMonth[0], futureMonth[1])
print(futureMonth)
index = calcMonthList(config["開始月"], [futureMonth[0], futureMonth[1]])["月"]
df_future = pd.DataFrame(0, index=index, columns=[("予測", "実績"), ("予測", "予測")])
shusiPredict = {}
for month in calcMonthList(config["開始月"], config["締め月"])["月"]:
    shusiPredict[month[4:7]] = df_month[('収支', '収支')][month]
zandaka = df_month[('資産', '資産')]
money_old = 0
for month in df_future.index:
    money = zandaka.get(month)
    if month in calcMonthList(config["開始月"], config["締め月"])["月"]:
        df_future.loc[month, ("予測", "実績")] = money
        df_future.loc[month, ("予測", "予測")] = 0
    else:
        money = money_old + shusiPredict[month[4:7]]
        df_future.loc[month, ("予測", "実績")] = 0
        df_future.loc[month, ("予測", "予測")] = money
    money_old = money
df_future.astype(int)
print(df_future.tail())

# 推移グラフ用
dataGraph = {}
dataGraph["x"] = df_month.index.tolist()
dataGraph["y"] = {}
for column in df_month.columns:
    if not column[0] in dataGraph["y"].keys():
        dataGraph["y"][column[0]] = []
    dataGraph["y"][column[0]].append({column[1]: df_month[column].tolist()})

# 月毎用
dataMonth = {}
for month in df_month.index:
    if not month in dataMonth.keys():
        dataMonth[month] = {}
    for column in df_month.columns:
        if not column[0] in dataMonth[month].keys():
            dataMonth[month][column[0]] = {}
        dataMonth[month][column[0]][column[1]] = int(df_month[column][month])
dataMonthAverage = []
for column in df_month.columns:
    if column[0] == "支出小項目":
        dataMonthAverage.append([column[1], int(df_month[column][calcMonthList(config["開始月"], config["締め月"])["月"]].mean())])

dataYear = {}
for year in df_year.index:
    if not year in dataYear.keys():
        dataYear[year] = {}
    for column in df_year.columns:
        if not column[0] in dataYear[year].keys():
            dataYear[year][column[0]] = {}
        dataYear[year][column[0]][column[1]] = int(df_year[column][year])


dataFuture = {}
dataFuture["x"] = df_future.index.tolist()
dataFuture["y"] = {}  #"収入":{}, "収入項目":{}, "支出小項目":{}, "支出大項目":{}}
for column in df_future.columns:
    if not column[0] in dataFuture["y"].keys():
        dataFuture["y"][column[0]] = []
    dataFuture["y"][column[0]].append({column[1]: df_future[column].tolist()})



app = Flask(__name__)

@app.route('/get_month')
def get_month():
    return json.dumps(df_month.index.tolist())

@app.route('/get_year')
def get_year():
    return json.dumps(df_year.index.tolist())

#with open('get_year.json', 'w', encoding="utf-8") as f:
#    json.dump(df_year.index.tolist(), f, ensure_ascii=False)
#with open('get_month.json', 'w', encoding="utf-8") as f:
#    json.dump(df_month.index.tolist(), f, ensure_ascii=False)


@app.route('/get_dataGraph')
def get_dataGraph():
    return json.dumps(dataGraph)

@app.route('/get_dataMonth')
def get_dataMonth():
    return json.dumps(dataMonth)

@app.route('/get_dataMonth_ave')
def get_dataMonth_ave():
    return json.dumps([dataMonth, dataMonthAverage])

@app.route('/get_dataYear')
def get_dataYear():
    return json.dumps(dataYear)

@app.route('/get_dataFuture')
def get_dataFuture():
    return json.dumps(dataFuture)

@app.route('/get_monthList')
def get_monthList():
    return json.dumps(calcMonthList(config["開始月"], config["現在月"])["月"])

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