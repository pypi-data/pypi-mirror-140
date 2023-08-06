#!/usr/bin/env python
# -*- coding: utf8 -*-
# Create on : 2019/07/13
from __future__ import unicode_literals

print('HEAD')
from math import sqrt
import sys
print(sys.path)
print('HEAD2')
from joblib import Parallel, delayed
print('HEAD3')
p = Parallel(n_jobs=2, prefer='threads')(delayed(sqrt)(i ** 2) for i in range(10))
print('Hello')
print(p)
print('World')
