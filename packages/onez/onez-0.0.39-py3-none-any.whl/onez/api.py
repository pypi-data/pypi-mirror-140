#!/usr/bin/env python
#-*- coding:utf-8 -*-

def mysum(*args):
    s = 0
    for v in args:
        i = float(v)
        s += i
    print('0.38'+str(s))