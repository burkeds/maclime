"""
Created on May 18, 2022

@author: Devin Burke

This file is where you should write survey specific functions to
extract and manipulate data however you want.
"""
import pandas as pd
from textwrap import wrap
from mhw.config import zscore, pop, all_respondents
from mhw.read_results import get_single_response, get_included_responses
from mhw.scoring import get_value_dict, get_scored_data
from mhw.utils import standard_error, fpc, get_confidence_interval, mean, mwu_test, add, get_include_valid_entries
from mhw.read_statistics import get_subquestion, get_possible_answers, get_top_question
from mhw.figures import make_barplot, make_boxplot, make_histo
from mhw.include_arrays import subtract_include


# Returns asset score of a respondent
def get_mental_health_asset_score(resp_id):
    asset_codes = ['MH0(SQ001)', 
                   'MH0(SQ002)', 
                   'MH0(SQ003)', 
                   'MH0(SQ004)', 
                   'MH0(SQ005)']
    score = 0
    for code in asset_codes:
        value = get_value_dict(code)
        resp = get_single_response(code, resp_id)
        if pd.isna(resp):
            return None
        else:
            score += value[resp]
    score = score / 20
    return score


# Returns deficit score of respondent
def get_mental_health_deficit_score(resp_id):      
    deficit_codes = ['MH1(SQ001)', 
                     'MH1(SQ002)', 
                     'MH1(SQ003)', 
                     'MH1(SQ004)', 
                     'MH1(SQ005)', 
                     'MH1(SQ006)']
    score = 0
    for code in deficit_codes:
        value = get_value_dict(code)
        resp = get_single_response(code, resp_id)
        if pd.isna(resp):
            return None
        else:
            score += value[resp]
    score = score / 24
    return score * -1


# Returns mean academic impact score from all sources
# for a single respondent
def get_academic_impact(resp_id):
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
    score = []
    for code in impact_codes:
        value = get_value_dict(code)
        resp = get_single_response(code, resp_id)
        if pd.isna(resp) or resp == 'Not applicable':
            continue
        else:
            score.append(value[resp])
    if not score:
        return None
    else:
        score_mean = mean(score)
        return score_mean

    
