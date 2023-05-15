"""
Created on April 27, 2023

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""
import pandas as pd
import numpy as np
from textwrap import wrap
from mhw.config import zscore, pop, all_respondents
from mhw.read_results import get_included_responses, get_results
from mhw.scoring import get_value_dict, get_scored_data
from mhw.utils import standard_error, fpc, get_confidence_interval, mwu_test
from mhw.read_statistics import get_subquestion, get_possible_answers, get_top_question
from mhw.figures import make_histo
from mhw.include_arrays import include_all, subtract_include
from mhw.figures import plot_impact_statistics
from mhw.include_arrays import inc_under
from mhw.scoring import get_value_dict
from mhw.read_statistics import get_possible_answers

results = get_results()


def _get_academic_impact(resp_id):
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
    xs = results[impact_codes].xs(resp_id)
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
    include_comp = include_other
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
    frames = []
    for codes in args:
        frames.append(pd.DataFrame(index=codes, columns=stats))
    for i in range(len(frames)):
        df = frames[i]
        df.attrs['include'] = include
        df.attrs['include_comp'] = include_comp
        df.attrs['description'] = description
        df.attrs['sample_size'] = all_respondents
        df.attrs['population_size'] = pop
        df.attrs['included_respondents'] = len(include)
        df.attrs['complementary_respondents'] = len(include_comp)
        for code in df.index.tolist():
            df.loc[code, 'subquestion'] = get_subquestion(code)

            responses = get_included_responses(code, include)
            scores = np.array(get_scored_data(code, responses))
            scores = [i for i in scores if not pd.isna(i)]
            scores_inc = scores.copy()
            df.attrs['include_responses'] = responses
            df.attrs['include_scores'] = scores_inc

            if scores:
                df.loc[code, 'mean'] = float(np.mean(scores))
                df.loc[code, 'moe'] = float(standard_error(scores) * zscore * fpc(pop, len(scores)))
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
                df.loc[code, 'comp_moe'] = float(standard_error(scores) * zscore * fpc(pop, len(scores)))
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
            print("Calculate the impact score of specific academic experiences on mental health")
            print("with respect to the mental health continuum.")
            print("Impact score scaled from -2 (strongly negative) to +2 (strongly positive).")
            print("Top question:\t,", get_top_question(df.index[0]))
            print(df.round(2).to_csv(sep='\t'))
            print("********************************************************************")
    if len(frames) == 1:
        return frames[0]
    else:
        return frames


def ae6(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, inc_under)
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
    xlabels = ['\n'.join(wrap(l, 20)) for l in xlabels]
    ylabels = ["strongly negative", "negative", "neutral", "positive", "strongly positive"]
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    plot_impact_statistics(impact_stats,
                           complement=False,
                           title=title,
                           x_labels=xlabels,
                           y_labels=ylabels)
    plot_impact_statistics(impact_stats,
                           complement=True,
                           title=title,
                           x_labels=xlabels,
                           y_labels=ylabels)
    return impact_stats


def mh2(include, description="", include_other=None, print_table=False):
    codes = ['MH2']
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, inc_under)
    mh2_stats = _get_stats_comparison(codes,
                                      include=include,
                                      description=description,
                                      include_other=include_comp,
                                      print_table=print_table)

    make_histo(mh2_stats, "Mental_health_continuum", description)
    make_histo(mh2_stats, "Mental_health_continuum", description, complementary=True)


def ae0_ae1(include, description, include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, inc_under)
    codes = ['AE0(SQ001)',
             'AE0(SQ002)',
             'AE0(SQ003)',
             'AE0(SQ004)',
             'AE0(SQ005)',
             'AE0(SQ006)',
             'AE1(SQ001)',
             'AE1(SQ002)',
             'AE1(SQ003)',
             'AE1(SQ004)',
             'AE1(SQ005)']
    impact_stats = _get_stats_comparison(codes,
                                         include=include,
                                         description=description,
                                         include_other=include_comp,
                                         print_table=print_table)

    return impact_stats

if __name__ == "__main__":
    mh2(inc_under, "Undergraduates")
    dfae0 = ae0_ae1(inc_under, "undergraduates")

# OLD

def ae0_and_ae1(include, desc, other_include=None):
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE0(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE0(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE0(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE0(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE0(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE0(SQ006)': [None, None, None, None, None, None, None, None, None],
                 'AE1(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE1(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE1(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE1(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE1(SQ005)': [None, None, None, None, None, None, None, None, None]}

    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("Perceptions and feelings")
    print("Questions AE0(SQ001)-AE0(SQ006) are scored on a scale from 0-4 representing numerical values assigned to the"
          " possible answers.")
    print(get_possible_answers('AE0(SQ001)')[0:5])
    print("Questions AE1(SQ001)-AE1(SQ005) are scored on a scale from -3-3 representing numerical values assigned to"
          " the possible answers.")
    print(get_possible_answers('AE1(SQ001)')[0:7])
    print("\n")
    print("Top question: ", get_top_question('AE0(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae0 = {'AE0(SQ001)': None,
                     'AE0(SQ002)': None,
                     'AE0(SQ003)': None,
                     'AE0(SQ004)': None,
                     'AE0(SQ005)': None,
                     'AE0(SQ006)': None}
    for code in data_dict_ae0.keys():
        data_dict_ae0[code] = data_dict[code][1]
    data_dict_ae0_comp = {'AE0(SQ001)': None,
                          'AE0(SQ002)': None,
                          'AE0(SQ003)': None,
                          'AE0(SQ004)': None,
                          'AE0(SQ005)': None,
                          'AE0(SQ006)': None}
    for code in data_dict_ae0_comp.keys():
        data_dict_ae0_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    make_barplot("Social_perception" + res_str, desc, True, 0, 4, data_dict_ae0, ylabels)
    make_barplot("Social_perception" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae0_comp, ylabels)
    make_barplot("Social_perception", desc, True, 0, 4, data_dict_ae0, ylabels, xlabels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5',
                                                                                         'Q6'])

    data_dict_ae1 = {'AE1(SQ001)': None,
                     'AE1(SQ002)': None,
                     'AE1(SQ003)': None,
                     'AE1(SQ004)': None,
                     'AE1(SQ005)': None}
    for code in data_dict_ae1.keys():
        data_dict_ae1[code] = data_dict[code][1]
    data_dict_ae1_comp = {'AE1(SQ001)': None,
                          'AE1(SQ002)': None,
                          'AE1(SQ003)': None,
                          'AE1(SQ004)': None,
                          'AE1(SQ005)': None}
    for code in data_dict_ae1_comp.keys():
        data_dict_ae1_comp[code] = data_dict[code][2]
    ylabels = ['Strongly disagree', 'Disagree', 'Somewhat disagree', 'Neither agree nor disagree', 'Somewhat agree',
               'Agree', 'Strongly agree']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    make_barplot("Department_perception" + res_str, desc, True, -3, 3, data_dict_ae1, ylabels)
    make_barplot("Department_perception" + res_str_comp, "(comp)" + desc, True, -3, 3, data_dict_ae1_comp, ylabels)
    make_barplot("Department_perception", desc, True, -3, 3, data_dict_ae1, ylabels, xlabels=['Q1', 'Q2', 'Q3', 'Q4',
                                                                                              'Q5'])


def ae2(include, desc, other_include=None):
    # Questions about workload for graduate students
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE2(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ006)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ007)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ008)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ009)': [None, None, None, None, None, None, None, None, None],
                 'AE2(SQ016)': [None, None, None, None, None, None, None, None, None]}
    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("Graduate student workload")
    print("Questions AE2(SQ001)-AE2(SQ016) are scored on a scale from 0-4 representing numerical values assigned to the"
          " possible answers.")
    print(get_possible_answers('AE2(SQ001)')[0:5])
    print("\n")
    print("Top question: ", get_top_question('AE2(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae = {'AE2(SQ001)': None,
                    'AE2(SQ002)': None,
                    'AE2(SQ003)': None,
                    'AE2(SQ004)': None,
                    'AE2(SQ005)': None,
                    'AE2(SQ006)': None,
                    'AE2(SQ007)': None,
                    'AE2(SQ008)': None,
                    'AE2(SQ009)': None,
                    'AE2(SQ016)': None}
    for code in data_dict_ae.keys():
        data_dict_ae[code] = data_dict[code][1]
    data_dict_ae_comp = {'AE2(SQ001)': None,
                         'AE2(SQ002)': None,
                         'AE2(SQ003)': None,
                         'AE2(SQ004)': None,
                         'AE2(SQ005)': None,
                         'AE2(SQ006)': None,
                         'AE2(SQ007)': None,
                         'AE2(SQ008)': None,
                         'AE2(SQ009)': None,
                         'AE2(SQ016)': None}
    for code in data_dict_ae_comp.keys():
        data_dict_ae_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    if include == [False] * all_respondents:
        return
    else:
        make_barplot("Graduate_student_workload" + res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False] * all_respondents:
        return
    else:
        make_barplot("Graduate_student_workload" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae_comp,
                     ylabels)


def ae21(include, desc, other_include=None):
    # For students employed as a TA. Respect and workload
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE21(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE21(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE21(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE21(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE21(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE21(SQ006)': [None, None, None, None, None, None, None, None, None]}
    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("TA workload and feelings of respect")
    print("Questions AE21(SQ001)-AE21(SQ006) are scored on a scale from 0-4 representing numerical values assigned to"
          " the possible answers.")
    print(get_possible_answers('AE21(SQ001)')[0:5])
    print("\n")
    print("Top question: ", get_top_question('AE21(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae = {'AE21(SQ001)': None,
                    'AE21(SQ002)': None,
                    'AE21(SQ003)': None,
                    'AE21(SQ004)': None,
                    'AE21(SQ005)': None,
                    'AE21(SQ006)': None}
    for code in data_dict_ae.keys():
        data_dict_ae[code] = data_dict[code][1]
    data_dict_ae_comp = {'AE21(SQ001)': None,
                         'AE21(SQ002)': None,
                         'AE21(SQ003)': None,
                         'AE21(SQ004)': None,
                         'AE21(SQ005)': None,
                         'AE21(SQ006)': None}
    for code in data_dict_ae_comp.keys():
        data_dict_ae_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    if include == [False] * all_respondents:
        return
    else:
        make_barplot("TA_experiences" + res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False] * all_respondents:
        return
    else:
        make_barplot("TA_experiences" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae3(include, desc, other_include=None):
    # Questions about workload for undergraduates
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE3(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE3(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE3(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE3(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE3(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE3(SQ006)': [None, None, None, None, None, None, None, None, None]}
    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("Undergraduate student workload")
    print("Questions AE3(SQ001)-AE3(SQ006) are scored on a scale from 0-4 representing numerical values assigned to the"
          " possible answers.")
    print(get_possible_answers('AE3(SQ001)')[0:5])
    print("\n")
    print("Top question: ", get_top_question('AE3(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae = {'AE3(SQ001)': None,
                    'AE3(SQ002)': None,
                    'AE3(SQ003)': None,
                    'AE3(SQ004)': None,
                    'AE3(SQ005)': None,
                    'AE3(SQ006)': None}
    for code in data_dict_ae.keys():
        data_dict_ae[code] = data_dict[code][1]
    data_dict_ae_comp = {'AE3(SQ001)': None,
                         'AE3(SQ002)': None,
                         'AE3(SQ003)': None,
                         'AE3(SQ004)': None,
                         'AE3(SQ005)': None,
                         'AE3(SQ006)': None}
    for code in data_dict_ae_comp.keys():
        data_dict_ae_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    if include == [False] * all_respondents:
        return
    else:
        make_barplot("Undergraduate_workload" + res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False] * all_respondents:
        return
    else:
        make_barplot("Undergraduate_workload" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae4(include, desc, other_include=None):
    # Questions for students in a co-op placement
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE4(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE4(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE4(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE4(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE4(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE4(SQ006)': [None, None, None, None, None, None, None, None, None]}
    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("Co-op placement experiences")
    print("Questions AE4(SQ001)-AE4(SQ006) are scored on a scale from 0-4 representing numerical values assigned to the"
          " possible answers.")
    print(get_possible_answers('AE4(SQ001)')[0:5])
    print("\n")
    print("Top question: ", get_top_question('AE4(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae = {'AE4(SQ001)': None,
                    'AE4(SQ002)': None,
                    'AE4(SQ003)': None,
                    'AE4(SQ004)': None,
                    'AE4(SQ005)': None,
                    'AE4(SQ006)': None}
    for code in data_dict_ae.keys():
        data_dict_ae[code] = data_dict[code][1]
    data_dict_ae_comp = {'AE4(SQ001)': None,
                         'AE4(SQ002)': None,
                         'AE4(SQ003)': None,
                         'AE4(SQ004)': None,
                         'AE4(SQ005)': None,
                         'AE4(SQ006)': None}
    for code in data_dict_ae_comp.keys():
        data_dict_ae_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    if include == [False] * all_respondents:
        return
    else:
        make_barplot("Co-op_placement_experiences" + res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False] * all_respondents:
        return
    else:
        make_barplot("Co-op_placement_experiences" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae_comp,
                     ylabels)


def ae5(include, desc, other_include=None):
    # Questions for undergraduates with a thesis
    include_comp = subtract_include([True] * all_respondents, include)
    if other_include:
        include_comp = other_include
    #    Dict = {CODE        : [subquestion, scores, comp_scores, mean, moe, lconf, median, hconf, pvalue]}
    data_dict = {'AE5(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE5(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE5(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE5(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE5(SQ005)': [None, None, None, None, None, None, None, None, None]}
    for code in data_dict.keys():
        responses = get_included_responses(code, include)
        scores = get_scored_data(code, responses)
        comp_responses = get_included_responses(code, include_comp)
        comp_scores = get_scored_data(code, comp_responses)
        lconf, median, hconf = get_confidence_interval(scores)
        pval = mwu_test(scores, comp_scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = comp_scores
        data_dict[code][3] = mean(scores)
        try:
            data_dict[code][4] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][4] = None
        data_dict[code][5] = lconf
        data_dict[code][6] = median
        data_dict[code][7] = hconf
        data_dict[code][8] = pval

    print("********************************************************************")
    print("Undergraduates with a thesis")
    print("Questions AE5(SQ001)-A5(SQ005) are scored on a scale from 0-4 representing numerical values assigned to the"
          " possible answers.")
    print(get_possible_answers('AE5(SQ001)')[0:5])
    print("\n")
    print("Top question: ", get_top_question('AE5(SQ001)'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 3
        while i < 9:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i + 1
        print("\n", end="")
    print("********************************************************************")

    data_dict_ae = {'AE5(SQ001)': None,
                    'AE5(SQ002)': None,
                    'AE5(SQ003)': None,
                    'AE5(SQ004)': None,
                    'AE5(SQ005)': None}
    for code in data_dict_ae.keys():
        data_dict_ae[code] = data_dict[code][1]
    data_dict_ae_comp = {'AE5(SQ001)': None,
                         'AE5(SQ002)': None,
                         'AE5(SQ003)': None,
                         'AE5(SQ004)': None,
                         'AE5(SQ005)': None}
    for code in data_dict_ae_comp.keys():
        data_dict_ae_comp[code] = data_dict[code][2]
    ylabels = ['None of the time', 'Rarely', 'Some of the time', 'Most of the time', 'All of the time']
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "(" + str(included_respondents) + " of " + str(all_respondents) + ")"
    res_str_comp = "(" + str(included_respondents_comp) + " of " + str(all_respondents) + ")"
    if include == [False] * all_respondents:
        return
    else:
        make_barplot("Undergrad_thesis_experiences" + res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False] * all_respondents:
        return
    else:
        make_barplot("Undergrad_thesis_experiences" + res_str_comp, "(comp)" + desc, True, 0, 4, data_dict_ae_comp,
                     ylabels)


def ae7(include, desc, other_include=None):
    pass



