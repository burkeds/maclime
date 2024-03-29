"""
Created on June 27, 2023
@author: Devin Burke

This module contains classes and methods for working with the questions and sections of a survey.
"""

from maclime.read_results import get_included_responses
from maclime.read_statistics import *
from maclime.config import get_config
from maclime.scoring import get_scored_data


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
        responses (list): The responses for the question.
        value_dict (dict): The value dictionary for the question.
        scores (list): The scores for the question.
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
    responses = []
    value_dict = {}
    scores = []
    question_headers = []
    possible_answers = []
    counts = []
    stats = []
    error = ""
    data = pd.DataFrame()

    def __init__(self, code=None, include=None, description=""):
        config = get_config()
        if not code:
            raise Exception("No code provided.")
        try:
            _ = CODEX[code]
            self.code = code
        except KeyError as e:
            self.error = "KeyError: {}".format(e)
        try:
            self.summary = get_summary(code)
        except Exception as e:
            self.error = e
        try:
            if not include:
                self.include = config.get_include_all()
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
            self.responses = get_included_responses(self.include, self.code)
        except Exception as e:
            self.error = e
        try:
            self.value_dict = config.get_value_dict(self.code)
        except Exception as e:
            self.error = e
        try:
            if self.value_dict:
                self.scores = get_scored_data(self.responses, self.code, self.value_dict)
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
        config = get_config()
        if self.include == config.get_include_all():
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
                number_of_nan = get_number_of_nan_in_list(included_responses)
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


def get_questions(include=None, codes=None):
    """
    Returns a dictionary of questions from a list of codes and inclusion criteria. If codes is 'ALL', then all questions
    are returned.
    :param include: The inclusion criteria for the questions.
    :param codes: The codes for the questions.
    :return:
    """
    if not codes:
        raise Exception("No codes provided. Set codes to 'ALL' to get all questions.")
    config = get_config()
    all_questions = {}

    if not include:
        include = config.get_include_all()
    if codes == 'ALL':
        codes = get_all_codes()
    for code in codes:
        all_questions[code] = Question(code, include=include)
    return all_questions


class QuestionSection:
    """
    This class will be used to store the data for each question section.

    Attributes:
        top_code (str): The top code for the section.
        title (str): The title of the section.
        subtitle (str): The subtitle of the section.
        codes (list): The codes for the questions in the section.
        questions (dict): The questions in the section.

    Methods:
        get_questions: Gets the questions for the section.
    """
    top_code = None
    title = None
    subtitle = None
    codes = None
    include = []
    description = ""
    questions = None

    def __init__(self, top_code=None, title=None, subtitle=None, codes=None, include=None, description=""):
        self.top_code = top_code
        self.title = title
        self.subtitle = subtitle
        self.codes = codes
        self.include = include
        self.description = description

        if self.codes:
            self.questions = get_questions(include=self.include, codes=self.codes)
