"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""
import pandas as pd
import numpy as np
from textwrap import wrap

from mhw.analysis import get_stats_comparison
from mhw.read_results import get_results
from mhw.scoring import get_value_dict
from mhw.figures import make_histo, plot_impact_statistics
from mhw.questions import get_all_questions

from mhw.config import get_config
CONFIG = get_config()
ZSCORE = CONFIG.get_zscore()
POP = CONFIG.get_population()
ALL_RESPONDENTS = CONFIG.get_all_respondents()
RESULTS = get_results()
QUESTIONS = get_all_questions()
INCLUDE_ALL = CONFIG.get_include_all()

if not RESULTS.empty:
    from mhw.include_arrays import *
    from mhw.include_arrays import subtract_include


def _get_academic_impact(resp_id):
    """
    Gets the academic impact score for the given respondent.
    :param resp_id: The respondent ID
    :return: The academic impact score for the given respondent.
    """
    resp_id = int(resp_id)
    impact_codes = ['AE6(SQ001)',
                    'AE6(SQ002)',
                    'AE6(SQ003)',
                    'AE6(SQ004)',
                    'AE6(SQ005)',
                    'AE6(SQ006)',
                    'AE6(SQ007)',
                    'AE6(SQ008)',
                    'AE6(SQ009)',
                    'AE6(SQ010)']
    xs = RESULTS[impact_codes].xs(resp_id)
    responses = xs.to_dict()
    scores = []
    for code in impact_codes:
        value = get_value_dict(code)
        response = responses[code]
        score = value[response]
        if not pd.isna(score):
            scores.append(score)
    else:
        score_mean = np.array(scores).mean()
        return score_mean


def mh2(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the mental health continuum.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return:
    """
    codes = ['MH2']
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    mh2_stats = get_stats_comparison(codes,
                                     include=include,
                                     description=description,
                                     include_other=include_comp,
                                     print_table=print_table)
    if make_figures:
        make_histo(mh2_stats, "Mental_health_continuum", description, save_figure=save_fig)
        make_histo(mh2_stats, "Mental_health_continuum", description, complementary=True, save_figure=save_fig)


def analyze_ae(include, codes=None, title="", description="", include_other=None, print_table=False, make_figures=False,
               save_fig=False):
    """
        Gets the statistics for the social perception.
        :param include: An include array of respondents.
        :param codes: The question codes to analyze.
        :param title: The title of the analysis.
        :param description: A description of the inclusion criteria.
        :param include_other: Another include array for comparison.
        :param print_table: When true, prints the table to the console.
        :param make_figures: When true, makes figures.
        :param save_fig: When true, saves figures.
        :return: A dataframe with the statistics for social perception.
        """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    stats = get_stats_comparison(codes,
                                 include=include,
                                 description=description,
                                 include_other=include_comp,
                                 print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title=title, complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title=title, complement=True, save_figure=save_fig)
    return stats


def ae6(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the impact of academics on wellness.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for impact of academics on wellness.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE6(SQ001)',
             'AE6(SQ002)',
             'AE6(SQ003)',
             'AE6(SQ004)',
             'AE6(SQ005)',
             'AE6(SQ006)',
             'AE6(SQ007)',
             'AE6(SQ008)',
             'AE6(SQ009)',
             'AE6(SQ010)']
    impact_stats = get_stats_comparison(codes,
                                        include=include,
                                        description=description,
                                        include_other=include_comp,
                                        print_table=print_table)
    title = "Impact of academics on wellness"
    xlabels = ["classwork",
               "labwork",
               "testing",
               "research/thesis",
               "co-op",
               "TAs",
               "faculty/admin",
               "non-P&A",
               "students",
               "not academic"]
    xlabels = ['\n'.join(wrap(label, 20)) for label in xlabels]
    ylabels = ["strongly negative", "negative", "neutral", "positive", "strongly positive"]
    ylabels = ['\n'.join(wrap(label, 10)) for label in ylabels]

    if make_figures:
        plot_impact_statistics(impact_stats,
                               complement=False,
                               title=title,
                               x_labels=xlabels,
                               y_labels=ylabels,
                               save_figure=save_fig)
        plot_impact_statistics(impact_stats,
                               complement=True,
                               title=title,
                               x_labels=xlabels,
                               y_labels=ylabels,
                               save_figure=save_fig)
    return impact_stats
