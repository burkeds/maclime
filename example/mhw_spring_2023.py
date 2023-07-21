"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""
import math
import textwrap

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

from mhw.read_results import get_results, get_included_responses
from mhw.questions import get_questions

from mhw.config import get_config
from mhw.read_statistics import get_subquestion, get_possible_answers
from mhw.scoring import get_scored_data
from mhw.utils import mwu_test, standard_error, fpc, get_confidence_interval

CONFIG = get_config()
ZSCORE = CONFIG.get_zscore()
POP = CONFIG.get_population()
ALL_RESPONDENTS = CONFIG.get_all_respondents()
RESULTS = get_results()
QUESTIONS = get_questions(codes='ALL')
INCLUDE_ALL = CONFIG.get_include_all()

if not RESULTS.empty:
    from mhw.include_arrays import *


# Store dictionaries that map responses to arbitrary
# numerical values valid for a list of questions.
# This is passed to the configuration object returned by mhw.config.get_config().
def get_value_dict(code):
    """
    Returns a dictionary that maps responses to arbitrary numerical values for a given question code.
    :param code: The question code
    :return: A dictionary that maps responses to arbitrary numerical values
    """
    agree_list = ['AE1(SQ001)',
                  'AE1(SQ001)',
                  'AE1(SQ002)',
                  'AE1(SQ003)',
                  'AE1(SQ004)',
                  'AE1(SQ005)']
    freq_list = ['MH0(SQ001)',
                 'MH0(SQ002)',
                 'MH0(SQ003)',
                 'MH0(SQ004)',
                 'MH0(SQ005)',
                 'MH1(SQ001)',
                 'MH1(SQ002)',
                 'MH1(SQ003)',
                 'MH1(SQ004)',
                 'MH1(SQ005)',
                 'MH1(SQ006)',
                 'AE0(SQ001)',
                 'AE0(SQ002)',
                 'AE0(SQ003)',
                 'AE0(SQ004)',
                 'AE0(SQ005)',
                 'AE0(SQ006)',
                 'AE2(SQ001)',
                 'AE2(SQ002)',
                 'AE2(SQ003)',
                 'AE2(SQ004)',
                 'AE2(SQ005)',
                 'AE2(SQ006)',
                 'AE2(SQ007)',
                 'AE2(SQ008)',
                 'AE2(SQ009)',
                 'AE2(SQ016)',
                 'AE21(SQ001)',
                 'AE21(SQ002)',
                 'AE21(SQ003)',
                 'AE21(SQ004)',
                 'AE21(SQ005)',
                 'AE21(SQ006)',
                 'AE3(SQ001)',
                 'AE3(SQ002)',
                 'AE3(SQ003)',
                 'AE3(SQ004)',
                 'AE3(SQ005)',
                 'AE3(SQ006)',
                 'AE4(SQ001)',
                 'AE4(SQ002)',
                 'AE4(SQ003)',
                 'AE4(SQ004)',
                 'AE4(SQ005)',
                 'AE4(SQ006)',
                 'AE5(SQ001)',
                 'AE5(SQ002)',
                 'AE5(SQ003)',
                 'AE5(SQ004)',
                 'AE5(SQ005)']
    pos_neg_list = ['AE6(SQ001)',
                    'AE6(SQ002)',
                    'AE6(SQ003)',
                    'AE6(SQ004)',
                    'AE6(SQ005)',
                    'AE6(SQ006)',
                    'AE6(SQ007)',
                    'AE6(SQ008)',
                    'AE6(SQ009)',
                    'AE6(SQ010)']
    if code in freq_list:
        return {'None of the time': 0,
                'Rarely': 1,
                'Some of the time': 2,
                'Most of the time': 3,
                'All of the time': 4}
    elif code in pos_neg_list:
        return {'Strongly negative': -2,
                'Negative': -1,
                'Neutral': 0,
                'Positive': 1,
                'Strongly positive': 2}
    elif code == 'MH2':
        return {'In crisis': -2,
                'Struggling': -1,
                'Surviving': 0,
                'Thriving': 1,
                'Excelling': 2}
    elif code in agree_list:
        return {'Strongly disagree': -3,
                'Disagree': -2,
                'Somewhat disagree': -1,
                'Neither agree nor disagree': 0,
                'Somewhat agree': 1,
                'Agree': 2,
                'Strongly agree': 3}
    else:
        return None


