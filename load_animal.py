import json
import numpy as np


DIM = 2
DIM_DELIM = {0:'', 1:'$', 2:'%', 3:'#', 4:'@A', 5:'@B', 6:'@C', 7:'@D', 8:'@E', 9:'@F'}


def _recur_cubify(dim, list1, max_lens):
    more = max_lens[dim] - len(list1)
    if dim < DIM - 1:
        list1.extend([[]] * more)
        for list2 in list1:
            _recur_cubify(dim + 1, list2, max_lens)
    else:
        list1.extend([0] * more)
def _recur_get_max_lens(dim, list1, max_lens):
    max_lens[dim] = max(max_lens[dim], len(list1))
    if dim < DIM - 1:
        for list2 in list1:
            _recur_get_max_lens(dim + 1, list2, max_lens)
def _append_stack(list1, list2, count, is_repeat=False):
    list1.append(list2)
    if count != '':
        repeated = list2 if is_repeat else []
        list1.extend([repeated] * (int(count) - 1))

def ch2val(c):
    if c in '.b': return 0
    elif c == 'o': return 255
    elif len(c) == 1: return ord(c)-ord('A')+1
    else: return (ord(c[0])-ord('p')) * 24 + (ord(c[1])-ord('A')+25)

def rle2cells(st):
    stacks = [[] for dim in range(DIM)]
    last, count = '', ''
    delims = list(DIM_DELIM.values())
    st = st.rstrip('!') + DIM_DELIM[DIM - 1]
    for ch in st:
        if ch.isdigit():
            count += ch
        elif ch in 'pqrstuvwxy@':
            last = ch
        else:
            if last + ch not in delims:
                _append_stack(stacks[0], ch2val(last + ch) / 255, count, is_repeat=True)
            else:
                dim = delims.index(last + ch)
                for d in range(dim):
                    _append_stack(stacks[d + 1], stacks[d], count, is_repeat=False)
                    stacks[d] = []
                # print("{0}[{1}] {2}".format(last+ch, count, [np.asarray(s).shape for s in stacks]))
            last, count = '', ''
    A = stacks[DIM - 1]
    max_lens = [0 for dim in range(DIM)]
    _recur_get_max_lens(0, A, max_lens)
    _recur_cubify(0, A, max_lens)
    return np.asarray(A)

from os.path import dirname, join
with open(join(dirname(__file__),"animals.json")) as f:
    animal_list = json.load(f)

animaldict = {}

for animal in animal_list:
    if animal.get("cells"):
        if animal["params"]["kn"] == 1 and animal["params"]["gn"]==1:
            pars = animal["params"]
            bs = pars["b"]
            bs = bs.split(",")
            bs2=[]
            for b in bs:
                if not "/" in b:
                    bs2.append(int(b))
                else:
                    b1, b2 = b.split("/")
                    bs2.append(int(b1)/int(b2))
            animaldict[animal["name"]] = {"R":pars["R"],
                                          "T":pars["T"],
                                          "s":pars["s"],
                                          "m":pars["m"],
                                          "b":bs2,
                                          "cells":rle2cells(animal["cells"])

                                      }

np.save("animals.npy", animaldict)