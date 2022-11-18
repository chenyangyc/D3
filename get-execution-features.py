from glob import glob
from scipy.stats import spearmanr
import numpy as np
from tqdm import tqdm
import pandas as pd

names = './data/llvm280/names'
wrongat = './data/llvm280/names/wrongat-new'
cov_prefix = './data/llvm280/'
ep_file = './passing-testsuite-coverage/testsuite_280_ep.txt'
np_file = './passing-testsuite-coverage/testsuite_280_np.txt'
dis_url = './coverage.npy'

id2level = {}
with open(wrongat, 'r') as f:
    for index, line in enumerate(f):
        line = line.strip()
        levels = line.split(' ')
        res = levels.index('n')
        level = str(res + 1)
        id2level[index] = level

all_covs = []
name2id = {}
id2name = {}
with open(names, 'r') as f:
    for index, line in enumerate(f):
        line = line.strip()
        name = line.split('/')[-1].split('.')[0]
        id = index
        name2id[name] = id
        id2name[id] = name
        if index <= 84:
            cov = cov_prefix + name + '.' + id2level[id] + 'fcov'
            all_covs.append(cov)
        else:
            cov = cov_prefix + name + '.ofcov'
            all_covs.append(cov)

all_func_list = []
for i in all_covs:
    if i.strip().split('/')[-1].split('.')[0] in id2name.values():
        with open(i, 'r') as f:
            for line in f:
                n = line.split(' ')
                all_func_list.append(n[0] + n[1])
    all_func_list = list(set(all_func_list))
all_func_list.sort()

ep_dict = {}
with open(ep_file, 'r') as f:
    for line in f:
        name = line.strip().split(',')[0]
        count = int(line.strip().split(',')[1])
        ep_dict[name] = count

np_dict = {}
with open(np_file, 'r') as f:
    for line in f:
        name = line.strip().split(',')[0]
        count = int(line.strip().split(',')[1])
        np_dict[name] = count

all_cases_set = {}
for single_case in tqdm(cov):
    rank_set = {}
    tc_name = single_case.strip().split('/')[-1].split('.')[0]
    if tc_name in id2name.values():
        failures = set()
        ef_dict = {}
        with open(single_case, 'r') as f:
            for line in f:
                n = line.split(' ')
                name = n[0] + ' ' + n[1] + ' ' + n[2]
                ef_dict[name] = ef_dict.setdefault(name, 0) + int(n[-1])
                failures.add(name)

        func_score = dict.fromkeys(all_func_list)  # default value is None
        for statement in failures:
            ef = 1
            ep = ep_dict.get(statement, 0)
            mnp = np_dict.get(statement, 0.0000001)

            # ochiai
            score = ef / (ep + ef) ** .5

            # # kulczynski2
            # score = 0.5 * (1 + (ef / (ef + ep)))

            # # ochiai2
            # score = np / ((ef + ep) * np * (ep + np)) ** .5

            function_name = statement.split(' ')[0] + statement.split(' ')[1]

            if func_score[function_name] is None:
                func_score[function_name] = [score]
            else:
                func_score[function_name].append(score)

        for key, value in func_score.items():
            func_score[key] = max(value) if value is not None and value else 0

        vec = np.array(list(func_score.values()))
        all_cases_set[name2id[tc_name]] = vec


distance = np.full((len(all_cases_set.values()), len(all_cases_set.values())), -1000.0)
for i1, v1 in tqdm(all_cases_set.items()):
    for i2, v2 in all_cases_set.items():
        try:
            if distance[int(i2), int(i1)] != -1000.0:
                distance[int(i1), int(i2)] = distance[int(i2), int(i1)]
                continue
            if int(i1) == int(i2):
                distance[int(i1), int(i2)] = 0.0
                distance[int(i2), int(i1)] = 0.0
                continue
            distance[int(i1), int(i2)] = np.linalg.norm(v1 - v2)
        except Exception as e:
            print('')
            continue
np.save(dis_url, distance)
print(distance)
print(distance.shape)
