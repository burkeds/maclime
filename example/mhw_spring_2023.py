"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""

from mhw.analysis import get_stats_comparison
from mhw.read_results import get_results
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


def analyze_ae(include, codes=None, title="", description="", include_other=None, print_table=None,
               figure_callback=None, callback_args=None):
    """
        Perform some sort of statistical analysis on a set of question codes with a set of inclusion criteria defined
        by an include array. It will perform a complementary analysis based on the complement of the include array.
        This method accepts a callback function to produce a figure if desired. It will pass the statistics dataframe
        and some arguments to the callback.

        :param include: An include array of respondents.
        :param codes: The question codes to analyze.
        :param title: The title of the analysis.
        :param description: A description of the inclusion criteria.
        :param include_other: Another include array for comparison.
        :param print_table: When true, prints the table to the console.
        :param figure_callback: A callback function which is passed the statistics dataframe and some arguments
                                to produce a figure.
        :param callback_args: A dictionary of keyword arguments to pass to the figure callback function.
        :return: A dataframe with the statistics for social perception.
        """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    stats = get_stats_comparison(codes,
                                 include=include,
                                 title=title,
                                 description=description,
                                 include_other=include_comp,
                                 print_table=print_table)

    if figure_callback:
        figure_callback(**callback_args, complement=False)
        figure_callback(**callback_args, complement=True)

    return stats


# Store dictionaries that map responses to arbitrary
# numerical values valid for a list of questions.
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
    if code in pos_neg_list:
        return {'Strongly negative': -2,
                'Negative': -1,
                'Neutral': 0,
                'Positive': 1,
                'Strongly positive': 2}
    if code == 'MH2':
        return {'In crisis': -2,
                'Struggling': -1,
                'Surviving': 0,
                'Thriving': 1,
                'Excelling': 2}
    if code in agree_list:
        return {'Strongly disagree': -3,
                'Disagree': -2,
                'Somewhat disagree': -1,
                'Neither agree nor disagree': 0,
                'Somewhat agree': 1,
                'Agree': 2,
                'Strongly agree': 3}
