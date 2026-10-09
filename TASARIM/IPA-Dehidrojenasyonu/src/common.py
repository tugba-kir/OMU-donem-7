# -*- coding: utf-8 -*-
"""Ortak yardımcılar: akım numaralama haritası ve 4 anlamlı rakam biçimlendirici."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq

MAP = {}                      # eski (iç) akım no -> PFD'deki soldan-sağa akım no
def nn(k): return MAP.get(k, k)
def f4(x):
    """4 anlamlı rakama yuvarlanmış metin (SI; örn. 1234.5678 -> 1235, 0.0123456 -> 0.01235)"""
    import math
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))): return '-'
    if x == 0: return '0'
    if abs(x) < 1e-3: return f"{x:.3g}"
    d = 3 - int(math.floor(math.log10(abs(x))))
    v = round(x, d)
    return f"{v:.0f}" if d <= 0 else f"{v:.{d}f}"


__all__ = [_n for _n in dir() if not _n.startswith('__')]
