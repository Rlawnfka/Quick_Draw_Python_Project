import ndjson

with open("cat.ndjson") as f : 
    data = ndjson.load(f)

print(data[0].keys())