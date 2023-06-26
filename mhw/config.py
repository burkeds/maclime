"""
Created on May 18, 2022

@author: Devin Burke
This file contains configuration variables used by many different functions.
These variables will change for any given survey.
"""

from matplotlib import rc
import pandas as pd

CONFIG = None


class Configuration:
    """
    This class contains configuration variables used by many different functions.
    These variables will change for any given survey. Set and retrieve configuration variable using the get/set methods.

    Attributes:
        _RESULTS_FILE: The results file
        _STATISTICS_FILE: The statistics file
        _ALL_RESPONDENTS: The number of respondents
        _ZSCORE: The z-score used to calculate confidence intervals
        _POPULATION: The estimated population size
        _INCLUDE_ALL: The include array containing all respondents
        _FONT: The font used by matplotlib in figures

    Methods:
        get_results_file: Returns the results file
        set_results_file: Sets the results file by specifying the path to the file
        get_include_all: Returns the include array containing all respondents
        get_statistics_file: Returns the statistics file
        set_statistics_file: Sets the statistics file by specifying the path to the file
        get_all_respondents: Returns the total number of respondents
        set_all_respondents: Sets the total number of respondents
        get_zscore: Returns the z-score
        set_zscore: Sets the z-score
        get_population: Returns the population size
        set_population: Sets the population size
        get_font: Returns the font used by matplotlib in figures
        set_font: Sets the font used by matplotlib in figures

    """
    _RESULTS_FILE = None
    _STATISTICS_FILE = None
    _ALL_RESPONDENTS = None
    _ZSCORE = 1.96
    _POPULATION = None
    _INCLUDE_ALL = None
    # Font used by matplotlib in figures
    _FONT = {'family': 'DejaVu Sans',
             'weight': 'normal',
             'size': 10}
    rc('font', **_FONT)

    def __new__(cls):
        global CONFIG
        if CONFIG is None:
            print("Creating new configuration object.")
            CONFIG = super(Configuration, cls).__new__(cls)
        else:
            raise Exception("Configuration object already exists. Access the object with mhw.config.get_config().")
        return CONFIG

    def __init__(self):
        pass

    def get_results_file(self):
        return self._RESULTS_FILE

    def set_results_file(self, **args):
        try:
            self._RESULTS_FILE = pd.read_excel(**args)
            self._ALL_RESPONDENTS = len(self._RESULTS_FILE.index)
            self._INCLUDE_ALL = list(self._RESULTS_FILE.index)
        except FileNotFoundError as _:
            self._RESULTS_FILE = pd.DataFrame()

    def get_include_all(self):
        return self._INCLUDE_ALL

    def get_statistics_file(self):
        return self._STATISTICS_FILE

    def set_statistics_file(self, **args):
        try:
            self._STATISTICS_FILE = pd.read_excel(**args)
        except FileNotFoundError as _:
            self._STATISTICS_FILE = pd.DataFrame()

    def get_all_respondents(self):
        return self._ALL_RESPONDENTS

    def set_all_respondents(self, respondents):
        self._ALL_RESPONDENTS = respondents

    def get_zscore(self):
        return self._ZSCORE

    def set_zscore(self, zscore):
        self._ZSCORE = zscore

    def get_population(self):
        return self._POPULATION

    def set_population(self, population):
        self._POPULATION = population

    def get_font(self):
        return self._FONT

    def set_font(self, **args):
        self._FONT = args
        rc('font', **args)


def create_config():
    global CONFIG
    CONFIG = Configuration()
    return CONFIG


def get_config():
    return CONFIG
