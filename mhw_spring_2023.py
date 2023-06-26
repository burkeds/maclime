"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""
import pandas as pd
import numpy as np
from textwrap import wrap
from mhw.read_results import get_included_responses, get_results
from mhw.scoring import get_scored_data, get_value_dict
from mhw.utils import standard_error, fpc, get_confidence_interval, mwu_test
from mhw.figures import make_histo, plot_impact_statistics
from mhw.read_statistics import get_all_questions, get_subquestion

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

__all__ = ['mh2',
           'ae0',
           'ae1',
           'ae2',
           'ae21',
           'ae3',
           'ae4',
           'ae5',
           'ae6']


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


def _get_stats_comparison(*args, include=None, description="", include_other=None, print_table=False):
    """
    Gets the statistics for the given questions and subquestions.
    :param args: Any number of question codes or subquestion codes.
    :param include: An include array.
    :param description: Description of inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :return: A dataframe with the statistics for the given questions and subquestions.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
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
    frames = []
    for codes in args:
        frames.append(pd.DataFrame(index=codes, columns=stats))
    for i in range(len(frames)):
        df = frames[i]
        df.attrs['include'] = include
        df.attrs['include_comp'] = include_comp
        df.attrs['description'] = description
        df.attrs['sample_size'] = ALL_RESPONDENTS
        df.attrs['population_size'] = POP
        df.attrs['included_respondents'] = len(include)
        df.attrs['complementary_respondents'] = len(include_comp)

        first_code = df.index[0]
        df.attrs['question'] = QUESTIONS[first_code].question
        df.attrs['possible_answers'] = QUESTIONS[first_code].possible_answers
        for code in df.index.tolist():
            df.loc[code, 'subquestion'] = get_subquestion(code)
            responses = get_included_responses(code, include)
            scores = np.array(get_scored_data(code, responses))
            scores = [i for i in scores if not pd.isna(i)]
            scores_inc = scores.copy()
            df.attrs['include_responses'] = responses
            df.attrs['include_scores'] = scores_inc
            if len(scores) > 1:
                df.loc[code, 'mean'] = float(np.mean(scores))
                df.loc[code, 'moe'] = float(standard_error(scores) * ZSCORE * fpc(POP, len(scores)))
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
            scores = np.array(get_scored_data(code, responses))
            scores = [i for i in scores if not pd.isna(i)]
            scores_comp = scores.copy()
            df.attrs['complementary_responses'] = responses
            df.attrs['complementary_scores'] = scores_comp
            if len(scores) > 1:
                df.loc[code, 'comp_mean'] = float(np.mean(scores))
                df.loc[code, 'comp_moe'] = float(standard_error(scores) * ZSCORE * fpc(POP, len(scores)))
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
                df.loc[code, 'pvalue'] = float(mwu_test(scores_inc, scores_comp))
            else:
                df.loc[code, 'pvalue'] = None
        frames[i] = df.replace(pd.NA, np.nan)
        if print_table:
            print("********************************************************************")
            print("Top question text: {}".format(df.attrs['question']))
            print("Possible answers: {}".format(df.attrs['possible_answers']))
            print(df.round(2).to_csv(sep='\t'))
            print("********************************************************************")
    if len(frames) == 1:
        return frames[0]
    else:
        return frames


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
    mh2_stats = _get_stats_comparison(codes,
                                      include=include,
                                      description=description,
                                      include_other=include_comp,
                                      print_table=print_table)
    if make_figures:
        make_histo(mh2_stats, "Mental_health_continuum", description, save_figure=save_fig)
        make_histo(mh2_stats, "Mental_health_continuum", description, complementary=True, save_figure=save_fig)


def ae0(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the social perception.
    :param include: An include array of respondents.
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
    codes = ['AE0(SQ001)',
             'AE0(SQ002)',
             'AE0(SQ003)',
             'AE0(SQ004)',
             'AE0(SQ005)',
             'AE0(SQ006)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Social perception", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Social perception", complement=True, save_figure=save_fig)
    return stats


def ae1(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the department perception.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for the department perception.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE1(SQ001)',
             'AE1(SQ002)',
             'AE1(SQ003)',
             'AE1(SQ004)',
             'AE1(SQ005)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Department perception", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Department perception", complement=True, save_figure=save_fig)
    return stats


def ae2(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the graduate student workload.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for graduate student workload.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE2(SQ001)',
             'AE2(SQ002)',
             'AE2(SQ003)',
             'AE2(SQ004)',
             'AE2(SQ005)',
             'AE2(SQ006)',
             'AE2(SQ007)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Graduate student workload", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Graduate student workload", complement=True, save_figure=save_fig)
    return stats


def ae21(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the TA workload.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for TA workload.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE21(SQ001)',
             'AE21(SQ002)',
             'AE21(SQ003)',
             'AE21(SQ004)',
             'AE21(SQ005)',
             'AE21(SQ006)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="TA workload", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="TA workload", complement=True, save_figure=save_fig)
    return stats


def ae3(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the undergraduate workload.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for undergraduate workload.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE3(SQ001)',
             'AE3(SQ002)',
             'AE3(SQ003)',
             'AE3(SQ004)',
             'AE3(SQ005)',
             'AE3(SQ006)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Undergraduate workload", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Undergraduate workload", complement=True, save_figure=save_fig)
    return stats


def ae4(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the co-op workload.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for co-op workload.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE4(SQ001)',
             'AE4(SQ002)',
             'AE4(SQ003)',
             'AE4(SQ004)',
             'AE4(SQ005)',
             'AE4(SQ006)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Co-op workload", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Co-op workload", complement=True, save_figure=save_fig)
    return stats


def ae5(include, description="", include_other=None, print_table=False, make_figures=False, save_fig=False):
    """
    Gets the statistics for the undergraduate thesis experience.
    :param include: An include array of respondents.
    :param description: A description of the inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :param make_figures: When true, makes figures.
    :param save_fig: When true, saves figures.
    :return: A dataframe with the statistics for undergraduate thesis experience.
    """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    codes = ['AE5(SQ001)',
             'AE5(SQ002)',
             'AE5(SQ003)',
             'AE5(SQ004)',
             'AE5(SQ005)']
    stats = _get_stats_comparison(codes,
                                  include=include,
                                  description=description,
                                  include_other=include_comp,
                                  print_table=print_table)
    if make_figures:
        plot_impact_statistics(stats, title="Undergraduate thesis experience", complement=False, save_figure=save_fig)
        plot_impact_statistics(stats, title="Undergraduate thesis experience", complement=True, save_figure=save_fig)
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
    impact_stats = _get_stats_comparison(codes,
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
