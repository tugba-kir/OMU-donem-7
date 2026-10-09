# -*- coding: utf-8 -*-
"""PDF üretimi için ortak içe aktarmalar ve yazı tipi kaydı."""
import os, numpy as np, pandas as pd, matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .core import *

def _fonts():
    d = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    pdfmetrics.registerFont(TTFont('DV', os.path.join(d, 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DVB', os.path.join(d, 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DVI', os.path.join(d, 'DejaVuSans-Oblique.ttf')))
    pdfmetrics.registerFontFamily('DV', normal='DV', bold='DVB', italic='DVI', boldItalic='DVB')


__all__ = [_n for _n in dir() if not _n.startswith('__')]
