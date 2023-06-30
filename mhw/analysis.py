"""
Created on June 28, 2023
@author: Devin Burke

This module contains methods which accept callback functions to perform some sort of analysis on a set of questions.
"""

from example.mhw_spring_2023 import INCLUDE_ALL
from mhw.include_arrays import subtract_include


def analyze(include, stats_callback=None, stats_args=None, include_other=None, figure_callback=None,
            callback_args=None):
    """
        Perform some sort of statistical analysis on a set of question codes with a set of inclusion criteria defined
        by an include array. It will perform a complementary analysis based on the complement of the include array.
        This method accepts a callback function to produce a figure if desired. It will pass the statistics dataframe
        and some arguments to the callback.

        :param include: An include array of respondents.
        :param include_other: Another include array for comparison.
        :param stats_callback: A callback function which is passed the include array and some arguments to return a
                               dataframe.
        :param stats_args: A dictionary of keyword arguments to pass to the stats callback function.
        :param figure_callback: A callback function which is passed the statistics dataframe and some arguments
                                to produce a figure.
        :param callback_args: A dictionary of keyword arguments to pass to the figure callback function.
        :return: A dataframe with the statistics for social perception.
        """
    include_comp = include_other
    if not include_comp:
        include_comp = subtract_include(INCLUDE_ALL, include)
    stats = stats_callback(include=include,
                           include_other=include_comp,
                           **stats_args)

    if figure_callback:
        figure_callback(**callback_args, complement=False, frame=stats)
        figure_callback(**callback_args, complement=True, frame=stats)

    return stats