# This is an example of a function performing useful statistical analysis using methods from mhw.
# This should be used as a callback function passed to mhw.analysis.analyze().
def get_stats_comparison(codes,
                         include=None,
                         title="",
                         description="",
                         include_other=None,
                         print_table=False,
                         p_test=mwu_test):
    """
    Gets the statistics for the given questions and subquestions.
    :param codes: Any number of question codes.
    :param include: An include array.
    :param title: Title of the analysis.
    :param description: Description of inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param p_test: The p-test to use. This is mhw.utils.mwu_test() by default but any callback function that takes two
                   arrays and returns a float can be substituted.
    :return: A dataframe with the statistics for the given questions and subquestions.
    """
    config = get_config()
    include_all = config.get_include_all()
    all_respondents = config.get_all_respondents()
    population = config.get_population()
    zscore = config.get_zscore()
    questions = get_questions(codes='ALL')
    include_comp = include_other
    if not include:
        include = include_all
    if not include_comp:
        include_comp = subtract_include(include_all, include)
    stats = ['subquestion',
             'mean',
             'moe',
             'lconf',
             'median',
             'hconf',
             'comp_mean',
             'comp_moe',
             'comp_lconf',
             'comp_median',
             'comp_hconf',
             'pvalue']
    df = pd.DataFrame(index=codes, columns=stats)
    df.attrs['include'] = include
    df.attrs['include_comp'] = include_comp
    df.attrs['title'] = title
    df.attrs['description'] = description
    df.attrs['sample_size'] = all_respondents
    df.attrs['population_size'] = population
    df.attrs['included_respondents'] = len(include)
    df.attrs['complementary_respondents'] = len(include_comp)

    first_code = df.index[0]
    df.attrs['question'] = questions[first_code].question
    df.attrs['possible_answers'] = questions[first_code].possible_answers
    for code in df.index.tolist():
        df.loc[code, 'subquestion'] = get_subquestion(code)
        responses = get_included_responses(code, include)
        scores = np.array(get_scored_data(responses, code))
        scores = [i for i in scores if not pd.isna(i)]
        scores_inc = scores.copy()
        df.attrs['include_responses'] = responses
        df.attrs['include_scores'] = scores_inc
        if len(scores) > 1:
            df.loc[code, 'mean'] = float(np.mean(scores))
            df.loc[code, 'moe'] = float(standard_error(scores) * zscore * fpc(population, len(scores)))
            lconf, median, hconf = get_confidence_interval(scores)
            df.loc[code, 'lconf'] = float(lconf)
            df.loc[code, 'median'] = float(median)
            df.loc[code, 'hconf'] = float(hconf)
        else:
            df.loc[code, 'mean'] = None
            df.loc[code, 'moe'] = None
            df.loc[code, 'lconf'] = None
            df.loc[code, 'median'] = None
            df.loc[code, 'hconf'] = None

        responses = get_included_responses(code, include_comp)
        scores = np.array(get_scored_data(responses, code))
        scores = [i for i in scores if not pd.isna(i)]
        scores_comp = scores.copy()
        df.attrs['complementary_responses'] = responses
        df.attrs['complementary_scores'] = scores_comp
        if len(scores) > 1:
            df.loc[code, 'comp_mean'] = float(np.mean(scores))
            df.loc[code, 'comp_moe'] = float(standard_error(scores) * zscore * fpc(population, len(scores)))
            lconf, median, hconf = get_confidence_interval(scores)
            df.loc[code, 'comp_lconf'] = float(lconf)
            df.loc[code, 'comp_median'] = float(median)
            df.loc[code, 'comp_hconf'] = float(hconf)
        else:
            df.loc[code, 'comp_mean'] = None
            df.loc[code, 'comp_moe'] = None
            df.loc[code, 'comp_lconf'] = None
            df.loc[code, 'comp_median'] = None
            df.loc[code, 'comp_hconf'] = None

        if scores_inc and scores_comp:
            df.loc[code, 'pvalue'] = float(p_test(scores_inc, scores_comp))
        else:
            df.loc[code, 'pvalue'] = None
    df = df.replace(pd.NA, np.nan)
    if print_table:
        print("********************************************************************")
        print("Top question text: {}".format(df.attrs['question']))
        print("Possible answers: {}".format(df.attrs['possible_answers']))
        print(df.round(2).to_csv(sep='\t'))
        print("********************************************************************")
    return df


