"""
Created on May 18, 2022

@author: Devin Burke

This file will allow you to read from the limesurvey statistics output file.
This version of the code requires the statistics file but these data could
be obtained from the results file in future versions.
"""
from mhw.config import last_row, statistics_file
import pandas as pd
from mhw.utils import char_split, merge


data = statistics_file


def generate_codex(data):
    code_dict = {}
    index = -1
    while index <= last_row:
        index += 1
        ls = data.loc[index].values.tolist()
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
                code_dict[code] = index
    return code_dict


codex = generate_codex(data)


def get_summary(code):
    row = codex[code]
    ls = data.loc[row].values.tolist()
    return ls[0]


def get_top_question(code):
    row = codex[code]
    ls = data.loc[row+1].values.tolist()
    return ls[0]


def get_subquestion(code):
    row = codex[code]
    ls = data.loc[row].values.tolist()
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
    row = codex[code]
    ls = data.loc[row+2].values.tolist()
    return ls[0:3] 


def get_possible_answers(code):
    subq = []
    row = codex[code] + 2
    while row > 0:
        row += 1
        ls = data.loc[row].values.tolist()
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
    counts = []
    row = codex[code] + 2
    while row > 0:
        row += 1
        ls = data.loc[row].values.tolist()
        if not pd.isna(ls[2]):
            counts.append(ls[1])
        else:
            break
    count_data = counts
    return count_data


def get_data(code):
    perc = []
    row = codex[code] + 2
    while row > 0:
        row += 1
        ls = data.loc[row].values.tolist()
        if not pd.isna(ls[2]):
            perc.append(ls[2])
        else:
            break
    for index, dat in enumerate(perc):
        perc[index] = round(dat*100, 1)        
    qdata = perc
    return qdata
