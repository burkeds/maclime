"""
Created on May 18, 2022

@author: Devin Burke

This file holds functions for reading the limesurvey results file and extracting responses.

"""
from mhw.config import results_file as results
import pandas as pd


# Returns list of responses for a question code
def get_all_responses(code):
    """
    Returns a list of all responses for a given question code.
    :param code:
    :return:
    """
    keys = results.index.tolist()
    values = results[code].values.tolist()
    responses = {keys[i]: None if pd.isna(values[i]) else values[i] for i in range(len(keys))}
    return responses


def get_single_response(code, resp_id):
    """
    Returns a single response for a given question code and respondent ID.
    :param code:
    :param resp_id:
    :return:
    """
    response_id = int(resp_id)
    response = results.loc[response_id, code]
    if pd.isna(response):
        return None
    else:
        return results.loc[response_id, code]


# Returns only responses which have a corresponding True value in the include array
def get_included_responses(code, include):
    """
    Returns a list of responses for a given question code and include array.
    :param code:
    :param include:
    :return:
    """
    return results[code][include].to_list()


def get_results():
    """
    Returns the results dataframe.
    :return:
    """
    return results