# Investigate effects of specific academic experiences
def impact_of_single_academics_on_mental_health(include, desc, other_include=None):    
    # Build complementary array for pvalue calculations
    include_comp = subtract_include([True]*all_respondents, include)
    if other_include:
        include_comp = other_include    
    # Build dict for set of question codes
    #    Dict = {CODE        : [subquestion, scores, mean, moe, lconf, median, hconf, pvalue, comp_scores]}
    data_dict = {'AE6(SQ001)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ002)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ003)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ004)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ005)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ006)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ007)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ008)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ009)': [None, None, None, None, None, None, None, None, None],
                 'AE6(SQ010)': [None, None, None, None, None, None, None, None, None]}
    # Fill data_dict
    for code in data_dict.keys():
        resps = get_included_responses(code, include)
        comp_resps = get_included_responses(code, include_comp)
        scores = get_scored_data(code, resps)
        comp_scores = get_scored_data(code, comp_resps)
        lconf, median, hconf = get_confidence_interval(scores)
        data_dict[code][0] = get_subquestion(code)
        data_dict[code][1] = scores
        data_dict[code][2] = mean(scores)
        try:
            data_dict[code][3] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            data_dict[code][3] = None
        data_dict[code][4] = lconf
        data_dict[code][5] = median
        data_dict[code][6] = hconf
        data_dict[code][7] = mwu_test(scores, comp_scores)      
        data_dict[code][8] = comp_scores        
    # Print data
    print("********************************************************************")
    print("Calculate the impact score of specific academic experiences on mental health")
    print("with respect to the mental health continuum.")
    print("Impact score scaled from -2 (strongly negative) to +2 (strongly positive).")    
    print("Top question:\t", get_top_question('AE6(SQ001)'))
    print("Question code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tP-value")
    for code in data_dict.keys():
        print(code, end="\t")
        print(data_dict[code][0], end="\t")
        i = 2
        while i < 8:
            try:
                print(round(data_dict[code][i], 2), end="\t")
            except TypeError:
                print(None, end="\t")
            finally:
                i = i+1
        print("\n", end="")  
    print("********************************************************************")
    # Call make_barplot to build figures
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
    ylabels = ["strongly negative", "negative",  "neutral",  "positive",  "strongly positive"]
    ylabels = ['\n'.join(wrap(l, 10)) for l in ylabels]
    plot_dict = {}
    comp_plot_dict = {}
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"
    for i, code in enumerate(data_dict.keys()):
        plot_dict[xlabels[i]] = data_dict[code][1]
        comp_plot_dict[xlabels[i]] = data_dict[code][-1]
    make_barplot("Impact_on_mental_health_continuum", desc+res_str, True, -2, 2, plot_dict, ylabels, True)
    make_barplot("Impact_on_mental_health_continuum", "(comp)"+desc+res_str_comp, True, -2, 2, comp_plot_dict, ylabels,
                 True)
    make_barplot("Impact_on_mental_health_continuum", desc, True, -2, 2, plot_dict, ylabels, True, xlabels=['Q1', 'Q2',
                                                                                                            'Q3', 'Q4',
                                                                                                            'Q5', 'Q6',
                                                                                                            'Q7', 'Q8',
                                                                                                            'Q9',
                                                                                                            'Q10'])
    make_barplot("Impact_on_mental_health_continuum", "not_" + desc, True, -2, 2, comp_plot_dict, ylabels, True,
                 xlabels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10'])


def mean_impact_of_all_academics_on_health(include, desc, other_include=None):
    include_comp = subtract_include([True]*len(include), include)
    if other_include:
        include_comp = other_include
    academic_impacts = [get_academic_impact(i) if var else None for i, var in enumerate(include)]
    academic_impacts = [i for i in academic_impacts if not pd.isna(i)]
    comp_academic_impacts = [get_academic_impact(i) if var else None for i, var in enumerate(include_comp)]
    comp_academic_impacts = [i for i in comp_academic_impacts if not pd.isna(i)]
    lconf, median, hconf = get_confidence_interval(academic_impacts)
    pval = mwu_test(academic_impacts, comp_academic_impacts)
    try:
        se = standard_error(academic_impacts) * zscore * fpc(pop, len(academic_impacts))
    except TypeError:
        se = None
    print_list = [mean(academic_impacts),
                  se,
                  lconf,
                  median,
                  hconf,
                  pval]
    print("********************************************************************")
    print("Calculate the mean impact of all academics on mental health")
    print("with respect to the mental health continuum.")    
    print("Impact score scaled from -2 (strongly negative) to +2 (strongly positive)")
    print("mean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    if not academic_impacts:
        print("No valid responses.")
        return None
    for num in print_list:
        try:
            print(round(num, 2), end="\t")
        except TypeError:
            print(None, end="\t")
    print("\n")
    print("********************************************************************")
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    make_boxplot("Academic_impact_score_on_mental_health_continuum"+res_str, desc, True, -2, +2, ["impact score"],
                 [academic_impacts])
    make_boxplot("Academic_impact_score_on_mental_health_continuum"+res_str_comp, "(comp)"+desc, True, -2, +2,
                 ["impact score"], [comp_academic_impacts])


def ae0_and_ae1(include, desc, other_include=None):
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    make_barplot("Social_perception"+res_str, desc, True, 0, 4, data_dict_ae0, ylabels)
    make_barplot("Social_perception"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae0_comp, ylabels)
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
    make_barplot("Department_perception"+res_str, desc, True, -3, 3, data_dict_ae1, ylabels)
    make_barplot("Department_perception"+res_str_comp, "(comp)"+desc, True, -3, 3, data_dict_ae1_comp, ylabels)
    make_barplot("Department_perception", desc, True, -3, 3, data_dict_ae1, ylabels, xlabels=['Q1', 'Q2', 'Q3', 'Q4',
                                                                                              'Q5'])


def ae2(include, desc, other_include=None):
    # Questions about workload for graduate students
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    if include == [False]*all_respondents:
        return
    else:
        make_barplot("Graduate_student_workload"+res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False]*all_respondents:
        return
    else:
        make_barplot("Graduate_student_workload"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae21(include, desc, other_include=None):
    # For students employed as a TA. Respect and workload
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    if include == [False]*all_respondents:
        return    
    else:
        make_barplot("TA_experiences"+res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False]*all_respondents:
        return
    else:
        make_barplot("TA_experiences"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae3(include, desc, other_include=None):
    # Questions about workload for undergraduates
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    if include == [False]*all_respondents:
        return    
    else:
        make_barplot("Undergraduate_workload"+res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False]*all_respondents:
        return
    else:
        make_barplot("Undergraduate_workload"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae4(include, desc, other_include=None):
    # Questions for students in a co-op placement
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    if include == [False]*all_respondents:
        return    
    else:
        make_barplot("Co-op_placement_experiences"+res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False]*all_respondents:
        return
    else:
        make_barplot("Co-op_placement_experiences"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae_comp, ylabels)


def ae5(include, desc, other_include=None):
    # Questions for undergraduates with a thesis
    include_comp = subtract_include([True]*all_respondents, include)
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
                i = i+1
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
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    if include == [False]*all_respondents:
        return    
    else:
        make_barplot("Undergrad_thesis_experiences"+res_str, desc, True, 0, 4, data_dict_ae, ylabels)
    if include_comp == [False]*all_respondents:
        return
    else:
        make_barplot("Undergrad_thesis_experiences"+res_str_comp, "(comp)"+desc, True, 0, 4, data_dict_ae_comp, ylabels)


def mental_health_continuum_stats(include, desc, other_include=None):
    code = 'MH2' 
    include_comp = subtract_include([True]*len(include), include)
    if other_include:
        include_comp = other_include   
    # Collect statistics from mental health continuum responses
    responses = get_included_responses(code, include)
    scores = get_scored_data(code, responses)
    comp_responses = get_included_responses(code, include_comp)
    comp_scores = get_scored_data(code, comp_responses)
    lconf, median, hconf = get_confidence_interval(scores)
    pval = mwu_test(scores, comp_scores)
    try:
        se = standard_error(scores) * zscore * fpc(pop, len(scores))
    except TypeError:
        se = None
    print_list = [mean(scores),
                  se,
                  lconf,
                  median,
                  hconf,
                  pval]
    print("********************************************************************")
    print("Self-perceived position on mental health continuum.")
    print("Scores are scaled from -2 (in crisis) to +2 (excelling)")
    print("Top question: ", get_top_question('MH2'))
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    print('MH2', end="\t")
    print("None", end="\t")
    if not responses:
        print("No valid responses.")
        return None
    for num in print_list:
        try:
            print(round(num, 2), end="\t")
        except TypeError:
            print(None, end="\t")
    print("\n")
    print("********************************************************************")
    # Build two histograms
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"    
    make_histo(scores, "Mental_health_continuum"+res_str, desc)
    make_histo(comp_scores, "Mental_health_continuum"+res_str_comp, "(comp)"+desc)
    

def mental_health_scores(include, desc, other_include=None):
    include_comp = subtract_include([True]*all_respondents, include)
    if other_include:
        include_comp = other_include
    # dict      = {key       :  scores, comp_scores, mean,  moe, lconf, median, hconf, p-value
    scores_dict = {'assets'  : [None, None, None, None,  None,   None,  None, None],
                   'deficits': [None, None, None, None,  None,   None,  None, None],
                   'total'   : [None, None, None, None,  None,   None,  None, None]}    
    # Populate scores
    # Calculate mental health score statistics from MH0 and MH1
    asset_scores = [get_mental_health_asset_score(i) if var else None for i, var in enumerate(include)]
    deficit_scores = [get_mental_health_deficit_score(i) if var else None for i, var in enumerate(include)]
    mental_health_scores = [add(asset_scores[i], deficit_scores[i]) if var else None for i, var in enumerate(include)]
    asset_scores = [i for i in asset_scores if not pd.isna(i)]
    deficit_scores = [i for i in deficit_scores if not pd.isna(i)]
    mental_health_scores = [i for i in mental_health_scores if not pd.isna(i)]
    # Store scores in dictionary
    scores_dict['assets'][0] = asset_scores
    scores_dict['deficits'][0] = deficit_scores
    scores_dict['total'][0] = mental_health_scores
        
    # Get data for complementary scores
    comp_asset_scores = [get_mental_health_asset_score(i) if var else None for i, var in enumerate(include_comp)]
    comp_deficit_scores = [get_mental_health_deficit_score(i) if var else None for i, var in enumerate(include_comp)]
    comp_mental_health_scores = [add(comp_asset_scores[i], comp_deficit_scores[i]) if var else None for i, var in
                                 enumerate(include_comp)]
    # Filter None type values from arrays
    comp_asset_scores = [i for i in comp_asset_scores if not pd.isna(i)]
    comp_deficit_scores = [i for i in comp_deficit_scores if not pd.isna(i)]
    comp_mental_health_scores = [i for i in comp_mental_health_scores if not pd.isna(i)]
    # Store complementary scores in dictionary
    scores_dict['assets'][1] = comp_asset_scores
    scores_dict['deficits'][1] = comp_deficit_scores
    scores_dict['total'][1] = comp_mental_health_scores
    
    # Populate statistical values
    for key in scores_dict.keys():
        scores = scores_dict[key][0]
        comp_scores = scores_dict[key][1]
        scores_dict[key][2] = mean(scores)
        try:
            scores_dict[key][3] = standard_error(scores) * zscore * fpc(pop, len(scores))
        except TypeError:
            scores_dict[key][3] = None
        lconf, median, hconf = get_confidence_interval(scores)
        scores_dict[key][4] = lconf
        scores_dict[key][5] = median
        scores_dict[key][6] = hconf
        pval = mwu_test(scores, comp_scores)
        scores_dict[key][7] = pval

    print("********************************************************************")
    print("Mental health assets.")
    print("Scores are scaled from 0 (never benefits from assets) to +1 (always benefitting from assets)")
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    print('MH0', end="\t")
    print('assets', end="\t")
    i = 2
    while i < 8:
        try:
            print(round(scores_dict['assets'][i], 2), end="\t")
        except TypeError:
            print(None, end="\t")
        finally:
            i = i+1
    print("\n")
    print("Mental health deficits.")
    print("Scores are scaled from 0 (never experiences deficits) to -1 (always experiences deficits)")
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    print('MH0', end="\t")
    print('deficits', end="\t")
    i = 2
    while i < 8:
        try:
            print(round(scores_dict['deficits'][i], 2), end="\t")
        except TypeError:
            print(None, end="\t")
        finally:
            i = i+1
    print("\n")    
    print("Total mental health score.")
    print("Scores are scaled from -1 to +1 as a measure of mental health equity")
    print("code\tsubquestion\tmean\tmargin_of_error\tlconf\tmedian\thconf\tp-value")
    print('MH0', end="\t")
    print('total', end="\t")
    i = 2
    while i < 8:
        try:
            print(round(scores_dict['total'][i], 2), end="\t")
        except TypeError:
            print(None, end="\t")
        finally:
            i = i+1
    print("\n")
    print("********************************************************************")
    included_respondents = get_include_valid_entries(include)
    included_respondents_comp = get_include_valid_entries(include_comp)
    res_str = "("+str(included_respondents)+" of "+str(all_respondents)+")"
    res_str_comp = "("+str(included_respondents_comp)+" of "+str(all_respondents)+")"
    make_boxplot("Mental_health_scores"+res_str, desc, True, -1, +1, 
                 ["assets", "deficits", "total"], 
                 [scores_dict['assets'][0], scores_dict['deficits'][0], scores_dict['total'][0]])
    make_boxplot("Mental_health_scores"+res_str_comp, "(comp)"+desc, True, -1, +1, 
                 ["assets", "deficits", "total"], 
                 [scores_dict['assets'][1], scores_dict['deficits'][1], scores_dict['total'][1]])


# Perform MannWhitneyU test between any two include arrays for a specific question code
def mwu_test_arbitrary(inc1, inc2, code):
    responses1 = get_included_responses(code, inc1)
    responses2 = get_included_responses(code, inc2,)
    values1 = get_scored_data(code, responses1)
    values2 = get_scored_data(code, responses2)
    pval = mwu_test(values1, values2)
    return pval


"""
#This is a copy of get_value_dict. This dict should 
#be present and uncommented in mhw.scoring so the
#get_scored_data function can find it.
#Store dictionaries that map responses to arbitrary 
#numerical values valid for a list of questions.
def get_value_dict(code):
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
"""