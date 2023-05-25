import pandas as pd
from pymongo import MongoClient
import numpy as np
import multiprocessing as mp
from time import perf_counter
from datetime import datetime
import math
import sys
import matplotlib.pyplot as plt
import seaborn as sns

mongos1 = "mongodb://localhost:27019/"
mongos2 = "mongodb://localhost:27020/"
cpus = 10
chunksize = 40

def get_distinct_vessels():
    client = MongoClient(mongos1)
    db = client["ships"]
    collection = db["filtered_positions"]
    query = {'mmsi': {'$ne': '0'}}
    vessels = collection.distinct('mmsi', query)
    client.close()

    return vessels

def update_vessel_data_points(data_points, collection):
    delta_t = []
    print('updating', len(data_points), 'for vessel:', data_points[0]['mmsi'])
    data_points.sort(key=lambda x: x['timestamp'])

    for i in range(len(data_points)):
        if i == 0:
            delta_t.append((data_points[i]['_id'], 0))
            continue
        curr_time = datetime.strptime(data_points[i - 1]['timestamp'], '%d/%m/%Y %H:%M:%S')
        next_time = datetime.strptime(data_points[i]['timestamp'], '%d/%m/%Y %H:%M:%S')
        delta_t.append((data_points[i]['_id'], (next_time - curr_time).total_seconds() * 1000))

    for update in delta_t:
        collection.update_one({'_id': update[0]}, {'$set': {'delta_t': int(update[1])}})
    
    print('updated', len(data_points), 'for vessel:', data_points[0]['mmsi'])

def update_data(vessel_mmsi, chunkId):
    start_time = perf_counter()

    print('processing chunk', chunkId)
    conn_string = mongos1 if chunkId % 2 == 0 else mongos2
    client = MongoClient(conn_string)
    db = client["ships"]
    collection = db["filtered_positions"]

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
            '$lookup': {
                'from': 'ship_positions',
                'localField': '_id',
                'foreignField': 'mmsi',
                'as': 'documents'
            }
        }
    ]

    vessels = list(collection.aggregate(query))

    [update_vessel_data_points(vessel['documents'], collection) for vessel in vessels]

    timing = perf_counter() - start_time
    print('done processing chunk', chunkId, 'in', round(timing, 2))
    client.close()


def parallelize_updates(vessels):
    pool = mp.Pool(cpus)
    vessels = [int(vessel) for vessel in vessels]
    n_chunks = math.ceil(len(vessels) / chunksize)
    chunks = np.array_split(vessels, n_chunks)
    pool.starmap(update_data, [(chunk.tolist(), i) for i, chunk in enumerate(chunks)])

def create_histogram(vessels):
    client = MongoClient(mongos1)
    db = client["ships"]
    collection = db["filtered_positions"]

    query = [
        {
            '$match': {
                'delta_t': {'$ne': 0}
            }
        },
        {
            '$group': {
                '_id': '$delta_t',
                'frequency': {'$sum': 1}
            }
        },
    ]
    delta_ts = list(collection.aggregate(query))
    delta_ts.sort(key=lambda x: x['_id'])

    # print(list(delta_ts))

    # delta_ts = collection.find({'delta_t': {'$ne': 0}}, {'_id': 0, 'delta_t': 1})
    deltas = [str(obj['_id']) for obj in delta_ts]
    frequencies = [obj['frequency'] for obj in delta_ts]
    client.close()

    plt.figure(figsize=(10,5))
    plt.bar(range(len(deltas)), frequencies)
    plt.yscale('log')

    # Set plot labels and title
    plt.xlabel('Delta_t')
    plt.ylabel('Frequency')
    plt.title('Delta_t Histogram')

    # Display the histogram
    plt.show()

    # sns.kdeplot(delta_ts,shade=True)
    # sns.histplot(delta_ts, bins=50)
    # plt.show()


if __name__ == '__main__':
    vessels = get_distinct_vessels()
    if len(sys.argv) > 1 and sys.argv[1] == 'update':
        start_time = perf_counter()
        parallelize_updates(vessels)
        timing = perf_counter() - start_time
        print('finished updating in', round(timing, 2))

    create_histogram(vessels)
