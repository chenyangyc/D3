import random
from tqdm import tqdm
import numpy as np
from glob import glob
import csv
import copy
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import Config

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', type=str, default='gcc430')
parser.add_argument('--loop_time', type=int, default=100)
args = parser.parse_args()
print(args)

loop_time = args.loop_time
tested_compiler = args.dataset
dis_base_url = './distances/' + tested_compiler + '/'
res_csv = './results/' + tested_compiler + '.csv'

compiler = Config.datasets[tested_compiler]
topn = compiler.n
names = compiler.names
missing_tc = compiler.missing_tc
bug_num = compiler.bug_num
COUNT = compiler.COUNT - len(missing_tc)
rev_url = compiler.rev_url

name2id = {}
id2name = {}
with open(names, 'r') as f:
    for index, line in enumerate(f):
        name = line.strip().split('/')[-1].split('.')[0]
        name2id[name] = index
        id2name[index] = name


def FPF(distance_matrix):
    tag = np.zeros(COUNT + len(missing_tc))
    # missing tc start
    tc_ids = []
    start = random.randint(0, COUNT - 1)
    while True:
        if id2name[start] not in missing_tc:
            tc_ids = [start]
            break
        else:
            start = random.randint(0, COUNT - 1)
    # # origin start
    # start = random.randint(0, COUNT - 1)
    # tc_ids = [start]
    tag[start] = 1
    dis = copy.deepcopy(distance_matrix[start])
    while len(tc_ids) < COUNT:
        choice = np.argmax(dis)
        if tag[choice] == 1:
            remain_candidate = [i for i, x in enumerate(dis) if tag[i] == 0 and id2name[i] not in missing_tc]
            # random.shuffle(remain_candidate)
            tc_ids.extend(remain_candidate)
            break

        if id2name[int(choice)] in missing_tc:
            dis[choice] = 0
            tag[choice] = 1
            continue
        mask = distance_matrix[choice] < dis
        dis[mask] = copy.deepcopy(distance_matrix[choice][mask])
        tc_ids.append(choice)
        dis[choice] = 0
        tag[choice] = 1
    return tc_ids


def random_tc():
    tc_ids = list(range(0, COUNT + len(missing_tc)))
    for i in missing_tc:
        tc_ids.remove(name2id[i])
    random.shuffle(tc_ids)
    return tc_ids


def get_bug_map():
    file_list = glob(rev_url)
    bug_map = {}
    for file in file_list:
        with open(file, 'r') as f:
            contents = f.read()
            if '#' in contents:
                contents = contents.split('#')[2]
            name = file.split('/')[-1].split('.')[0]
            if name in name2id.keys():
                bug_map[name] = contents
            # bug_map[file.split('/')[-1].split('.')[0]] = f.read()
    return bug_map


def form_trigger(tc_ids, bug_map):
    bug_list = []
    nums_list = []
    flag = False
    for index, tc_id in enumerate(tc_ids):
        if flag:
            return nums_list
        tc_name = id2name[tc_id]
        bug_id = bug_map[tc_name]
        if bug_id not in bug_list:
            nums_list.append(index + 1)
            if len(set(bug_list)) == bug_num:
                # print("All bugs revealed    ====>   {}".format(index))
                flag = True
        bug_list.append(bug_id)
    return nums_list


def triggered_bugs(tc_ids, bug_map):
    bug_list = []
    num = 0
    bug_id = 0
    nums_list = []
    exist = []
    flag = False
    for index, tc_id in enumerate(tc_ids):
        if flag:
            bug_list.append((id2name[tc_id], bug_id))
            exist.append(bug_id)
            nums_list.append(num)
            continue
        # try:
        tc_name = id2name[tc_id]
        bug_id = bug_map[tc_name]
        if bug_id not in exist:
            bug_list.append((id2name[tc_id], bug_id))
            num = num + 1
            if num == bug_num:
                # print("All bugs revealed    ====>   {}".format(index))
                flag = True
        bug_list.append((id2name[tc_id], bug_id))
        exist.append(bug_id)
        nums_list.append(num)
        # except:
        #     print(tc_id)
    # print(bug_list)
    return np.array(nums_list)
    # return bug_list, np.array(nums_list)


def max_min_normalize(x):
    min_mask = x < 0.0001
    x[min_mask] = 0
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    return x


def plus(x, y):
    x = max_min_normalize(x)
    y = max_min_normalize(y)

    m1 = np.mean(x)
    m2 = np.mean(y)
    r = x + (y * (m1 / m2))
    return r


def write_result_table(reses, names):
    path = res_csv
    bugs = ['']
    for b in range(1, bug_num + 1):
        bugs.append(str(b))
    with open(path, 'w') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(['APP.', 'Bug number'])
        csv_write.writerow(bugs)
        for i, name in zip(reses, names):
            t = [name]
            for j in range(0, len(i)):
                t.append(i[j] / loop_time)
            csv_write.writerow(t)


