"""
Created on Apr. 12, 2022

@author: Devin Burke
This file contains various general purpose utility functions
"""

from mhw.config import zscore, pop
import pandas as pd
import numpy as np
import math
from scipy.stats import mannwhitneyu  


def char_split(word):
    return [char for char in word]


def merge(s):
    new = ""
    for x in s:
        new += x
    return new


def func(pct, allvals):
    absolute = int(np.round(pct/100.*np.sum(allvals)))
    return "{:.1f}%\n({:d})".format(pct, absolute)


# Returns the median and lower/upper limits of the median confidence interval
def get_confidence_interval(data):
    data = [i for i in data if not pd.isna(i)]
    if not data:
        return None, None, None
    data.sort()        
    j = math.ceil(len(data) * 0.5 + (zscore * fpc(pop, len(data)) * math.sqrt(len(data) * 0.5 * (1-0.5))))
    k = math.ceil(len(data) * 0.5 - (zscore * fpc(pop, len(data)) * math.sqrt(len(data) * 0.5 * (1-0.5))))
    if 0 < j < (len(data)-1):
        hconf = data[j]
    else:
        hconf = data[-1]
    if 0 < k < (len(data)-1):
        lconf = data[k]
    else:
        lconf = data[0]
    median = np.median(data)    
    return lconf, median, hconf


#  True if the median or confidence interval have type None or are nan
def conf_check(lconf, median, hconf):
    if pd.isna(lconf):
        return True
    elif pd.isna(median):
        return True
    elif pd.isna(hconf):
        return True
    return False


# Returns the standard error of an array
def standard_error(sample):
    sample = [i for i in sample if not pd.isna(i)]
    if not sample:
        return None
    if len(sample) == 1:
        return None
    se = np.std(sample) * np.std(sample)
    se = se / len(sample)
    se = math.sqrt(se)
    return se


def mean(data):
    data = [i for i in data if not pd.isna(i)]
    if len(data) == 1:
        return data[0]
    if not data:
        return None
    avg = np.mean(data)
    return avg


# finite population correction
# Use when n/N > 0.05
def fpc(N, n):
    cor = N-n
    cor = cor/(N-1)
    cor = math.sqrt(cor)
    return cor


# Perform MannWhitneyU test for two datasets and return pvalue
def mwu_test(data, comp):
    data = [i for i in data if not pd.isna(i)]
    if not data:
        return None
    comp = [i for i in comp if not pd.isna(i)]
    if not data or not comp:
        return None
    if len(data) < 8:
        pval = mannwhitneyu(data, comp, method='exact').pvalue
    else:
        pval = mannwhitneyu(data, comp).pvalue
    return pval


def add(x, y):
    if pd.isna(x):
        return y
    elif pd.isna(y):
        return x
    elif pd.isna(x) and pd.isna(y):
        return None
    else:
        return x + y
