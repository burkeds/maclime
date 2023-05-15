"""
Created on May 18, 2022

@author: Devin Burke
"""

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
from mhw.scoring import get_value_dict
from mhw.read_results import get_included_responses
from mhw.scoring import get_scored_data


def make_histo(frame, title, description, complementary=False):
    plt.clf()
    sample = frame.attrs['sample_size']
    if complementary:
        data = frame.attrs['complementary_scores']
        included_respondents = frame.attrs['complementary_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
        description = "(comp)" + description
    else:
        data = frame.attrs['include_scores']
        included_respondents = frame.attrs['included_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
    title += res_str

    _, ax = plt.subplots()
    N, __, patches = ax.hist(data, bins=[-2.5, -1.5, -0.5, 0.5, 1.5, 2.5], edgecolor='black', linewidth=1, zorder=3)
    ax.bar_label(patches)
    ax.set_title(title + "\n" + description)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels(["in crisis", "struggling", "surviving", "thriving", "excelling"])
    ax.grid(axis='y', zorder=0)
    ax.set_ylabel('Respondent count')
    color = {0: 'red', 1: 'orange', 2: 'yellow', 3: '#90EE90', 4: '#013220'}
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(len(N)):
        patches[i].set_facecolor(color[i])
    # plt.savefig(title + "_" + desc + ".png")
    plt.show()
    # plt.close()


def plot_impact_statistics(impact_statistics,
                           complement=False,
                           title="",
                           x_labels=None,
                           y_labels=None,
                           include_sample_size=True):
    plt.clf()
    df = impact_statistics
    code = df.index[0]

    included_respondents = df.attrs['included_respondents']
    sample_size = df.attrs['sample_size']
    description = df.attrs['description']
    include = df.attrs['include']
    mean_df = df['mean']
    moe_df = df['moe']

    if complement:
        included_respondents = df.attrs['complementary_respondents']
        sample_size = df.attrs['sample_size']
        description = "(comp)" + df.attrs['description']
        include = df.attrs['include_comp']
        mean_df = df['comp_mean']
        moe_df = df['comp_moe']

    # Add information about sample size
    if include_sample_size:
        res_str = "(" + str(included_respondents) + " of " + str(sample_size) + ")"
        description = description + res_str

    if include_sample_size:
        # Generate labels if not specified
        if not x_labels:
            x_labels = df.index.tolist()
        if not y_labels:
            y_labels = get_possible_answers(code)
            bad_labels = ['Not applicable', 'No answer', 'Not completed or Not displayed']
            y_labels = [label for label in y_labels if label not in bad_labels]
            y_labels = ['\n'.join(wrap(label, 10)) for label in y_labels]

    # Add valid respondents to x_label
    for i, label in enumerate(x_labels):
        question_code = df.index[i]
        responses = get_included_responses(question_code, include)
        scores = get_scored_data(question_code, responses)
        valid = len(scores)
        p_value = df['pvalue'][question_code]
        x_labels[i] += "\n {}".format(valid)
        x_labels[i] += "\n {}".format(round(p_value, 2))

    # Get bar colours from colourmap
    cmap = matplotlib.colormaps['RdYlGn']
    colours = []
    low_y = min(list(get_value_dict(code).values()))
    high_y = max(list(get_value_dict(code).values()))
    for val in mean_df.values.tolist():
        cval = math.fabs(low_y - val)
        cval = cval / (high_y - low_y)
        colours.append(matplotlib.colors.to_hex(cmap(cval)))
    if mean_df.dropna().values.tolist():
        # Create plot axis
        title = title + "\n" + description
        ax = mean_df.plot.bar(color=colours, title=title, yerr=moe_df, capsize=4)
        ax.set_yticks(range(low_y, high_y + 1))
        ax.set_yticklabels(y_labels)
        ax.set_xticklabels(x_labels, rotation=45, fontsize=5.5)
        ax.set_ylim([low_y, high_y])
        ax.tick_params(direction='in')
        plt.show()
