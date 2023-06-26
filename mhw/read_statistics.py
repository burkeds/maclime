"""
Created on May 18, 2022

@author: Devin Burke

This file will allow you to read from the limesurvey statistics output file.
This version of the code requires the statistics file but these data could
be obtained from the results file in future versions.
"""
from mhw.read_results import get_included_responses
import pandas as pd
from mhw.utils import char_split, merge

from mhw.config import get_config
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


codex = generate_codex(STATISTICS)


def get_summary(code):
    """
    Returns the summary of the question with the given code.
    :param code: The question code
    :return: The summary
    """
    row = codex[code]
    ls = STATISTICS.loc[row].values.tolist()
    return ls[0]


def get_top_question(code):
    """
    Returns the top question of the question with the given code.
    :param code: The question code
    :return: The top question
    """
    row = codex[code]
    ls = STATISTICS.loc[row + 1].values.tolist()
    return ls[0]


def get_subquestion(code):
    """
    Returns the subquestion of the question with the given code.
    :param code: The question code
    :return: The subquestion
    """
    row = codex[code]
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
    row = codex[code]
    ls = STATISTICS.loc[row + 2].values.tolist()
    return ls[0:3] 


def get_possible_answers(code):
    """
    Returns the possible answers of the question with the given code.
    :param code: The question code
    :return: The possible answers
    """
    subq = []
    row = codex[code] + 2
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
    row = codex[code] + 2
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
    row = codex[code] + 2
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


def _get_number_of_nan_in_list(ls):
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


class Question:
    """
    This class will be used to store the data for each question.

    Attributes:
        code (str): The code for the question.
        summary (str): The summary of the question.
        include (list): The list of responses to include.
        description (str): The description of the question.
        question (str): The question.
        subquestion (str): The subquestion if applicable.
        question_headers (list): The headers for the question.
        possible_answers (list): The possible answers for the question.
        counts (list): The counts for each possible answer.
        stats (list): The percentages for each possible answer.
        error (str): Exceptions raised while instantiating object.
        data (DataFrame): The data for the question.

    """
    code = ""
    summary = ""
    include = []
    description = ""
    question = ""
    subquestion = ""
    question_headers = ""
    possible_answers = ""
    counts = []
    stats = []
    error = ""
    data = pd.DataFrame()

    def __init__(self, code, include=INCLUDE_ALL, description=""):
        try:
            _ = codex[code]
            self.code = code
        except KeyError as e:
            self.error = "KeyError: {}".format(e)
        try:
            self.summary = get_summary(code)
        except Exception as e:
            self.error = e
        try:
            self.include = include
        except Exception as e:
            self.error = e
        try:
            self.description = description
        except Exception as e:
            self.error = e
        try:
            self.question = get_top_question(code)
        except Exception as e:
            self.error = e
        try:
            self.subquestion = get_subquestion(code)
        except Exception as e:
            self.error = e
        try:
            self.question_headers = get_question_headers(code)
        except Exception as e:
            self.error = e
        try:
            self.possible_answers = get_possible_answers(code)
        except Exception as e:
            self.error = e
        self._populate_data()
        if code == 'TEST':
            self._init_test_question()
        self._build_dataframe()

    def _build_dataframe(self):
        """
        Builds the dataframe for the question.
        :return:
        """
        df = pd.DataFrame(columns=self.question_headers)
        df['Answer'] = self.possible_answers
        df['Count'] = self.counts
        df['Percentage'] = self.stats
        self.data = df

    def _populate_data(self):
        """
        Populates the counts and stats attributes.
        :return:
        """
        if self.include == INCLUDE_ALL:
            try:
                self.counts = get_counts(self.code)
            except Exception as e:
                self.error = e
            try:
                self.stats = get_data(self.code)
            except Exception as e:
                self.error = e
        else:
            try:
                included_responses = get_included_responses(self.code, self.include)
                counts = {}
                percentages = {}
                for answer in self.possible_answers:
                    if answer == "Not completed or Not displayed":
                        counts[answer] = None
                        percentages[answer] = None
                        continue
                    counts[answer] = included_responses.count(answer)
                    percentages[answer] = round(counts[answer]/len(included_responses) * 100, 1)
                number_of_nan = _get_number_of_nan_in_list(included_responses)
                counts['No answer'] = number_of_nan
                percentages['No answer'] = round(number_of_nan/len(included_responses) * 100, 1)
                self.counts = counts.values()
                self.stats = percentages.values()
            except Exception as e:
                self.error = e

    def _init_test_question(self):
        """
        Initializes the test question.
        :return:
        """
        self.code = 'TEST'
        self.question_headers = ['Answers', 'Counts', 'Stats']
        self.possible_answers = ['Strongly disagree',
                                 'Disagree',
                                 'Somewhat disagree',
                                 'Neither agree nor disagree',
                                 'Somewhat agree',
                                 'Agree',
                                 'Strongly agree',
                                 'Not applicable',
                                 'No answer']
        self.summary = "Summary of test question."
        self.question = 'How much do you agree with the test question?'
        self.counts = [0, 5, 6, 3, 4, 4, 6, 2, 1]
        sum_counts = sum(self.counts)
        self.stats = [round(i/sum_counts, 1) for i in self.counts]


def get_all_questions():
    """
    Returns a dictionary of all questions.
    :return:
    """
    all_stats = {}
    all_codes = list(codex.keys())
    for code in all_codes:
        all_stats[code] = Question(code)
    return all_stats
