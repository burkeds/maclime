"""
Created on May 18, 2022

@author: Devin Burke

This file holds functions for reading the limesurvey results file and extracting responses.

"""
from mhw.config import results_file
import pandas as pd


# Returns list of responses for a question code
def get_all_responses(code):
    keys = results_file.index.tolist()
    values = results_file[code].values.tolist()
    responses = {keys[i]: None if pd.isna(values[i]) else values[i] for i in range(len(keys))}
    return responses


def get_single_response(code, resp_id):
    response_id = int(resp_id)
    response = results_file.loc[response_id, code]
    if pd.isna(response):
        return None
    else:
        return results_file.loc[response_id, code]


# Returns only responses which have a corresponding True value in the include array
def get_included_responses(code, include):
    all_responses = get_all_responses(code)
    filtered_responses = {}
    for i, key in enumerate(list(all_responses.keys())):
        if include[key]:
            if pd.isna(all_responses[key]):
                filtered_responses[key] = None
            else:
                filtered_responses[key] = all_responses[key]
        else:
            filtered_responses[key] = None
    return filtered_responses
