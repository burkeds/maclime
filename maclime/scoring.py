"""
Created on May 18, 2022

@author: Devin Burke
"""
from maclime.config import get_config


# An array of responses passed returns an array of scored values using value_dict
def get_scored_data(responses, code=None, value_dict=None):
    """
    Returns an array of scored values for a given question code and array of responses.
    :param responses: An array of responses
    :param code: The question code
    :param value_dict: The value dictionary for the question
    :return: An array of scored values
    """
    config = get_config()
    if value_dict is None:
        if code is None:
            raise ValueError("Either code or value_dict must be passed.")
        value_dict = config.get_value_dict(code)
    scores = []
    for response in responses:
        if response in value_dict.keys():
            scores.append(value_dict[response])
    return scores
