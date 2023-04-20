'''
Created on May 18, 2022

@author: Devin Burke
'''

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import AutoMinorLocator
from textwrap import wrap
import pandas as pd
import numpy as np
import math
from mhw.utils import get_confidence_interval, standard_error, fpc, func, mean
from mhw.config import pop, zscore
from mhw.read_statistics import get_possible_answers

def make_boxplot(title, desc, flag, lowy, highy, xlabels, series):
    plt.clf()
    xlabels = list(xlabels)
    hconf = []
    lconf = []
    if len(xlabels) != len(series):
        print("The length of xlabels must be the same as the number of data series.")
        return None
    for i, data in enumerate(series):
        data = [i for i in data if not pd.isna(i)]
        xlabels[i] = xlabels[i] + "\n" + str(len(data))
        low, _, high = get_confidence_interval(data)
        hconf.append(high)
        lconf.append(low)  
    conf = np.column_stack((hconf,lconf))
    if len(series) == 1:
        if not series[0]:
            return
    for i, data in enumerate(series):
        if not data:
            if i == len(series)-1:
                return
            continue
    _, ax1 = plt.subplots()
    ax1.set_title(title + "\n" + desc)
    ax1.boxplot(series, notch=True, conf_intervals=conf, showfliers=True, zorder=3)
    ax1.tick_params(direction='in')
    ticks = list(range(1,len(series)+1))
    ax1.set_xticks(ticks)
    ax1.set_xticklabels(xlabels)
    ax1.grid(axis='y', zorder=0)
    if flag == True:
        ax1.set_ylim([lowy, highy])
    plt.savefig(title + "_" + desc + ".png")    
    #plt.show()
    plt.close()

def make_histo(data, title, desc):
    plt.clf()
    data = [i for i in data if not pd.isna(i)]
    if not data:
        return
    _, ax = plt.subplots()
    N, __, patches = ax.hist(data, bins = [-2.5,-1.5,-0.5,0.5, 1.5,2.5], edgecolor='black', linewidth=1, zorder=3)    
    ax.bar_label(patches)
    ax.set_title(title + "\n" + desc)
    ax.set_xticks([-2,-1,0,1,2])
    ax.set_xticklabels(["in crisis", "struggling", "surviving", "thriving", "excelling"])
    ax.grid(axis='y', zorder=0)
    ax.set_ylabel('Respondent count')
    color = {0:'red', 1:'orange', 2:'yellow', 3:'#90EE90', 4:'#013220'}
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(len(N)):
        patches[i].set_facecolor(color[i])
    plt.savefig(title + "_" + desc + ".png")
    #plt.show()
    plt.close()
    
def make_barplot(title, desc, flag, lowy, highy, data_dict, ylabels, minorgridflag = False, xlabels = None):
    plt.clf()
    qflag = False
    if xlabels:
        qflag = True
        if len(xlabels) == len(data_dict.keys()):
            new_dict = {}
            for i, key in enumerate(data_dict.keys()):
                new_dict[xlabels[i]] = data_dict[key]
            data_dict = new_dict
        else:
            raise Exception('The list of xlabels must have a number of entries equal to keys in the data dict')
    filtered = {k: v for k, v in data_dict.items() if v is not None}
    xlabels = list(filtered.keys())
    series = list(filtered.values())   
    means = [None]*len(xlabels)
    errors = [None]*len(xlabels)
    for i, data in enumerate(series):
        data = [i for i in data if not pd.isna(i)]
        if not qflag:
            xlabels[i] = xlabels[i] + "\n" + str(len(data))
        m = mean(data)
        if pd.isna(m):
            continue
        means[i]=(round(m,2))
        try:
            errors[i]=(round(standard_error(data) * zscore * fpc(pop, len(data)), 2))
        except TypeError:
            errors[i]=(0)
    xlabels = [x for i, x in enumerate(xlabels) if not pd.isna(means[i])]
    means = [i for i in means if not pd.isna(i)]
    errors = [i for i in errors if not pd.isna(i)]
    if not xlabels:
        return
    cmap = matplotlib.cm.get_cmap('RdYlGn')    
    colours = []
    for val in means:
        cval = math.fabs(lowy - val)
        cval = cval / (highy - lowy)
        colours.append(matplotlib.colors.to_hex(cmap(cval)))    
    _, ax = plt.subplots()
    xpos = list(range(1,len(xlabels)+1))
    ax.bar(xpos, means, yerr = errors, align='center', alpha=0.5, ecolor='black', capsize=10, zorder=3, color = colours )
    ax.set_yticks(range(lowy, highy+1))
    ax.set_ylim([lowy, highy])
    ax.set_yticklabels(ylabels)
    ax.set_xticks(xpos)
    if qflag:
        ax.set_xticklabels(xlabels)
    else:
        ax.set_xticklabels(xlabels, rotation=45, fontsize=5)
    if minorgridflag == True:
        minor_locator = AutoMinorLocator(2)
        ax.yaxis.set_minor_locator(minor_locator)
        ax.grid(zorder=0, which='minor')
    else:
        ax.grid(axis = 'y')
    ax.set_title(title + "\n" + desc)
    if flag == True:
        ax.set_ylim([lowy, highy])
    ax.tick_params(direction='in')
    plt.savefig(title + "_" + desc + ".png")
    #plt.show()
    plt.close()
    
def pie_chart(code, rows, title, legend_title, counts):
    plt.clf()
    _, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    x = counts
    subs = get_possible_answers(code)
    wedges, __, autotexts = ax.pie(x[0:rows], autopct=lambda pct: func(pct, x[0:rows]) if pct > 0 else '',
                                      textprops=dict(color="w"))  
    ax.legend(wedges, subs,
              title="\n".join(wrap(legend_title)),
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))    
    plt.setp(autotexts, size=8, weight="bold")
    ax.set_title("\n".join(wrap(title)))       
    plt.show()
    plt.close()