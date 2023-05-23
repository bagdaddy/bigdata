import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
from time import perf_counter

def test():
    print('Please, enter several strings. Enter 0 to finish the input stage.')
    arr = []
    stop = False
    while not stop:
        inp = input('Please, enter a string or 0 to proceed: ')
        if inp != '0':
            arr.append(inp)
        elif inp == '0':
            if len(arr) > 1:
                stop = True
                print(arr)
                parallelized_count(np.array(arr), 1, 1)
            else:
                print('Please, enter at least 2 strings.')

def parallelized_count(data, n_splits, n_cpus):
    print(1)
    pool = mp.Pool(n_cpus)
    print(2)
    chunks = np.array_split(data, n_splits)
    print(3)
    final_dict = dict()
    temp = pool.starmap(character_count, [(chunk,n_cpus) for chunk in chunks])
    print(4)
    emt = {final_dict.update({k: v + final_dict.get(k, 0)}) for d in temp for k, v in d.items()}
    print(5)
    pool.close()
    # Compute final results:
    # count unique characters
    n_chars = len(list(final_dict.keys()))
    # get the top 10
    ser = pd.DataFrame({'count': final_dict.values()}, index=final_dict.keys())
    ser.sort_values('count', ascending=False,inplace=True)
    # Printing the results
    print(f'RESULTS:\nUnique characters - {n_chars} \nTop 10:')
    print(ser.head(10))

def character_count(chunk, n):
    temp_dict = {}
    for line in chunk:
        characters, counts = np.unique(np.array(list(line)), return_counts = True)
        print(counts)
        dic = dict(zip(characters, counts))
        emt = {temp_dict.update({k: v + temp_dict.get(k, 0)}) for k, v in dic.items()}

    return temp_dict

if __name__ == '__main__':
    testing = input('Enter 0 for testing or press Enter to proceed: ')
    if testing == '0':
        test()
    else:
        df = pd.read_csv('./covid_abstracts.csv')
        df = np.array(df["abstract"][0:100])
        cpus_max = mp.cpu_count()
        timings = {}
        for c in range(1, 2 + 1):
            start_time = perf_counter()
            parallelized_count(df, c, c)
            timings[c] = perf_counter() - start_time
        plt.plot(timings.keys(), timings.values())
        plt.title('Processing time vs number of CPUs')
        plt.ylabel('Processing time (seconds)')
        plt.xlabel('Number of CPUs')
        plt.show()