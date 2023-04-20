"""
Created on May 18, 2022

@author: Devin Burke

This file holds functions for reading the limesurvey results file and extracting responses.

"""
from mhw.config import max_responses, results_file

results_rows = results_file
ls0 = results_rows.loc[0].values.tolist()


# Returns array of responses for a question code
def get_all_responses(code):
    col_i = -1
    resps = []
    for index, cell in enumerate(ls0):
        if cell == code:
            col_i = index
    row = 2 
    while row <= max_responses:
        ls = results_rows.loc[row].values.tolist()    
        resps.append(ls[col_i])
        row += 1
    return resps


# Fetched a single response from a respondent for a specific question code
def get_single_response(code, resp_id):
    all_resp = get_all_responses(code)
    response = all_resp[resp_id]
    return response


# Returns only responses which have a corresponding True value in the include array
def get_included_responses(code, include):
    all_resps = get_all_responses(code)
    filtered_resps = [var if include[i] else None for i, var in enumerate(all_resps)]
    return filtered_resps
