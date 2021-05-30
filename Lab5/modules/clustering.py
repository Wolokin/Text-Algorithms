from metrics import cosine_metric, dice_metric, levenshteinC_wrapper, lcs_metric2
from sklearn.cluster import DBSCAN
import numpy as np
from multiprocessing import Pool
from time import time, sleep
from collections import defaultdict
from collections import Counter

MAX_THREADS = 24


def calc_single_distance(a):
    t1, t2, metric = a
    # abs because numerical errors may go slighlty below 0
    return abs(metric(t1, t2))


def distances_parallel(tokens, metric):
    n = len(tokens)
    res = [(tokens[i], tokens[j], metric) for j in range(n) for i in range(n)]
    with Pool(MAX_THREADS) as p:
        res = p.map(calc_single_distance, res)
    res = np.array(res, dtype=np.float64)
    return res.reshape((n, n))


def distances(tokens, metric):
    n = len(tokens)
    res = np.ndarray((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i, n):
            res[i][j] = res[j][i] = abs(metric(tokens[i], tokens[j]))
    return res


def clusterize(lines, metric, original=None, timeit=False):
    t1 = time()
    X = distances_parallel(lines, metric)
    if timeit: print("Calculating distance matrix time:", time() - t1)
    t1 = time()
    clustering = DBSCAN(eps=0.42, min_samples=2, metric='precomputed').fit(X)
    if timeit: print("Calculating clusterization time:", time() - t1)
    d = defaultdict(list)
    for line, label in zip(lines, clustering.labels_):
        d[label].append(line)
    print("Outliers:", len(d[-1]))
    print("Clusters:", len(d))
    t1 = time()
    q = davies_bouldin_index(d, metric)
    if timeit: print("Calculating Davies-Bouldin index time:", time() - t1)
    print("Davies-Bouldin index:", q)
    t1 = time()
    q = dunn_index(d, metric)
    if timeit: print("Calculating Dunn index time:", time() - t1)
    print("Dunn index:", q)
    if original:
        d = defaultdict(list)
        for line, label in zip(original, clustering.labels_):
            d[label].append(line)
    return d


def print_classes(d, f=None):
    s = []
    for k, cluster in d.items():
        s.append(
            f"\n#################################\nclass {k}\n#################################\n"
        )
        for line in cluster:
            s.append(line)
            s.append('\n')
    s = ''.join(s)
    if f:
        with open(f, "w") as fi:
            fi.write(s)
    else:
        print(s)


# Centroid is chosen as a cluster element that
# has the lowest distance to all other cluster elements
def get_centroid_and_avg(cluster, metric):
    n = len(cluster)
    distances = []
    avg = 0
    with Pool(MAX_THREADS) as p:
        for i in range(n):
            dist = p.map(calc_single_distance,
                         [(cluster[i], cluster[j], metric) for j in range(n)])
            s = np.sum(dist)
            distances.append(s)
            avg += s
    centroid = cluster[np.argmin(distances)]
    avg /= n * (n - 1)
    return (centroid, avg)


def davies_bouldin_index(d, metric):
    dcp = d.copy()
    dcp.pop(-1, None)
    n = len(dcp)
    res = 0
    ca = [get_centroid_and_avg(v, metric) for v in dcp.values()]
    for i in range(n):
        lis = [0]
        for j in range(n):
            if i != j:
                (c1, a1) = ca[i]
                (c2, a2) = ca[j]
                lis.append((a1 + a2) / metric(c1, c2))
        res += np.max(lis)
    return res / len(dcp)


def dunn_index(d, metric):
    dcp = d.copy()
    dcp.pop(-1, None)
    tmp = [get_centroid_and_avg(cluster, metric) for cluster in dcp.values()]
    centroids = [x[0] for x in tmp]
    avgs = [x[1] for x in tmp]
    dist = distances_parallel(centroids, metric)
    for i in range(dist.shape[0]):
        dist[i][i] = float("inf")
    dist = np.min(dist)
    size = np.max(avgs)
    return dist / size


def remove_chars(lines, to_replace=None):
    if not to_replace:
        to_replace = ['.', ',', ':', '/', ';', '"']
    else:
        to_replace = [' ' + rep + ' ' for rep in to_replace]
    res = []
    for line in lines:
        res.append(line)
        for a in to_replace:
            res[-1] = res[-1].replace(a, " ")
    return res


def stoplist(lines, n=50):
    return [
        b[0] for b in Counter([t for u in [line.split() for line in lines]
                               for t in u]).most_common(n)
    ]


def remove_stoplist(lines, n=50):
    # Removing dots, commas etc.
    lines = remove_chars(lines)
    # Removing 50 most common words
    res = remove_chars(lines, stoplist(lines))
    # Removing multiple spaces
    for i in range(10):
        res = remove_chars(res, to_replace=[""])
    return res


def test_all():
    with open('../sources/lines.txt') as f:
        lines = f.read().splitlines()
    print("Without stoplist\n####################################")
    print("\nDICE metric")
    print_classes(clusterize(lines, dice_metric), "clusters_dice.txt")
    print("\nCosine metric")
    print_classes(clusterize(lines, cosine_metric), "clusters_cosine.txt")
    print("\nLevenshtein metric")
    print_classes(clusterize(lines, levenshteinC_wrapper), "clusters_levenshtein.txt")
    print("\nLCS metric")
    print_classes(clusterize(lines, lcs_metric2), "clusters_lcs.txt")
    sleep(5)
    print("\n\nWith stoplist\n####################################")
    print("\nDICE metric")
    print_classes(clusterize(remove_stoplist(lines), dice_metric, lines),
                  "clusters_dice_stoplist.txt")
    print("\nCosine metric")
    print_classes(clusterize(remove_stoplist(lines), cosine_metric, lines),
                  "clusters_cosine_stoplist.txt")
    print("\nLevenshtein metric")
    print_classes(clusterize(remove_stoplist(lines), levenshteinC_wrapper, lines),
                  "clusters_levenshtein_stoplist.txt")
    print("\nLCS metric")
    print_classes(clusterize(remove_stoplist(lines), lcs_metric2, lines),
                  "clusters_lcs_stoplist.txt")


def print_lines(lines):
    for line in lines:
        print(line)


if __name__ == '__main__':
    with open('../sources/lines.txt') as f:
        lines = f.read().splitlines()
    # print(stoplist(remove_chars(stoplist(lines))))
    # print_lines(stoplist(remove_chars(lines)))
    # print_lines(remove_stoplist(lines))
    test_all()
