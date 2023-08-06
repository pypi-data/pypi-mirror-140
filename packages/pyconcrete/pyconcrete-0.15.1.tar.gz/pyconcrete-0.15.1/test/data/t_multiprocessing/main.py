#!/usr/bin/env python
# -*- coding: utf8 -*-
# Create on : 2019/07/13
from __future__ import unicode_literals
from multiprocessing import Pool


def sqrt(x):
    return x*x


if __name__ == '__main__':
    with Pool(5) as p:
        for r in p.map(sqrt, [1, 2, 3]):
            print(r)
