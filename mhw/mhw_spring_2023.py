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
from mhw.include_arrays import inc_under, inc_grad
from mhw.scoring import get_value_dict
from mhw.read_statistics import get_possible_answers, get_all_statistics, Question

results = get_results()
questions = get_all_statistics()


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

        first_code = df.index[0]
        df.attrs['question'] = questions[first_code].question
        df.attrs['possible_answers'] = questions[first_code].possible_answers
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
            print("Top question text: {}".format(df.attrs['question']))
            print("Possible answers: {}".format(df.attrs['possible_answers']))
            print(df.round(2).to_csv(sep='\t'))
            print("********************************************************************")
    if len(frames) == 1:
        return frames[0]
    else:
        return frames


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


def ae0(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
    codes = ['AE0(SQ001)',
             'AE0(SQ002)',
             'AE0(SQ003)',
             'AE0(SQ004)',
             'AE0(SQ005)',
             'AE0(SQ006)']
    stats_df = _get_stats_comparison(codes,
                                     include=include,
                                     description=description,
                                     include_other=include_comp,
                                     print_table=print_table)
    plot_impact_statistics(stats_df, title="Social perception")
    plot_impact_statistics(stats_df, title="Social perception", complement=True)
    return stats_df


def ae1(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
    codes = ['AE1(SQ001)',
             'AE1(SQ002)',
             'AE1(SQ003)',
             'AE1(SQ004)',
             'AE1(SQ005)']
    ae0_stats = _get_stats_comparison(codes,
                                      include=include,
                                      description=description,
                                      include_other=include_comp,
                                      print_table=print_table)
    plot_impact_statistics(ae0_stats, title="Department perception")
    plot_impact_statistics(ae0_stats, title="Department perception", complement=True)
    return ae0_stats


def ae2(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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
    plot_impact_statistics(stats, title="Graduate student workload")
    plot_impact_statistics(stats, title="Graduate student workload", complement=True)
    return stats


def ae21(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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
    plot_impact_statistics(stats, title="TA workload")
    plot_impact_statistics(stats, title="TA workload", complement=True)
    return stats


def ae3(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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
    plot_impact_statistics(stats, title="Undergraduate workload")
    plot_impact_statistics(stats, title="Undergraduate workload", complement=True)
    return stats


def ae4(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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
    plot_impact_statistics(stats, title="Co-op workload")
    plot_impact_statistics(stats, title="Co-op workload", complement=True)
    return stats


def ae5(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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
    plot_impact_statistics(stats, title="Undergraduate thesis experience")
    plot_impact_statistics(stats, title="Undergraduate thesis experience", complement=True)
    return stats


def ae6(include, description="", include_other=None, print_table=False):
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(include_all, include)
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


class QuestionInclude(Question):
    def __init__(self, code, include=None, description=""):
        super().__init__(code)
        if not include:
            raise Exception("You must specify inclusion criteria with an include array of respondent IDs.")
        else:
            self.include = include
        self.description = description
        responses = get_included_responses(code, include)
        for ans in self.possible_answers:
            count = responses.count(ans)
            self.counts.append(count)
            self.stats.append(count / len(responses))

if __name__ == "__main__":
    ae7 = QuestionInclude('AE7', include=inc_under, description="Undergraduates")
    print_table = True
    if print_table:
        print("********************************************************************")
        print("Question code: {}".format(ae7.code))
        print("Top question text: {}".format(ae7.question))
        print("Inclusion criteria: {}".format(ae7.description))
        print("Respondents fitting inclusion criteria: {}".format(len(ae7.include)))
        print("Sample size: {}".format(all_respondents))
        print('\t'.join(ae7.question_headers))
        for i, ans in enumerate(ae7.possible_answers):
            print(ans, "\t", ae7.counts[i], "\t", ae7.stats[i])
        print("********************************************************************")
