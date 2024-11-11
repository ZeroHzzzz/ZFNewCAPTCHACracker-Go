import matplotlib.pyplot as plt
import json
import math
import random


def read_data_from_json(data: str):
    '''read x y t data'''
    x = []
    y = []
    t = []
    data = json.loads(data)
    for i in data:
        x.append(i['x'])
        y.append(i['y'])
        t.append(i['t'])

    return x, y, t


def draw_map(x, y):
    plt.plot(x, y)
    plt.show()


def draw_vxt(x, t):
    vx = []
    for i in range(len(x)-1):
        vx.append((x[i+1]-x[i])/(t[i+1]-t[i]))
    plt.plot(t[:-1], vx)
    plt.show()


def draw_xy(x, y):
    plt.scatter(x, y)
    plt.show()


def gen(vmax, tmax):
    t0 = tmax / 3
    a1 = vmax / (t0 ** 2)
    a2 = vmax / (2 * tmax / 3) ** 2
    def f1(t): return a1 * t ** 2
    def f2(t): return a2 * (t - tmax)**2

    def fgen(t):
        if t <= t0:
            return f1(t)
        else:
            return f2(t)
    x = [0]
    v = [0]
    t = [0]
    for i in range(10, tmax, 10):
        x.append(x[-1] + v[-1] * 10)
        v.append(fgen(i))
        t.append(i)
    plt.plot(t, v)
    plt.show()


def gen2(xmax, tmax):
    t0 = tmax / 3
    vmax = 2 * xmax / tmax
    a1 = vmax / t0
    a2 = vmax / (t0 - tmax)
    b2 = -a2 * tmax
    def f1(t): return a1 * t
    def f2(t): return a2 * t + b2

    def fgen(t):
        if t <= t0:
            return f1(t) + (random.random()) * 0.1
        else:
            return f2(t) + (random.random() - 1) * 0.1
    x = [0]
    v = [0]
    t = [0]
    for i in range(10, tmax, 10):
        x.append(x[-1] + v[-1] * 10)
        v.append(fgen(i))
        t.append(i)
    print(xmax, x[-1])
    plt.plot(t, v)
    plt.show()


def gen3(xmax):
    a1 = 1.5 / 100
    a2 = -a1
    div = 0.5
    tmax = math.sqrt(2 * xmax / (a1 * div))
    b2 = -a2 * tmax
    def f1(t): return a1 * t
    def f2(t): return a2 * t + b2

    def fgen(t):
        if t <= div * tmax:
            return f1(t) + (random.random()) * 0.1
        else:
            return f2(t) + (random.random() - 1) * 0.1
    return fgen, tmax


def draw():
    x = [0]
    v = [0]
    t = [0]
    fgen, tmax = gen3(100)
    for i in range(10, int(tmax), 10):
        x.append(x[-1] + v[-1] * 10)
        v.append(fgen(i))
        t.append(i)

    plt.plot(t, v)
    plt.show()
    plt.scatter(t, x)
    plt.show()


if __name__ == "__main__":
    with open("xy.data", "r") as f:
        data = f.read()

    x, y, t = read_data_from_json(data)
    print(x[-1] - x[0])
    draw_vxt(x, t)
    draw_xy(x, y)
    # draw()
