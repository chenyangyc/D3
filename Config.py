import numpy as np

# GCC-4.3.0
LoopTime = 100

class gcc430:
    bug_num = 29
    COUNT = 1235
    n = 250
    rev_url = './data/gcc430/*.rev'
    names = './data/gcc430/names'
    missing_tc = []


# GCC-4.4.0
class gcc440:
    bug_num = 20
    COUNT = 647
    n = 120
    rev_url = './data/gcc440/*.rev'
    names = './data/gcc440/names'
    missing_tc = ['417', '31', '65']


# GCC-4.5.0
class gcc450:
    COUNT = 26
    bug_num = 7
    n = 20
    rev_url = './data/gcc450/*.rev'
    names = './data/gcc450/names'
    missing_tc = ['6', '11', '14', '17', '18', '24']


# LLVM-2.8.0
class llvm280:
    bug_num = 6
    COUNT = 101
    n = 20
    rev_url = './data/llvm280/*.rev'
    names = './data/llvm280/names'
    missing_tc = ['86', '100', '90', '87']
    # missing_tc = ['86', '100', '90', '93']


datasets = {
    'gcc430': gcc430,
    'gcc440': gcc440,
    'gcc450': gcc450,
    'llvm280': llvm280
}
