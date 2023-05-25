import pandas as pd
from pymongo import MongoClient
import numpy as np
import multiprocessing as mp
from time import perf_counter
import math

mongos1 = "mongodb://localhost:27019/"
mongos2 = "mongodb://localhost:27020/"
cpus = 10
chunksize = 10000
nrows = 1500000
colnames = pd.read_csv('data.csv', nrows=0).columns
mongo_clients = [
    MongoClient(mongos1),
    MongoClient(mongos1),
    MongoClient(mongos1),
    MongoClient(mongos1),
    MongoClient(mongos1),
    MongoClient(mongos2),
    MongoClient(mongos2),
    MongoClient(mongos2),
    MongoClient(mongos2),
    MongoClient(mongos2)
]

def insert_data(indices, chunkId):
    print("chunk", chunkId, "processing")
    start_time = perf_counter()

    client = mongo_clients[chunkId % len(mongo_clients)]

    db = client["ships"]
    collection = db["ship_positions_3"]

    # _from = (chunksize * chunkId)
    # _to = _from + chunksize
    
    data = pd.read_csv('data.csv', skiprows=(chunkId * chunksize), nrows=chunksize, names=colnames)
    data = data.rename(columns=lambda x: x.lower().replace(' ', '_'))

    # data = df.iloc[range(_from, _to)]
    insert = data.to_dict(orient='records')

    for _id, row in enumerate(insert):
        row['id'] = chunkId * chunksize + _id
        row['timestamp'] = row['#_timestamp']
        del row['#_timestamp']

    result = collection.insert_many(insert)
    
    timing = perf_counter() - start_time
    print(f"chunk {chunkId}: inserted {len(result.inserted_ids)} rows of data in {timing}")
    
def parallelize_inserts(indices, n_chunks, n_cpus):
    pool = mp.Pool(n_cpus)
    chunks = np.array_split(indices, n_chunks)
    pool.starmap(insert_data, [(chunk, i) for i, chunk in enumerate(chunks)])

if __name__ == '__main__':
    cpus_max = mp.cpu_count()
    indices = range(nrows)

    n_chunks = math.ceil(len(indices) / chunksize)

    start_time = perf_counter()
    parallelize_inserts(indices, n_chunks, cpus)
    timing = perf_counter() - start_time

    [client.close() for client in mongo_clients]

    print()
    print(f"all data inserted in {round(timing, 2)}s")