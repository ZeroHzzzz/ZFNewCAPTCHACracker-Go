import requests
import time
import cv2
import numpy as np
import random
import json
import base64
import math
from flask import Flask, request

app = Flask(__name__)

DEBUG = False
# DEBUG = True

ZF_URL = "http://www.gdjw.zjut.edu.cn/jwglxt/"
# ZF_URL = "http://172.16.19.163/jwglxt/"

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
extend = 'eyJhcHBOYW1lIjoiTmV0c2NhcGUiLCJ1c2VyQWdlbnQiOiJNb3ppbGxhLzUuMCAoTWFjaW50b3NoOyBJbnRlbCBNYWMgT1MgWCAxMF8xNV83KSBBcHBsZVdlYktpdC82MDUuMS4xNSAoS0hUTUwsIGxpa2UgR2Vja28pIFZlcnNpb24vMTYuNiBTYWZhcmkvNjA1LjEuMTUiLCJhcHBWZXJzaW9uIjoiNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzYwNS4xLjE1IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xNi42IFNhZmFyaS82MDUuMS4xNSJ9'

timeout = 10


def getRtk(cookie):
    url = f"{ZF_URL}zfcaptchaLogin?type=resource&instanceId=zfcaptchaLogin&name=zfdun_captcha.js"

    response = requests.get(url, headers={'Cookie': cookie}, timeout=timeout)
    if response.status_code == 200:
        res = response.text
        rtk = res[res.find('rtk:')+5:res.find('rtk:')+32+9]
        if DEBUG:
            print(f"rtk:{str(rtk)}")
        return rtk
    return None


def getImageInfo(rtk, cookie):
    t = int(round(time.time() * 1000))
    url = f"{ZF_URL}zfcaptchaLogin?type=refresh&rtk={rtk}&time={t}&instanceId=zfcaptchaLogin"

    response = requests.get(
        url, headers={'User-Agent': UA, 'Cookie': cookie}, timeout=timeout)

    if(response.status_code == 200):
        res = response.json()
        if DEBUG:
            print(res['si'], res['imtk'], res['mi'], t, res['t'])
        return res['si'], res['imtk'], res['mi'], res['t']
    return None, None, None, None


def getImage(id, imtk, cookie, t):
    url = f"{ZF_URL}zfcaptchaLogin?type=image&id={id}&imtk={imtk}&t={str(t)}&instanceId=zfcaptchaLogin"

    response = requests.get(
        url, headers={'User-Agent': UA, 'Cookie': cookie}, timeout=timeout)

    if(response.status_code == 200):
        return cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
    return None


def imMatch(target, template):
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target = abs(255 - target)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    if DEBUG:
        print(x, y)
    return y


def genMT(x, t):
    res = []

    x1 = 620
    y = 240.0
    t1 = 0

    for _ in range(random.randint(2, 8)):
        x1 += random.randint(-1, 1)
        res.append({"x": x1, "y": int(y), "t": t})
        t += random.randint(5, 10)

    ft, tmax = genSpeed(x)

    while t1 <= tmax:
        x1 += int(ft(t1) * 5)
        y += (random.random() - 0.5) * 0.3
        res.append({"x": x1, "y": int(y), "t": t + t1})
        t1 = t1 + 5

    for _ in range(random.randint(5, 30)):
        x1 += random.randint(-1, 1)
        y += (random.random() - 0.5) * 0.3
        res.append({"x": x1, "y": int(y), "t": t + t1})
        t1 += random.randint(20, 100)

    if DEBUG:
        print(t1, tmax, x1 - 620)
    return json.dumps(res).replace(" ", ""), res[-1]['t']


def genSpeed(xmax):
    a1 = 1.5 / 100
    a2 = -a1
    div = 0.5
    tmax = math.sqrt(2 * xmax / (a1 * div))
    b1 = 0.1
    b2 = -a2 * tmax + 0.1
    def f1(t): return a1 * t + b1
    def f2(t): return a2 * t + b2

    def fgen(t):
        if t <= div * tmax:
            return f1(t)
        else:
            return f2(t)
    return fgen, tmax


def postAuth(mt, rtk, cookie, t):
    url = f"{ZF_URL}zfcaptchaLogin"
    data = {'type': 'verify', 'rtk': rtk, 'mt': mt, 'time': t,
            'instanceId': 'zfcaptchaLogin', 'extend': extend}
    r = requests.post(url, data=data, headers={
                      'User-Agent': UA, 'Cookie': cookie}, timeout=timeout)

    if r.status_code == 200:
        if DEBUG:
            print(r.json())
        return r.json()['status']
    return None


def authSession(cookie):
    st = time.time()
    rtk = getRtk(cookie)
    if rtk is None:
        return "ZF Die"
    si, imtk, mi, t = getImageInfo(rtk, cookie)
    if si is None:
        return "ZF Die"

    target = getImage(si, imtk, cookie, t)
    if target is None:
        return "Session Error"
    template = getImage(mi, imtk, cookie, t)
    if template is None:
        return "Session Error"
    et = time.time()
    if DEBUG:
        print("stge 1:", et-st)
    st = time.time()
    x = imMatch(template, target)
    et = time.time()
    if DEBUG:
        print("stge 2:", et-st)
    mt, et = genMT(x, t)

    dt = et - t

    if DEBUG:
        print(f"t:{t}, et:{et}, dt:{dt}")
        print(mt)

    status = postAuth(base64.b64encode(mt.encode('utf-8')), rtk, cookie, et)
    if status is None:
        return "ZF Die"
    return status


@ app.route('/')
def index():
    session = request.args.get('session')
    route = request.args.get('route')
    if DEBUG:
        print(session, route)

    cookie = f"JSESSIONID={session}; route={route}"

    for _ in range(5):
        try:
            status = authSession(cookie)
            if status == "Session Error":
                return {"status": 400, "msg": "Session Error"}
            elif status == "ZF Die":
                return {"status": 500, "msg": "ZF Die"}
            elif status == "success":
                return {"status": 0, "msg": "Success"}
        except Exception as e:
            print(e)
            return {"status": 500, "msg": "Server Error"}
    return "Die"


def runserver():
    app.run(host='0.0.0.0', port=8080, debug=DEBUG)


if __name__ == '__main__':
    runserver()
