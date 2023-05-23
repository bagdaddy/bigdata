import pandas as pd
from pymongo import MongoClient
import numpy as np
import multiprocessing as mp
from time import perf_counter
import math

mongos1 = "mongodb://localhost:27019/"
mongos2 = "mongodb://localhost:27020/"
cpus = 10
chunksize = 5000
df = pd.read_csv('data.csv', nrows=3000000)
df = df.rename(columns=lambda x: x.lower().replace(' ', '_'))

def insert_data(indices, chunkId):
    print("chunk", chunkId, "processing")

    start_time = perf_counter()

    conn_string = mongos1 if chunkId % 2 == 0 else mongos2
    client = MongoClient(conn_string)

    db = client["ships"]
    collection = db["ship_positions"]

    _from = (chunksize * chunkId)
    _to = _from + chunksize
    data = df.iloc[range(_from, _to)]
    insert = data.to_dict(orient='records')

    for _id, row in enumerate(insert):
        row['id'] = chunkId * chunksize + _id
        row['timestamp'] = row['#_timestamp']
        del row['#_timestamp']

    result = collection.insert_many(insert)
    
    timing = perf_counter() - start_time
    print(f"chunk {chunkId}: inserted {len(result.inserted_ids)} rows of data in {timing}")

    client.close()
    
def parallelize_inserts(indices, n_chunks, n_cpus):
    pool = mp.Pool(n_cpus)
    chunks = np.array_split(indices, n_chunks)
    temp = pool.starmap(insert_data, [(chunk, i) for i, chunk in enumerate(chunks)])

if __name__ == '__main__':
    cpus_max = mp.cpu_count()
    indices = range(len(df)) #11438537

    n_chunks = math.ceil(len(indices) / chunksize)

    print("trying to insert", len(df), "rows")
    start_time = perf_counter()
    parallelize_inserts(indices, n_chunks, cpus)
    timing = perf_counter() - start_time

    print()
    print("all data inserted in", timing)