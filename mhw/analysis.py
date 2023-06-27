import numpy as np
import pandas as pd

from mhw.include_arrays import subtract_include
from mhw.read_results import get_included_responses
from mhw.read_statistics import get_subquestion, get_all_questions
from mhw.scoring import get_scored_data
from mhw.utils import standard_error, fpc, get_confidence_interval, mwu_test
from mhw.config import get_config


def get_stats_comparison(*args, include=None, description="", include_other=None, print_table=False):
    """
    Gets the statistics for the given questions and subquestions.
    :param args: Any number of question codes or subquestion codes.
    :param include: An include array.
    :param description: Description of inclusion criteria.
    :param include_other: Another include array for comparison.
    :param print_table: When true, prints the table to the console.
    :return: A dataframe with the statistics for the given questions and subquestions.
    """
    config = get_config()
    include_all = config.get_include_all()
    all_respondents = config.get_all_respondents()
    population = config.get_population()
    zscore = config.get_zscore()
    questions = get_all_questions()
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
        df.attrs['population_size'] = population
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
            scores = np.array(get_scored_data(code, responses))
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