if __name__ == '__main__':
    bug_map = get_bug_map()
    # print(bug_map)

    program_dis = np.load(dis_base_url + 'program.npy')
    opt_dis = np.load(dis_base_url + 'opt.npy')
    coverage_dis = np.load(dis_base_url + 'coverage.npy')

    tamer_dis = np.load(dis_base_url + 'tamer.npy')

    total_dis = plus(plus(program_dis, coverage_dis), opt_dis)

    ablation1_dis = plus(program_dis, coverage_dis)
    ablation2_dis = plus(coverage_dis, opt_dis)
    ablation3_dis = plus(program_dis, opt_dis)

    total_num = np.zeros(COUNT)
    total_tc_num = np.zeros(bug_num)

    ab_num1 = np.zeros(COUNT)
    ab_num2 = np.zeros(COUNT)
    ab_num3 = np.zeros(COUNT)

    tc_ab_num1 = np.zeros(bug_num)
    tc_ab_num2 = np.zeros(bug_num)
    tc_ab_num3 = np.zeros(bug_num)

    tamer_num = np.zeros(COUNT)
    tamer_tc = np.zeros(bug_num)

    transformer_num = np.zeros(COUNT)
    transformer_tc = np.zeros(bug_num)

    for i in tqdm(range(0, loop_time)):
        total_num = total_num + triggered_bugs(FPF(total_dis), bug_map)
        total_tc_num = total_tc_num + form_trigger(FPF(total_dis), bug_map)

        ab_num1 = ab_num1 + triggered_bugs(FPF(ablation1_dis), bug_map)
        tc_ab_num1 = tc_ab_num1 + form_trigger(FPF(ablation1_dis), bug_map)

        ab_num2 = ab_num2 + triggered_bugs(FPF(ablation2_dis), bug_map)
        tc_ab_num2 = tc_ab_num2 + form_trigger(FPF(ablation2_dis), bug_map)

        ab_num3 = ab_num3 + triggered_bugs(FPF(ablation3_dis), bug_map)
        tc_ab_num3 = tc_ab_num3 + form_trigger(FPF(ablation3_dis), bug_map)

        tamer_num = tamer_num + triggered_bugs(FPF(tamer_dis), bug_map)
        tamer_tc = tamer_tc + form_trigger(FPF(tamer_dis), bug_map)

        rad = random_tc()
        transformer_num = transformer_num + triggered_bugs(rad, bug_map)
        transformer_tc = transformer_tc + form_trigger(rad, bug_map)

    # write wasted effort result into csv file
    improve1 = ((tamer_tc - total_tc_num) / tamer_tc) * 100
    improve2 = ((transformer_tc - total_tc_num) / transformer_tc) * 100
    reses = [tc_ab_num1, tc_ab_num2, tc_ab_num3, tamer_tc, transformer_tc, total_tc_num, improve1, improve2]
    names = ['$D3_{noO}$', '$D3_{noP}$', '$D3_{noC}$', '$Tamer$', '$Transformer$',
             '$D3$', '\\Uparrow $Im_{Tamer}(\%)$', '\\Uparrow $Im_{Transformer}(\%)$']
    write_result_table(reses, names)

    # calculate theoretical best RAUC
    theoretical_best = np.zeros(COUNT)
    if topn < bug_num:
        theoretical_best = list(range(1, topn))
    else:
        theoretical_best = list(range(1, bug_num + 1))
        for i in range(bug_num + 1, topn + 1):
            theoretical_best.append(bug_num)
    best_auc = np.trapz(theoretical_best)
    theoretical_best = np.array(theoretical_best) * loop_time

    # discovery curve & R-AUC value
    label_font = {'family': 'Times New Roman',
                  'weight': 'normal',
                  'size': 18,
                  }
    legend_font = {'family': 'Times New Roman',
                   'weight': 'normal',
                   'size': 20,
                   }
    plt.figure(figsize=(14, 9))
    ax = plt.gca()
    y_major_locator = MultipleLocator(1)
    ax.yaxis.set_major_locator(y_major_locator)
    plt.yticks(fontproperties='Times New Roman', fontsize=20)  # 设置大小及加粗
    plt.xticks(fontproperties='Times New Roman', fontsize=20)
    plt.xlabel('Number of test failures', label_font)
    plt.ylabel('Number of unique bugs', label_font)
    plt.tick_params(labelsize=18)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    [label.set_fontname('Times New Roman') for label in labels]
    plt.grid(b=True, axis='y', linestyle='--', color='gray', alpha=0.6)  # 只显示x轴网格线

    lists = [total_num[:topn], tamer_num[:topn], transformer_num[:topn]]
    types = ['D3', 'Tamer', 'Transformer']
    line_style = ['-', '--', ':', '-.']
    markers = ['*', 's', '^', '*']
    colors = ['#FA7F6F', '#8ECFC9', '#82B0D2', '#82B0D2']

    for num, t, s, m, c in zip(lists, types, line_style, markers, colors):
        num = num / loop_time
        num = num[:topn]
        auc = np.trapz(num)
        rauc = auc / best_auc
        rauc = str(rauc * 100)[0:5] + '%'
        num = np.insert(num, 0, 0)
        plt.plot(num, label=t + ' ' + '(APFD: ' + rauc + ')', ls=s, color=c, lw=2.8)
        print(t + ': ' + '(APFD: ' + rauc + ')')
        plt.legend(prop=legend_font)
    plt.show()
