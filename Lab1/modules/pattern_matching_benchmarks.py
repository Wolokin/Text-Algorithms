from naive_bench import naive
from automaton_bench import automaton
from kmp_bench import kmp
import matplotlib.pyplot as plt


def bench(text, pattern, p=True):
    naive_res = naive(text, pattern)
    automaton_res = automaton(text, pattern)
    kmp_res = kmp(text, pattern)
    if naive_res['matches'] != automaton_res['matches'] or automaton_res['matches'] != kmp_res[
            'matches']:
        print('Matches differ!!!')
        exit()
    if p:
        print('Match count:', len(naive_res['matches']))
        print('naive:', naive_res['times'])
        print('automaton:', automaton_res['times'])
        print('kmp:', kmp_res['times'])
    return naive_res, automaton_res, kmp_res


# Zadanie 1
print('=================Zad1====================')
# Test a, constant m
samples = 1000
s = 1000
text = 'a' * s
pattern = 'a' * s
dnaive, dauto, dkmp = [], [], []
size = []
for i in range(1, samples):
    print(i)
    n, a, k = bench(text * i, pattern, False)
    size.append(i * s)
    dnaive.append(sum(n['times'].values()))
    dauto.append(sum(a['times'].values()))
    dkmp.append(sum(k['times'].values()))
plt.plot(size, dnaive, label='naive')
plt.plot(size, dauto, label='automaton')
plt.plot(size, dkmp, label='kmp')
plt.legend(loc="upper left")
plt.xlabel('text length')
plt.ylabel('time[s]')
plt.title('Test a, constant m = ' + str(len(pattern)))
plt.show()

# Test a, constant n
samples = 1000
s = 100
text = 'a' * s * samples
pattern = 'a' * s
dnaive, dauto, dkmp = [], [], []
size = []
for i in range(1, samples):
    print(i)
    n, a, k = bench(text, pattern * i, False)
    size.append(i * s)
    dnaive.append(sum(n['times'].values()))
    dauto.append(sum(a['times'].values()))
    dkmp.append(sum(k['times'].values()))
plt.plot(size, dnaive, label='naive')
plt.plot(size, dauto, label='automaton')
plt.plot(size, dkmp, label='kmp')
plt.legend(loc="upper left")
plt.xlabel('pattern length')
plt.ylabel('time[s]')
plt.title('Test a, constant n = ' + str(len(text)))
plt.show()

# Test b, constant m
samples = 1000
s = 1000
text = ('a' * (s - 2) + 'b')
pattern = 'a' * (s - 1) + 'b'
dnaive, dauto, dkmp = [], [], []
size = []
for i in range(1, samples):
    print(i)
    n, a, k = bench(text * i, pattern, False)
    size.append(i * s)
    dnaive.append(sum(n['times'].values()))
    dauto.append(sum(a['times'].values()))
    dkmp.append(sum(k['times'].values()))
plt.plot(size, dnaive, label='naive')
plt.plot(size, dauto, label='automaton')
plt.plot(size, dkmp, label='kmp')
plt.legend(loc="upper left")
plt.xlabel('text length')
plt.ylabel('time[s]')
plt.title('Test b, constant m = ' + str(len(pattern)))
plt.show()

# Test b, constant n
samples = 30
s = 100
text = ('a' * (s - 2) + 'b') * samples
pattern = 'a' * (s - 1) + 'b'
dnaive, dauto, dkmp = [], [], []
size = []
for i in range(1, samples):
    print(i)
    n, a, k = bench(text, pattern * i, False)
    size.append(i * s)
    dnaive.append(sum(n['times'].values()))
    dauto.append(sum(a['times'].values()))
    dkmp.append(sum(k['times'].values()))
plt.plot(size, dnaive, label='naive')
plt.plot(size, dauto, label='automaton')
plt.plot(size, dkmp, label='kmp')
plt.legend(loc="upper left")
plt.xlabel('pattern length')
plt.ylabel('time[s]')
plt.title('Test b, constant n = ' + str(len(text)))
plt.show()

# Zadanie 2,3
print('=================Zad2,3====================')
with open("ustawa.txt") as f:
    text = f.read()
    pattern = 'art'
    n, a, k = bench(text, pattern)
    print('n,a,k')
    plt.bar(['naive', 'automaton', 'kmp'],
            [sum(n['times'].values()),
             sum(a['times'].values()),
             sum(k['times'].values())])
    plt.ylabel('time[s]')
    plt.title('Szybkość działania algorytmów na załączonej ustawie\n ze wzorcem \'art\'')
    plt.show()

# Zadanie 4
print('=================Zad4====================')
pattern = "a" * 1000000
text = pattern * 2
n, a, k = bench(text, pattern)
plt.bar(
    ['naive', 'automaton', 'kmp'],
    [n['times']['matching_time'], a['times']['matching_time'], k['times']['matching_time']])
plt.ylabel('time[s]')
plt.title('Szybkość działania algorytmów bez preprocessingu\n n = ' + str(len(text)) +
          ', m = ' + str(len(pattern)))
plt.show()

# Zadanie 5
print('=================Zad5====================')
pattern = 'qwertyuiopasdfghjklzxcvbnm'
text = pattern
n, a, k = bench(text, pattern)
plt.bar(['automaton', 'kmp'], [a['times']['init_time'], k['times']['init_time']])
plt.ylabel('time[s]')
plt.title('Szybkość inicjalizacji struktur\n n = ' + str(len(text)) + ', m = ' +
          str(len(pattern)))
plt.show()
