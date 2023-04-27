"""
Created on May 18, 2022

@author: Devin Burke

This file holds functions for reading the limesurvey results file and extracting responses.

"""
from mhw.config import all_respondents, results_file

results_rows = results_file
ls0 = results_rows.loc[0].values.tolist()


# Returns array of responses for a question code
def get_all_responses(code):
    col_i = -1
    responses = {}
    for index, cell in enumerate(ls0):
        if cell == code:
            col_i = index
    row = 2 
    while row <= all_respondents:
        ls = results_rows.loc[row].values.tolist()
        responses[str(ls[0])] = ls[col_i]
        row += 1
    return responses


# Fetched a single response from a respondent for a specific question code
def get_single_response(code, resp_id):
    resp_id = str(resp_id)
    all_resp = get_all_responses(code)
    response = all_resp[resp_id]
    return response


# Returns only responses which have a corresponding True value in the include array
def get_included_responses(code, include):
    all_responses = get_all_responses(code)
    filtered_responses = {}
    for i, key in enumerate(list(all_responses.keys())):
        if include[i]:
            filtered_responses[key] = all_responses[key]
        else:
            filtered_responses[key] = None
    return filtered_responses
