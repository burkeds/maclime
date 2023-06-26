"""
Created on May 18, 2022

@author: Devin Burke

This file holds functions for reading the limesurvey results file and extracting responses.

"""
import pandas as pd

from mhw.config import get_config
CONFIG = get_config()


# Returns list of responses for a question code
def get_all_responses(code):
    """
    Returns a list of all responses for a given question code.
    :param code: The question code
    :return: A list of responses
    """
    keys = CONFIG.get_results_file().index.tolist()
    values = CONFIG.get_results_file()[code].values.tolist()
    responses = {keys[i]: None if pd.isna(values[i]) else values[i] for i in range(len(keys))}
    return responses


def get_single_response(code, resp_id):
    """
    Returns a single response for a given question code and respondent ID.
    :param code: The question code
    :param resp_id: The respondent ID
    :return: A single response
    """
    response_id = int(resp_id)
    response = CONFIG.get_results_file().loc[response_id, code]
    if pd.isna(response):
        return None
    else:
        return CONFIG.get_results_file().loc[response_id, code]


# Returns only responses which have a corresponding True value in the include array
def get_included_responses(code, include):
    """
    Returns a list of responses for a given question code and include array.
    :param code: The question code
    :param include: The include array
    :return: A list of responses
    """
    return CONFIG.get_results_file()[code][include].to_list()


def get_results():
    """
    Returns the results dataframe.
    :return: The results dataframe
    """
    return CONFIG.get_results_file()
