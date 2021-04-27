from enum import Enum


class Step(Enum):
    NO_CHANGE = 0
    DEL = 1
    INS = 2
    REPL = 3


def levenshtein(s1, s2):
    n = len(s1)
    m = len(s2)
    distance = [[0 for i in range(m + 1)] for j in range(n + 1)]
    path = [[0 for i in range(m + 1)] for j in range(n + 1)]
    for i in range(n + 1):
        distance[i][0] = i
        path[i][0] = Step.DEL
    for i in range(m + 1):
        distance[0][i] = i
        path[0][i] = Step.INS
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                distance[i][j] = distance[i - 1][j - 1]
                path[i][j] = Step.NO_CHANGE
            else:
                distance[i][j] = distance[i - 1][j]
                path[i][j] = Step.DEL
                if distance[i][j] > distance[i][j - 1]:
                    distance[i][j] = distance[i][j - 1]
                    path[i][j] = Step.INS
                if distance[i][j] > distance[i - 1][j - 1]:
                    distance[i][j] = distance[i - 1][j - 1]
                    path[i][j] = Step.REPL
                distance[i][j] += 1
    return distance[n][m], path


def visualize(s1, s2, path):
    i = len(s1)
    j = len(s2)
    steps = []
    while i != 0 or j != 0:
        c = path[i][j]
        steps.append(c)
        if c == Step.DEL:
            i -= 1
        elif c == Step.INS:
            j -= 1
        else:
            i -= 1
            j -= 1
    steps.reverse()
    text = s1
    print(text)
    i, j = 0, 0
    for c in steps:
        if c == Step.INS:
            print(text[:i] + '(+' + s2[j] + ')' + text[i:])
            text = text[:i] + s2[j] + text[i:]
            i += 1
            j += 1
        elif c == Step.DEL:
            print(text[:i] + '(-' + text[i] + ')' + text[i + 1:])
            text = text[:i] + text[i + 1:]
        elif c == Step.NO_CHANGE:
            i += 1
            j += 1
        else:
            print(text[:i] + '(' + text[i] + '->' + s2[j] + ')' + text[i + 1:])
            text = text[:i] + s2[j] + text[i + 1:]
            i += 1
            j += 1
    print(text)


if __name__ == '__main__':
    t1, t2 = "los", "kloc"
    dist, path = levenshtein(t1, t2)
    visualize(t1, t2, path)
    print(dist)
    t1, t2 = "Łódź", "Lodz"
    dist, path = levenshtein(t1, t2)
    visualize(t1, t2, path)
    print(dist)
    t1, t2 = "kwintesencja", "quintessence"
    dist, path = levenshtein(t1, t2)
    visualize(t1, t2, path)
    print(dist)
    t1, t2 = "ATGAATCTTACCGCCTCG", "ATGAGGCTCTGGCCCCTG"
    dist, path = levenshtein(t1, t2)
    visualize(t1, t2, path)
    print(dist)

    t1, t2 = "ab", "cd"
    dist, path = levenshtein(t1, t2)
    visualize(t1, t2, path)
    print(dist)
