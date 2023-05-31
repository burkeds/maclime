"""
Created on May 18, 2022

@author: Devin Burke
This file contains configuration variables used by many different functions.
These variables will change for any given survey.
"""

from matplotlib import rc
import pandas as pd

# Read the results and stats files into a python pandas dataframe
try:
    results_file = pd.read_excel(r"C:\Users\burkeds\Documents\git\mhwpy\working\results\results-survey265235_2023.xls",
                                 header=0, skiprows=[1], index_col=0)
except FileNotFoundError as _:
    results_file = pd.DataFrame()
try:
    statistics_file = pd.read_excel(r"C:\Users\burkeds\Documents\git\mhwpy\working\results\statistic-survey265235_2023.xls",
                                    header=None)
except FileNotFoundError as _:
    statistics_file = pd.DataFrame()

# Sample size. The number of all respondents in results file
all_respondents = 33

# zscore for 95% confidence interval
zscore = 1.96

# Estimate population size of cohort
pop = 350

# Font used by matplotlib in figures
font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 10}
rc('font', **font)
