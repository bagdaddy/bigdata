from PIL import Image, ImageOps
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import multiprocessing as mp
from time import perf_counter

image_path = "./data/images"
column_names = ['image', 'black_count', 'white_count', 'black_ratio', 'white_ratio']

def convertImages(chunk, n):
    black_pixels_arr = np.array([])
    white_pixels_arr = np.array([])
    black_ratio_arr = np.array([])
    white_ratio_arr = np.array([])
    for image in chunk:
        img = Image.open(image_path + "/" + image)
        grayscale = img.convert("L")
        bw_img = Image.new("1", img.size)
        threshold = np.median(grayscale)
        bw_img = grayscale.point(arr, '1')
        bw_img.save('./gray/' + image)
        total_pixels = bw_img.size[0] * bw_img.size[1]
        black_pixels = sum(1 for pixel in bw_img.getdata() if pixel == 0)
        white_pixels = sum(1 for pixel in bw_img.getdata() if pixel == 1)
        black_ratio = black_pixels / total_pixels
        white_ratio = white_pixels / total_pixels
        black_pixels_arr = np.append(black_pixels_arr, black_pixels)
        white_pixels_arr = np.append(white_pixels_arr, white_pixels)
        black_ratio_arr = np.append(black_ratio_arr, black_ratio)
        white_ratio_arr = np.append(white_ratio_arr, white_ratio)

    return pd.DataFrame({'image': chunk, 
        'black_count': black_pixels_arr,
        'white_count': white_pixels_arr,
        'black_ratio': black_ratio_arr,
        'white_ratio': white_ratio_arr
    })
    

def parallelized_conversion(data, n_splits, n_cpus):
    result = pd.DataFrame({'image': [], 
        'black_count': [],
        'white_count': [],
        'black_ratio': [],
        'white_ratio': []
    })
    pool = mp.Pool(n_cpus)
    chunks = np.array_split(data, n_splits)
    temp = pool.starmap(convertImages, [(chunk,n_cpus) for chunk in chunks])
    result = pd.concat(temp)
    result.to_csv('result.csv')
    pool.close()

if __name__ == '__main__':
    image_arr = os.listdir(image_path)
    cpus_max = mp.cpu_count()
    timings = {}
    for c in range(1, cpus_max + 1):
        start_time = perf_counter()
        parallelized_conversion(image_arr, c, c)
        timings[c] = perf_counter() - start_time
        print(c, timings[c])
    result = pd.read_csv('result.csv')
    print()
    print()
    sorted_timings = sorted(timings.items(), key=lambda x:x[1])
    for timing in sorted_timings:
        print('num of cpus: ' + str(timing[0]) + ', time: ' + str(timing[1]))

    cnt = 0
    for index, row in result.iterrows():
        if (row['black_ratio'] < 0.6 and row['black_ratio'] > 0.4) or (row['white_ratio'] < 0.6 and row['black_ratio'] > 0.4):
            cnt += 1

    print(cnt / result[result.columns[0]].count())

    plt.plot(timings.keys(), timings.values())
    plt.title('Processing time vs number of CPUs')
    plt.ylabel('Processing time (seconds)')
    plt.xlabel('Number of CPUs')
    plt.show()