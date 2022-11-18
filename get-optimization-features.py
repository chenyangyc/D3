from glob import glob
from scipy.stats import spearmanr
import numpy as np
from tqdm import tqdm
import time

names = './data/llvm280/names'
optimizations = './data/llvm280/optimizations.txt'
dis_url = './opt_dis.npy'

name2id = {}
id2name = {}
with open(names, 'r') as f:
    for index, line in enumerate(f):
        line = line.strip()
        name = line.split('/')[-1].split('.')[0]
        id = index
        name2id[name] = id
        id2name[id] = name

all_opts = []
with open(optimizations, 'r') as f:
    for index, line in enumerate(f):
        line = line.strip()
        opts = line.split(' ')
        all_opts += opts

all_opts = list(set(all_opts))

all_cases_set = {}
with open(optimizations, 'r') as f:
    for index, line in enumerate(f):
        id = index
        vec = dict.fromkeys(all_opts, 0)
        line = line.strip()
        single_opts = line.split(' ')
        for i in single_opts:
            vec[i] = 1
        funcs = np.array(list(vec.values()))
        # funcs = funcs / np.linalg.norm(funcs, ord=1)
        all_cases_set[id] = funcs

distance = np.full((len(id2name.keys()), len(id2name.keys())), -100.0)
for i1, v1 in tqdm(all_cases_set.items()):
    for i2, v2 in all_cases_set.items():
        distance[int(i1), int(i2)] = np.linalg.norm(v1 - v2)
np.save(dis_url, distance)
print(distance)
