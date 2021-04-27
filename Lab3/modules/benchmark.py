from lempel_ziv_welch import LZW
from static_huffman import StaticHuffman, StaticCompressor
from dynamic_huffman import DynamicHuffmanCompressor
from time import time
import matplotlib.pyplot as plt
from os.path import getsize


def benchmark(funclist, datlist, labels, repeats=None):
    if repeats is None:
        repeats = 1
    xs = []
    ys = []
    for dat in datlist:
        times = dict()
        for func, label in zip(funclist, labels):
            for _ in range(repeats):
                t_enc, t_dec = func(dat)
                key1, key2 = label + '\nencoding', label + '\ndecoding'
                times[key1] = times.get(key1, 0) + (t_enc / repeats)
                times[key2] = times.get(key2, 0) + (t_dec / repeats)
        xs.append(times.keys())
        ys.append(times.values())
    return xs, ys


def compression_ratio_benchmark(funclist, datlist, labels, repeats=1):
    xs = []
    ys = []
    for dat in datlist:
        times = dict()
        for func, label in zip(funclist, labels):
            for _ in range(repeats):
                ratio = func(dat)
                key = label + '\n'
                times[key] = times.get(key, 0) + (ratio) / repeats
        xs.append(times.keys())
        ys.append(times.values())
    return xs, ys


def plot_factory(xs, ys, titles, axis_labels=None, save_to_file=False, display=True):
    for i in range(len(xs)):
        plt.bar(xs[i], ys[i])
        plt.title(titles[i])
        for j, v in enumerate(ys[i]):
            plt.annotate(str(round(v, 7)), xy=(j, v), ha='center', va='bottom')
        if axis_labels is not None:
            plt.xlabel(axis_labels['x'])
            plt.ylabel(axis_labels['y'])

        if save_to_file:
            plt.savefig("plots/" + titles[i] + ".png", bbox_inches='tight')
        if display:
            plt.show()


def universal_compression_wrapper(source_filename, compressed_filename, C):
    uncompressed = getsize('../sources/' + source_filename)
    with open('../sources/' + source_filename, "r") as f:
        text = f.read()
    C.encode(text)
    compressed = getsize(compressed_filename)
    return 1 - (compressed / uncompressed)


def LZW_compression_benchmark_wrapper(source_filename):
    filename = 'compressed.lzw'
    C = LZW(filename)
    return universal_compression_wrapper(source_filename, filename, C)


def static_compression_benchmark_wrapper(source_filename):
    filename = 'compressed.static'
    C = StaticCompressor(filename, StaticHuffman)
    return universal_compression_wrapper(source_filename, filename, C)


def dynamic_compression_benchmark_wrapper(source_filename):
    filename = 'compressed.dynamic'
    C = DynamicHuffmanCompressor(filename)
    return universal_compression_wrapper(source_filename, filename, C)


def universal_wrapper(source_filename, C):
    with open('../sources/' + source_filename, "r") as f:
        text = f.read()
    t_enc1 = time()
    C.encode(text)
    t_enc2 = time()
    t_dec1 = time()
    C.decode()
    t_dec2 = time()
    return t_enc2 - t_enc1, t_dec2 - t_dec1


def LZW_benchmark_wrapper(source_filename):
    C = LZW('compressed.lzw')
    return universal_wrapper(source_filename, C)


def static_benchmark_wrapper(source_filename):
    C = StaticCompressor('compressed.static', StaticHuffman)
    return universal_wrapper(source_filename, C)


def dynamic_benchmark_wrapper(source_filename):
    C = DynamicHuffmanCompressor('compressed.dynamic')
    return universal_wrapper(source_filename, C)


if __name__ == '__main__':
    labels = ["LZW", "Static", "Dynamic"]
    datlist = [
        name + str(i) + 'kB.txt'
        for i in [1, 10, 100, 1000]
        for name in ['guttenberg_krzyzacy_eng_ascii', 'merged_linux_source_ascii', 'uniform']
    ]
    # time benchmarks
    funclist = [LZW_benchmark_wrapper, static_benchmark_wrapper, dynamic_benchmark_wrapper]
    xs, ys = benchmark(funclist, datlist, labels, 10)
    # compression ratio benchmarks
    funclist = [
        LZW_compression_benchmark_wrapper, static_compression_benchmark_wrapper,
        dynamic_compression_benchmark_wrapper
    ]
    xs2, ys2 = compression_ratio_benchmark(funclist, datlist, labels)
    # Plotting
    titles = [s + " - times" for s in datlist]
    plot_factory(xs, ys, titles, {'x': 'Algorithm', 'y': 'Time [s]'}, True)
    titles = [s + " - compression ratio" for s in datlist]
    plot_factory(xs2, ys2, titles, {'x': 'Algorithm', 'y': 'Compression ratio'}, True)
