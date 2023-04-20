'''
Created on May 18, 2022

@author: Devin Burke
This file contains configuration variables used by many different functions.
These variables will change for any given survey.
'''
from matplotlib import rc
import pandas as pd

#Read the results and stats files into a python pandas object
results_file = pd.read_excel('./results/results-survey265235_2023.xls', header=None)
statistics_file = pd.read_excel('./results/statistic-survey265235_2023.xls', header=None)

#Variables used to read statistics file
last_row = 1099
max_responses = 44

#Sample size. The number of all respondents in main file
all_respondents = 43

#zscore for 95% confidence interval
zscore = 1.96

#Estimate population size of cohort
pop = 350

#Font used by matplotlib in figures
font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 10}
rc('font', **font)