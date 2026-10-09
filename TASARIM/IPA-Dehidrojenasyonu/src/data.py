# -*- coding: utf-8 -*-
"""Bileşen verileri (mol kütlesi, oluşum entalpisi, Cp, yoğunluk, Shomate katsayıları)."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from .common import *

NAMES = ['IPA', 'Aseton', 'H2', 'Su']
MW = np.array([60.095, 58.079, 2.016, 18.015])          # kg/kmol
T_REF = 298.15
HFV = np.array([-272.6e3, -217.1e3, 0.0, -241.826e3])    # J/mol gaz fazı oluşum entalpisi, 25 °C [DOGRULANDI]
# Buharlaşma entalpisi 25 °C (J/mol): IPA 45.34 (NIST/Chemeo), aseton 31.27 (NIST), su 43.99 (=40.65 kJ/mol@100 °C + ∫(Cpl-Cpg)dT, tutarlılık testi verify_data'da)
DHVAP = np.array([45.34e3, 31.27e3, 0.0, 43.99e3])
HFL = HFV - DHVAP
CPL = np.array([155.2, 125.45, 28.84, 75.3])             # sıvı Cp J/mol/K (sabit; su 75.3 = 4.18 kJ/kg/K x 18.015)
RHO = np.array([786., 790., 1., 997.])                   # kg/m3  (IPA 786 Wikipedia 20 °C [DOGRULANDI]; su 997; aseton ~790)

SHO_H2 = (33.066178, -11.363417, 11.432816, -2.772874, -0.158558)           # NIST Shomate 298-1000 K [DOGRULANDI]
SHO_H2O = (30.09200, 6.832514, 6.793435, -2.534480, 0.082139)                # NIST Shomate 500-1700 K; 298 K'de 33.59 (NIST 33.58) [DOGRULANDI/uzatma testli]
ACE_TAB = np.array([[298.15, 75.02], [300., 75.32], [400., 92.06], [500., 108.08], [600., 122.20], [700., 134.43]])
IPA_TAB = np.array([[358.72, 103.06], [373.15, 106.29], [398.15, 111.65], [423.15, 117.02], [448.15, 122.10],
                    [473.15, 127.01], [499.75, 130.30], [539.05, 137.50], [567.05, 142.60], [597.25, 148.10]])
P_ACE = np.poly1d(np.polyfit(ACE_TAB[:, 0], ACE_TAB[:, 1], 3))
P_IPA = np.poly1d(np.polyfit(IPA_TAB[:, 0], IPA_TAB[:, 1], 2))

__all__ = [_n for _n in dir() if not _n.startswith('__')]
