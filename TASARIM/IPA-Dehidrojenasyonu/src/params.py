# -*- coding: utf-8 -*-
"""Tasarım parametreleri (PAR)."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *
from .data import *
from .thermo import *

PAR = dict(
    GRUP=8, CAP_TON_YIL=85000.0, SAAT=8000.0,
    W_SU_URUN=0.004,       # [VARSAYIM] ürün suyu kütle kesri 0,4 % (şart: en çok 0,5 %; 0,1 puan emniyet payı)
    W_IPA_BESLEME=0.88,    # taze besleme azeotrop yakını IPA, kütle %88 (Turton/Rice)
    X=0.90,                # [VARSAYIM] tek geçiş dönüşümü (Turton: %85-92)
    T_R=350.0, T_6=300.0,  # reaktör sıcaklığı; E-101 soğuk çıkış (kızgın buhar)
    T_FL=40.0, T_ABS=35.0, T_SU=25.0, T_PA_HOT=40.0, T_PA_COLD=30.0,
    A_ABS=1.4,             # absorpsiyon faktörü (literatür aralığı 1,2-2 / 1,4-2, aralığın alt ucu)
    REC_ACE_ABS=0.995,     # [VARSAYIM] aseton geri kazanımı (absorber)
    REC_ACE_C1=0.999, REC_IPA_C2=0.995,
    AZ_WT=0.878,           # IPA-su azeotropu kütle kesri (patentler) -> geri dönüş bileşimi
    RR_FACTOR=1.3,         # R = 1.3 x Rmin
    ETA_POMPA=0.70, ETA_FIRIN=0.85, EXCESS_AIR=0.15,
    T_SALT_HOT=450.0, T_SALT_COLD=390.0, CP_SALT=1.56,   # [DOGRULANMADI] Hitec benzeri nitrat/nitrit tuzu Cp kJ/kg/K
    T_FLUE=250.0, T_FUEL=25.0, T_AIR=25.0,
    P={1: 1.0, 2: 1.1, 3: 1.0, 4: 3.2, 5: 2.8, 6: 2.6, 7: 2.2, 8: 2.0, 9: 1.8, 10: 1.8, 11: 1.8, 12: 3.0, 13: 1.7,
       14: 1.8, 15: 1.3, 16: 1.1, 17: 1.0, 18: 1.3, 19: 1.3, 42: 1.8, 43: 2.3, 44: 2.1,
       45: 1.1, 46: 1.1, 47: 1.1, 48: 1.3, 49: 1.3, 50: 1.1, 51: 1.1, 52: 1.1, 53: 1.3, 54: 1.3},
    P_COL1=(1.1, 1.3), P_COL2=(1.1, 1.3),
)


__all__ = [_n for _n in dir() if not _n.startswith('__')]
