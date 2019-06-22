from server import getOut2, getMonth, getYear, getTable_index, getGraph_index,\
   df_month, df_year, getGraph_snapMonth, getTable_snapMonth, getGraph_future, getTable_future
import json
out = {}
for x in ["getOut2", "getMonth", "getYear", "getGraph_future", "getTable_future"]:
    exec('out["{}"] = json.loads({}())'.format(x, x))

# index
for slct in ["asset", "inout", "in", "out1"]:
    out2Num = "None"
    txt = slct + "," + out2Num
    exec('out["/getTable_index/{}"] = json.loads(getTable_index("{}"))'.format(txt, txt))
    for dataLen in ["0", "1"]:
        txt = slct + "," + str(out2Num) + "," + dataLen
        exec('out["/getGraph_index/{}"] = json.loads(getGraph_index("{}"))'.format(txt, txt))
slct = "out2"
for out2Num in range(len(df_month["out2"].columns.tolist())):
    txt = slct + "," + str(out2Num)
    exec('out["/getTable_index/{}"] = json.loads(getTable_index("{}"))'.format(txt, txt))
    for dataLen in ["0", "1"]:
        txt = slct + "," + str(out2Num) + "," + dataLen
        exec('out["/getGraph_index/{}"] = json.loads(getGraph_index("{}"))'.format(txt, txt))

# month
for month in df_month["basic"].index.tolist() + df_year["basic"].index.tolist():
    for slct in ["in", "out"]:
        exec('out["/getGraph_snapMonth/{}/{}"] = json.loads(getGraph_snapMonth("{}", "{}"))'.format(slct, month, slct, month))
        exec('out["/getTable_snapMonth/{}/{}"] = json.loads(getTable_snapMonth("{}", "{}"))'.format(slct, month, slct, month))

with open('sampleData.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False)