# This is a function used to produce a desired figure. Can be used as a callback function in analyze.
def make_histo(frame, title, description, complement=False, save_figure=False, x_labels=None, y_label=None):
    """
    Makes a histogram of the data in the given frame.
    :param frame: The frame to be plotted
    :param title: The title of the plot
    :param description: The description of the plot
    :param complement: Whether to use the complementary scores
    :param save_figure: Whether to save the figure
    :param x_labels: The labels for the x axis
    :param y_label: The labels for the y axis
    :return:
    """
    plt.clf()
    sample = frame.attrs['sample_size']

    if complement:
        data = frame.attrs['complementary_scores']
        included_respondents = frame.attrs['complementary_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
        description = "(comp)" + description
    else:
        data = frame.attrs['include_scores']
        included_respondents = frame.attrs['included_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
    title += res_str

    if not x_labels:
        x_labels = frame.attrs['possible_answers']
    bad_labels = ['Not applicable', 'No answer', 'Not completed or Not displayed']
    x_labels = [x for x in x_labels if x not in bad_labels]

    if not y_label:
        y_label = 'Respondent count'
    _, ax = plt.subplots()
    arrays, __, patches = ax.hist(data,
                                  bins=[-2.5, -1.5, -0.5, 0.5, 1.5, 2.5],
                                  edgecolor='black',
                                  linewidth=1, zorder=3)
    ax.bar_label(patches)
    ax.set_title(title + "\n" + description)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels(x_labels)
    ax.grid(axis='y', zorder=0)
    ax.set_ylabel(y_label)
    color = {0: 'red', 1: 'orange', 2: 'yellow', 3: '#90EE90', 4: '#013220'}
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(len(arrays)):
        patches[i].set_facecolor(color[i])
    if save_figure:
        plt.savefig(title + "_" + description + ".png")
    plt.show()


# Another option for a figure callback function. Produces a bar chart.
def plot_impact_statistics(frame=None,
                           complement=False,
                           title="",
                           description="",
                           x_labels=None,
                           y_label=None,
                           include_sample_size=True,
                           save_figure=False):
    """
    Plots the impact statistics for the given question.
    :param frame: The impact statistics for the question
    :param complement: Whether to plot the complementary statistics
    :param title: The title of the plot
    :param description: The description of the plot
    :param x_labels: The labels for the x-axis
    :param y_label: The label for the y-axis
    :param include_sample_size: Whether to include the sample size in the title
    :param save_figure: Whether to save the figure
    :return:
    """
    if frame is None:
        raise Exception("No dataframe given.")
    plt.clf()
    df = frame
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
        if not y_label:
            y_label = get_possible_answers(code)
            bad_labels = ['Not applicable', 'No answer', 'Not completed or Not displayed']
            y_label = [label for label in y_label if label not in bad_labels]
            y_label = ['\n'.join(textwrap.wrap(label, 10)) for label in y_label]

    # Add valid respondents to x_label
    for i, label in enumerate(x_labels):
        question_code = df.index[i]
        responses = get_included_responses(question_code, include)
        scores = get_scored_data(responses, question_code)
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
        ax.set_yticklabels(y_label)
        ax.set_xticklabels(x_labels, rotation=45, fontsize=5.5)
        ax.set_ylim([low_y, high_y])
        ax.tick_params(direction='in')
        if save_figure:
            plt.savefig(title + ".png")
        plt.show()
