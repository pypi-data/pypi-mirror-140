import json
import csv

hotfinger = []

with open("../data/hotfinger_v1.json","r") as f:
    hotfinger = json.load(f)
with open("../data/hotfinger_v1.csv","w") as f:
    writer = csv.writer(f,delimiter=",")
    keys = ["id","name","tags"]
    writer.writerow(keys)
    for item in hotfinger:
        writer.writerow([item["_id"]["$oid"],item["name"],",".join(item["tags"])])
