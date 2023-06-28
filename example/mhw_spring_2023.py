"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""

from mhw.analysis import get_stats_comparison
from mhw.read_results import get_results
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
               save_fig=False, x_labels=None, y_labels=None):
    """
        Perform a statistical analysis on the academic experience questions.

        :param include: An include array of respondents.
        :param codes: The question codes to analyze.
        :param title: The title of the analysis.
        :param description: A description of the inclusion criteria.
        :param include_other: Another include array for comparison.
        :param print_table: When true, prints the table to the console.
        :param make_figures: When true, makes figures.
        :param save_fig: When true, saves figures.
        :param x_labels: The x labels for the figures.
        :param y_labels: The y labels for the figures.
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
        plot_impact_statistics(stats,
                               title=title,
                               complement=False,
                               save_figure=save_fig,
                               x_labels=x_labels,
                               y_label=y_labels)
        plot_impact_statistics(stats,
                               title=title,
                               complement=True,
                               save_figure=save_fig,
                               x_labels=x_labels,
                               y_label=y_labels)
    return stats
