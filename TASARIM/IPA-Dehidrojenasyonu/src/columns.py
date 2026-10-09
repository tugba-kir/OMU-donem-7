# -*- coding: utf-8 -*-
"""Kısa yol kolon ve absorber fonksiyonları (Rmin, Kremser)."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *
from .thermo import *
from .params import *

def _y_eq_binary(x1, P, pair):
    """İkili denge: pair=(i,j) hafif=i. Dönüş y_i (Wilson)"""
    i, j = pair; idx = (i, j); x = np.array([x1, 1 - x1])
    T = brentq(lambda T: float(np.sum(x * gamma(x, T, idx) * np.array([Psat(k, T) for k in idx]))) - P, 1, 250)
    g = gamma(x, T, idx); return x1 * g[0] * Psat(i, T) / P, T

def rmin_binary(xD, z, q, P, pair):
    """McCabe-Thiele minimum reflü: R_min = max_x (xD - y*)/(y* - x),  x in [x_q, xD)"""
    if abs(q - 1.0) < 1e-9: xq = z
    else:
        fq = lambda x: _y_eq_binary(x, P, pair)[0] - (q * x - z) / (q - 1.0)
        xq = brentq(fq, 1e-5, min(z, xD - 1e-4)) if fq(1e-5) * fq(min(z, xD - 1e-4)) < 0 else z
    xs = np.linspace(xq, xD - 1e-3, 120)
    r = []
    for x in xs:
        y = _y_eq_binary(x, P, pair)[0]
        r.append((xD - y) / (y - x) if y > x + 1e-9 else np.inf)
    return max(r), xq

def kremser_N(A, R): return np.log((A - R) / (1 - R)) / np.log(A) - 1.0


__all__ = [_n for _n in dir() if not _n.startswith('__')]
