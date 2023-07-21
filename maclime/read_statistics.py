"""
Created on May 18, 2022

@author: Devin Burke

This file will allow you to read from the limesurvey statistics output file.
This version of the code requires the statistics file but these data could
be obtained from the results file in future versions.
"""
import pandas as pd
from maclime.utils import char_split, merge

from maclime.config import get_config
CONFIG = get_config()
STATISTICS = CONFIG.get_statistics_file()
INCLUDE_ALL = CONFIG.get_include_all()

# data = statistics_file


def generate_codex(statistics_file):
    """
    Generates a dictionary of the codes and their row numbers in the statistics file.

    :param statistics_file: A pandas dataframe of the statistics file
    :return: A dictionary of the codes and their row numbers
    """
    code_dict = {}
    if statistics_file.empty:
        return code_dict
    else:
        for i in range(len(statistics_file)):
            ls = statistics_file.loc[i].values.tolist()
            if isinstance(ls[0], str):
                ls = ls[0].split()
                if ls[0] == "Summary":
                    code = ls[2]
                    characters = char_split(code)
                    ch = 0
                    for char in characters:
                        ch += 1
                        if char == ")":
                            break
                    code = code[0:ch]
                    code_dict[code] = i
    return code_dict


CODEX = generate_codex(STATISTICS)


def get_summary(code):
    """
    Returns the summary of the question with the given code.
    :param code: The question code
    :return: The summary
    """
    row = CODEX[code]
    ls = STATISTICS.loc[row].values.tolist()
    return ls[0]


def get_top_question(code):
    """
    Returns the top question of the question with the given code.
    :param code: The question code
    :return: The top question
    """
    row = CODEX[code]
    ls = STATISTICS.loc[row + 1].values.tolist()
    return ls[0]


def get_subquestion(code):
    """
    Returns the subquestion of the question with the given code.
    :param code: The question code
    :return: The subquestion
    """
    row = CODEX[code]
    ls = STATISTICS.loc[row].values.tolist()
    subq = ""
    while True:
        ls_check = ls[0].split()
        if ls_check[0] == "Summary":
            characters = char_split(ls[0])
            ch = 0
            for char in characters:
                ch += 1
                if char == "[":
                    subq = merge(characters[ch:-1])
                    break
        break
    return subq


def get_question_headers(code):
    """
    Returns the question headers of the question with the given code.
    :param code: The question code
    :return: The question headers
    """
    row = CODEX[code]
    ls = STATISTICS.loc[row + 2].values.tolist()
    return ls[0:3] 


def get_possible_answers(code):
    """
    Returns the possible answers of the question with the given code.
    :param code: The question code
    :return: The possible answers
    """
    subq = []
    row = CODEX[code] + 2
    while row > 0:
        row += 1
        ls = STATISTICS.loc[row].values.tolist()
        if not pd.isna(ls[2]):
            subq.append(ls[0])

        else:
            break
    for index, ans in enumerate(subq):
        characters = char_split(ans)
        ch = 0
        for char in characters:
            ch += 1
            if char == "(":
                subq[index] = merge(characters[0:ch-2])
                break   
    return subq


def get_counts(code):
    """
    Returns the frequency of each answer for a question with the given code.
    :param code: The question code
    :return: The counts
    """
    counts = []
    row = CODEX[code] + 2
    while row > 0:
        row += 1
        ls = STATISTICS.loc[row].values.tolist()
        if not pd.isna(ls[2]):
            counts.append(ls[1])
        else:
            break
    count_data = counts
    return count_data


def get_data(code):
    """
    Returns the dataframe for a question with the given code.
    :param code: The question code
    :return: The dataframe
    """
    perc = []
    row = CODEX[code] + 2
    while row > 0:
        row += 1
        ls = STATISTICS.loc[row].values.tolist()
        if not pd.isna(ls[2]):
            perc.append(ls[2])
        else:
            break
    for index, dat in enumerate(perc):
        perc[index] = round(dat*100, 1)        
    qdata = perc
    return qdata


def get_number_of_nan_in_list(ls):
    """
    Returns the number of nan values in a list.
    :param ls: A list
    :return: The number of nan values
    """
    number_of_nan = 0
    for item in ls:
        if pd.isna(item):
            number_of_nan += 1
    return number_of_nan


def get_all_codes():
    """
    Returns a list of all question codes.
    :return:
    """
    return list(CODEX.keys())
