from enum import Enum


class Step(Enum):
    MATCH = 0
    LEFT = 1
    UP = 2


def lcs(s1, s2):
    n = len(s1)
    m = len(s2)
    length = [[0 for i in range(m + 1)] for j in range(n + 1)]
    path = [[0 for i in range(m + 1)] for j in range(n + 1)]
    for i in range(n + 1):
        length[i][0] = 0
        path[i][0] = Step.UP
    for i in range(m + 1):
        length[0][i] = 0
        path[0][i] = Step.LEFT
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                length[i][j] = length[i - 1][j - 1] + 1
                path[i][j] = Step.MATCH
            else:
                length[i][j] = length[i - 1][j]
                path[i][j] = Step.UP
                if length[i][j] < length[i][j - 1]:
                    length[i][j] = length[i][j - 1]
                    path[i][j] = Step.LEFT
    return length[n][m], visualize(s1, s2, path)


def visualize(s1, s2, path):
    i = len(s1)
    j = len(s2)
    subseq = []
    while i != 0 or j != 0:
        c = path[i][j]
        if c == Step.UP:
            i -= 1
        elif c == Step.LEFT:
            j -= 1
        else:
            i -= 1
            j -= 1
            subseq.append(s1[i])
    subseq.reverse()
    return subseq


if __name__ == '__main__':
    t1, t2 = "los", "kloc"
    count, ss = lcs(t1, t2)
    print(count, ''.join(ss))
    t1, t2 = "Łódź", "Lodz"
    count, ss = lcs(t1, t2)
    print(count, ''.join(ss))
    t1, t2 = "kwintesencja", "quintessence"
    count, ss = lcs(t1, t2)
    print(count, ''.join(ss))
    t1, t2 = "ATGAATCTTACCGCCTCG", "ATGAGGCTCTGGCCCCTG"
    count, ss = lcs(t1, t2)
    print(count, ''.join(ss))
