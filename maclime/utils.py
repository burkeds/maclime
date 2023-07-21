"""
Created on Apr. 12, 2022

@author: Devin Burke
This file contains various general purpose utility functions
"""

import pandas as pd
import numpy as np
import math
from scipy.stats import mannwhitneyu  

from maclime.config import get_config
CONFIG = get_config()


def char_split(word):
    """
    Splits a string into a list of characters.
    :param word: The string
    :return: A list of characters
    """
    return [char for char in word]


def merge(s):
    """
    Merges a list of characters into a string.
    :param s: The list of characters
    :return: The string
    """
    new = ""
    for x in s:
        new += x
    return new


# Returns the median and lower/upper limits of the median confidence interval
def get_confidence_interval(data):
    """
    Returns the median and lower/upper limits of the median confidence interval.
    :param data: The data
    :return: The median and lower/upper limits of the median confidence interval
    """
    zscore = CONFIG.get_zscore()
    pop = CONFIG.get_population()
    data = [i for i in data if not pd.isna(i)]
    if not data:
        return None, None, None
    data.sort()        
    j = math.ceil(len(data) * 0.5 + (zscore * fpc(pop, len(data)) * math.sqrt(len(data) * 0.5 * (1 - 0.5))))
    k = math.ceil(len(data) * 0.5 - (zscore * fpc(pop, len(data)) * math.sqrt(len(data) * 0.5 * (1 - 0.5))))
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


# Returns the standard error of an array
def standard_error(sample):
    """
    Returns the standard error of an array.
    :param sample: The array
    :return: The standard error
    """
    sample = [i for i in sample if not pd.isna(i)]
    if not sample:
        return None
    if len(sample) == 1:
        return None
    se = np.std(sample) * np.std(sample)
    se = se / len(sample)
    se = math.sqrt(se)
    return se


# finite population correction
# Use when n/N > 0.05
def fpc(population_size, sample_size):
    """
    finite population correction
    :param population_size: Population size
    :param sample_size: Sample size
    :return: finite population correction
    """
    cor = population_size - sample_size
    cor = cor/(population_size - 1)
    cor = math.sqrt(cor)
    return cor


# Perform MannWhitneyU test for two datasets and return pvalue
def mwu_test(data, comp):
    """
    Perform MannWhitneyU test for two datasets and return pvalue.
    :param data: The data
    :param comp: The comparison data
    :return: The p-value
    """
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
