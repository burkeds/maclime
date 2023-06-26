"""
Created on April 27, 2023

@author: Devin Burke

This file houses user defined include arrays. 
An include array is a list with an entry for each respondent according to their respondent ID.
If a respondent gave the specified response for a given question code.
Include arrays can be combined with added together or subtracted from each other.

Pass include arrays to functions called from your main survey file and use them to
filter your data.
"""

from collections import Counter
from mhw.read_results import get_results


# Returns a list of index values (respondent IDs) that have the response to the code.
def get_include_array(code, response):
    """
    Returns a list of respondent IDs that have the specified response to the specified question code.
    :param code: The question code
    :param response: The response
    :return: A list of respondent IDs
    """
    RESULTS = get_results()
    f_results = RESULTS[RESULTS[code] == response]
    return f_results.index.tolist()


# Can combine lists using AND or OR logic.
def combine_include(*args, logic='OR'):
    """
    Combines include arrays using AND or OR logic.
    :param args: The include arrays to be combined
    :param logic: The logic to be used. AND or OR
    :return: A list of respondent IDs
    """
    x = args[0].copy()
    for i, inc in enumerate(args):
        if i == 0:
            continue
        x = x + inc
    if logic == 'OR':
        return list(dict.fromkeys(x))
    if logic == 'AND':
        return [item for item, count in Counter(x).items() if count > 1]

# All respondent arrays after the first are subtracted from the first.
# For each boolean in the first array, if any boolean of the same index in
# another array is True, the value in the first array becomes False.
# Returns a new array


def subtract_include(*args):
    """
    Subtracts include arrays from each other.
    :param args: The include arrays to be subtracted
    :return: A list of respondent IDs
    """
    new_include = args[0].copy()
    for i, inc in enumerate(args):
        if i == 0:
            continue
        new_include = [x for x in new_include if x not in inc]
    return new_include
