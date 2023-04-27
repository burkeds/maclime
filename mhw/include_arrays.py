"""
Created on April 27, 2023

@author: Devin Burke

This file houses user defined include arrays. 
An include array is a dictionary with an entry for each respondent according to their respondent ID.
If a respondent gave the specified response for a given question code
the value at the respondent's key is True, otherwise False.
For an array to be imported it must be listed as a string in __all__
Include arrays can be combined with added together or subtracted from each other

Pass include arrays to functions called from your survey file and use them to
filter your data.
"""

from mhw.read_results import get_all_responses
from mhw.config import all_respondents

__all__ = ['include_all',
           'inc_coop',
           'inc_disa',
           'inc_emp',
           'inc_TA',
           'inc_emp_notTA',
           'inc_fem',
           'inc_mal',
           'inc_grad',
           'inc_under',
           'inc_unem',
           'inc_race',
           'inc_danger',
           'inc_grad_race',
           'inc_under_race',
           'inc_under_not_race',
           'inc_under_fem',
           'inc_under_mal',
           'inc_grad_fem',
           'inc_grad_mal',
           'get_true_count',
           'subtract_include']


# Returns an include array of True/False values for a given code and response
def get_include_array(code, response):
    responses = get_all_responses(code)
    include = dict.fromkeys(responses.keys(), False)
    for key in responses.keys():
        if responses[key] == response:
            include[key] = True
    return include


# Use logic to combine include arrays. 'OR' is default logic.
# Returns a new array
def combine_include(*args, logic='OR'):
    logics = ['OR', 'AND']
    new_include = dict.fromkeys(args[0].keys(), None)
    if logic not in logics:
        raise Exception('Combine logic must be one of ', logics)
    for include in args:
        if len(include) != len(args[0]):
            raise Exception('All arrays must be of the same length.')
    for key in new_include.keys():
        entries = [include[key] for include in args]
        if logic == 'AND':
            new_include[key] = all(entries)
        if logic == 'OR':
            new_include[key] = any(entries)
    return new_include

# All respondent arrays after the first are subtracted from the first.
# For each boolean in the first array, if any boolean of the same index in
# another array is True, the value in the first array becomes False.
# Returns a new array


def subtract_include(*args):
    new_include = args[0].copy()
    for key in new_include.keys():
        entries = [include[key] for include in args]
        if entries[0]:
            for x in entries[1:]:
                if x:
                    new_include[key] = False
    return new_include


# Returns number of True values in an include array
def get_true_count(inc):
    x = 0
    for z in inc.values():
        if z:
            x = x + 1
    return x


# Any include arrays defined here need to be added to __all__ to be imported with *
# All respondents
include_all = [True]*all_respondents

inc_phd = get_include_array('SAL1', 'I am a PhD level graduate student within the Department of Physics and Astronomy.')
inc_master = get_include_array('SAL1', 'I am a master level graduate student within the Department of Physics and '
                                       'Astronomy.')
# Graduate students
inc_grad = combine_include(inc_phd, inc_master, logic='OR')

# Undergrads
inc_under = get_include_array('SAL1', 'I am an undergraduate student.')

# Female identifying
inc_fem = get_include_array('PI3', 'Female (cis or trans)')

# Male identifying
inc_mal = get_include_array('PI3', 'Male (cis or trans)')

# Person with a disability
inc_disa = get_include_array('PI2', "Yes")

# Racialized person
inc_race = get_include_array('PI1', "Yes")

# Employed but not on co-op
inc_a = get_include_array("SAL9-0", "Yes")
inc_b = get_include_array("SAL9-1", "Yes")
inc_c = get_include_array("SAL9-2", "Yes")
inc_emp = combine_include(inc_a, inc_b, inc_c, logic='OR')

# Employed as a TA or IA
inc_TA = get_include_array('SAL9-2', "Yes")

# Unemployed and not on co-op
inc_unem = subtract_include(get_include_array('SAL9-3', "Yes"), 
                            get_include_array('SAL6', "I am in a co-op work placement this semester."))

# Currently on co-op placement
inc_coop = get_include_array('SAL6', "I am in a co-op work placement this semester.")

# Employed but not as a TA
inc_d = get_include_array("SAL9-0", "Yes")
inc_e = get_include_array("SAL9-1", "Yes")
inc_f = get_include_array('SAL6', "I am in a co-op work placement this semester.")
inc_emp_notTA = combine_include(inc_d, inc_e, inc_f, logic='OR')

# Crisis and struggling
inc_crisis = get_include_array('MH2', 'In crisis')
inc_struggling = get_include_array('MH2', 'Struggling')
inc_danger = combine_include(inc_crisis, inc_struggling, logic='OR')

# Racialized graduates and undergraduates
inc_grad_race = combine_include(inc_grad, inc_race, logic='AND')
inc_under_race = combine_include(inc_under, inc_race, logic='AND')

# Undergraduates that are not racialized
inc_under_not_race = subtract_include(inc_under, inc_under_race)

# Male and female undergraduates and graduate
inc_under_fem = combine_include(inc_under, inc_fem, logic='AND')
inc_grad_fem = combine_include(inc_grad, inc_fem, logic='AND')
inc_under_mal = combine_include(inc_under, inc_mal, logic='AND')
inc_grad_mal = combine_include(inc_grad, inc_mal, logic='AND')
