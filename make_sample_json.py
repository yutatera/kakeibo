from server import getOut2, getMonth, getYear, getTable_index, getGraph_index,\
   df_month, df_year, getGraph_snapMonth, getTable_snapMonth, getGraph_future, getTable_future
import json

# future
outFuture = {}
for x in ["getGraph_future", "getTable_future"]:
    exec('outFuture["/{}"] = json.loads({}())'.format(x, x))

# index
outIndex = {}
for x in ["getOut2"]:
    exec('outIndex["/{}"] = json.loads({}())'.format(x, x))
for slct in ["asset", "inout", "in", "out1"]:
    out2Num = "None"
    txt = slct + "," + out2Num
    exec('outIndex["/getTable_index/{}"] = json.loads(getTable_index("{}"))'.format(txt, txt))
    for dataLen in ["0", "1"]:
        txt = slct + "," + str(out2Num) + "," + dataLen
        exec('outIndex["/getGraph_index/{}"] = json.loads(getGraph_index("{}"))'.format(txt, txt))
slct = "out2"
for out2Num in range(len(df_month["out2"].columns.tolist())):
    txt = slct + "," + str(out2Num)
    exec('outIndex["/getTable_index/{}"] = json.loads(getTable_index("{}"))'.format(txt, txt))
    for dataLen in ["0", "1"]:
        txt = slct + "," + str(out2Num) + "," + dataLen
        exec('outIndex["/getGraph_index/{}"] = json.loads(getGraph_index("{}"))'.format(txt, txt))

# month
outMonth= {}
for month in df_month["basic"].index.tolist() + df_year["basic"].index.tolist() + ["undefined"]:
    for slct in ["in", "out"]:
        exec('outMonth["/getGraph_snapMonth/{}/{}"] = json.loads(getGraph_snapMonth("{}", "{}"))'.format(slct, month, slct, month))
    for slct in ["in", "out", "inout"]:
        exec('outMonth["/getTable_snapMonth/{}/{}"] = json.loads(getTable_snapMonth("{}", "{}"))'.format(slct, month, slct, month))
for x in ["getMonth", "getYear"]:
    exec('outMonth["/{}"] = json.loads({}())'.format(x, x))

with open('sampleDataIndex.json', 'w', encoding="utf-8") as f:
    json.dump(outIndex, f, ensure_ascii=False)
with open('sampleDataMonth.json', 'w', encoding="utf-8") as f:
    json.dump(outMonth, f, ensure_ascii=False)
with open('sampleDataFuture.json', 'w', encoding="utf-8") as f:
    json.dump(outFuture, f, ensure_ascii=False)