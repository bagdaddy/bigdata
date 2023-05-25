import pandas as pd
from pymongo import MongoClient
import numpy as np
import multiprocessing as mp
from time import perf_counter
import math

mongos1 = "mongodb://localhost:27019/"
mongos2 = "mongodb://localhost:27020/"
cpus = 10
chunksize = 100

def get_distinct_vessels():
    client = MongoClient(mongos1)
    db = client["ships"]
    collection = db["ship_positions"]
    query = {'mmsi': {'$ne': '0'}}
    vessels = collection.distinct('mmsi', query)
    client.close()

    return vessels

def remove_nas(vessels):
    columns = [
        'timestamp',
        'navigational_status',
        'latitude',
        'longitude',
        'sog',
        'cog'
    ]

    return [
        doc for doc in vessels if all(
            column in doc and doc[column] is not None and (
                isinstance(doc[column], (float, int)) and not math.isnan(doc[column])
                or isinstance(doc[column], str) and doc[column].lower() != 'nan'
            )
            for column in columns
        )
    ]


def filter(vessel_mmsi, chunkId):
    start_time = perf_counter()

    conn_string = mongos1 if chunkId % 2 == 0 else mongos2
    client = MongoClient(conn_string)
    db = client["ships"]
    query = [
        {
            '$match': {
                '$and': [
                    {'mmsi': {'$in': vessel_mmsi}},
                ]
            }
        },
        {
            '$group': {
                '_id': '$mmsi',
                'count': {'$sum': 1}
            }
        },
        {
            '$match': {
                'count': {'$gte': 100}
            }
        },
        {
            '$lookup': {
                'from': 'ship_positions',
                'localField': '_id',
                'foreignField': 'mmsi',
                'as': 'documents'
            }
        }
    ]

    vessels = list(db["ship_positions"].aggregate(query))
    vessels = sum([vessel['documents'] for vessel in vessels], [])
    before_filter = len(vessels)
    vessels = remove_nas(vessels)
    
    if len(vessels) > 0:
        db['filtered_positions'].insert_many(vessels)

    timing = perf_counter() - start_time

    print(f"chunk #{chunkId} - before: {before_filter}, after filter: {len(vessels)}. Elapsed: {round(timing, 2)}s")

    client.close()

def parallelize_filtering(vessels):
    pool = mp.Pool(cpus)
    vessels = [int(vessel) for vessel in vessels]
    n_chunks = math.ceil(len(vessels) / chunksize)
    chunks = np.array_split(vessels, n_chunks)
    temp = pool.starmap(filter, [(chunk.tolist(), i) for i, chunk in enumerate(chunks)])


if __name__ == '__main__':
    cpus_max = mp.cpu_count()
    distinct_values = get_distinct_vessels()

    start_time = perf_counter()
    parallelize_filtering(distinct_values)
    timing = perf_counter() - start_time

    print()
    print(f"all data filtered and migrated in {round(timing, 2)}s")