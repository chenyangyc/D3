from glob import glob
from scipy.stats import spearmanr
import numpy as np
from tqdm import tqdm

names = './data/llvm280/names'
diff_url = './mutation-data/llvm280-diff/*.diff'
dis_url = './diff_dis.npy'

diff = glob(diff_url)
specials = ['(', ')', '{', '}', ';', ',']

name2id = {}
id2name = {}
with open(names, 'r') as f:
    for index, line in enumerate(f):
        line = line.strip()
        name = line.split('/')[-1].split('.')[0]
        id = index
        name2id[name] = id
        id2name[id] = name

all_cases_set = {}
for single_case in tqdm(diff):
    diff_set = {}
    rank_set = {}
    name = single_case.strip().split('/')[-1].split('.')[0]

    if name in name2id.keys():
        id = name2id[name]
        with open(single_case, 'r') as f:
            for line in f:
                line = line.strip()
                if line != '':
                    modify = line.split('\t')[1] + line.split('\t')[-1]
                    if line.split('\t')[1] not in specials:
                        diff_set[modify] = diff_set[modify] + 1 if modify in diff_set.keys() else 1

        a = sorted(diff_set.items(), key=lambda x: x[1], reverse=True)
        tmp = {}
        rank = 0
        cur = 1000
        for key in a:
            rank += 1
            rank_set[str(key[0])] = rank
        all_cases_set[id] = rank_set


distance = np.full((len(id2name.keys()), len(id2name.keys())), 0.0)
for i1, v1 in tqdm(all_cases_set.items()):
    for i2, v2 in all_cases_set.items():
        if int(i1) == int(i2):
            distance[int(i1), int(i2)] = 0.0
            continue
        all_diff = set(v1.keys()).union(set(v2.keys()))
        l1 = []
        l2 = []
        for name in all_diff:
            l1.append(v1.setdefault(name, 0))
            l2.append(v2.setdefault(name, 0))
        distance[int(i1), int(i2)] = 1.0 - spearmanr(l1, l2)[0]
np.save(dis_url, distance)
print(distance)
