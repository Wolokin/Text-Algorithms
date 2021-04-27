from mc_creight_final_attempt import suffixTreeFastWrapper, suffixTreeSlowWrapper
from trie import create_trie
from time import time
import matplotlib.pyplot as plt


def benchmark(funclist,
              datlist,
              labels,
              titles,
              axis_labels=None,
              repeats=None,
              save_to_file=False):
    if repeats is None:
        repeats = 1
    for dat, title in zip(datlist, titles):
        times = dict()
        for func, label in zip(funclist, labels):
            for _ in range(repeats):
                t1 = time()
                func(dat)
                t2 = time()
                times[label] = times.get(label, 0) + (t2 - t1) / repeats
        plt.bar(times.keys(), times.values())
        plt.title(title)
        for i, v in enumerate(times.values()):
            plt.annotate(str(round(v, 7)), xy=(i, v), ha='center', va='bottom')
        if axis_labels is not None:
            plt.xlabel(axis_labels['x'])
            plt.ylabel(axis_labels['y'])

        if save_to_file:
            plt.savefig(title + ".png")
        plt.show()


if __name__ == '__main__':
    with open("1997_714_head.txt") as ustawa:
        funclist = [create_trie, suffixTreeSlowWrapper, suffixTreeFastWrapper]
        datlist = [
            "bbbd", "aabbabd", "ababcd", "abcbccd",
            ustawa.read()[:2000] + "\uF000", "abc" * 1000 + "d"
        ]
        labels = ["trie", "suffixSlow", "suffixFast"]
        titles = [s for s in datlist]
        titles[-2] = "1997_714_head"
        titles[-1] = "\'abc\'*1000+'d'"
        axis_labels = {'x': 'Construction method', 'y': 'time [s]'}
        benchmark(funclist, datlist, labels, titles, axis_labels, 100, True)
