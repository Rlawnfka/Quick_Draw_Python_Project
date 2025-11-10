import ndjson

with open("dataset.ndjson") as f : 
    data = ndjson.load(f)