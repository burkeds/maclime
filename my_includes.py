"""
Created on June 27, 2023

@author: Devin Burke

Use this file to define inclusion arrays for your analysis.
Methods found within mhw.include_arrays can be used to create include arrays.
Each include array is a list of respondent IDs that match the inclusion criteria.
Inclusion criteria can be defined by a single question or a combination of questions.
"""

from mhw.include_arrays import *

# Define inclusion arrays
# Any include arrays defined here need to be added to __all__ to be imported with *
# All respondents
include_all = get_include_array('C0', 'I understand and agree to participate in the study.')

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
inc_a = get_include_array("SAL9(SQ001)", "Yes")
inc_b = get_include_array("SAL9(SQ002)", "Yes")
inc_c = get_include_array("SAL9(SQ003)", "Yes")
inc_emp = combine_include(inc_a, inc_b, inc_c, logic='OR')

# Employed as a TA or IA
inc_TA = get_include_array('SAL9(SQ003)', "Yes")

# Unemployed and not on co-op
inc_unem = subtract_include(get_include_array('SAL9(SQ004)', "Yes"),
                            get_include_array('SAL6', "I am in a co-op work placement this semester."))

# Currently on co-op placement
inc_coop = get_include_array('SAL6', "I am in a co-op work placement this semester.")

# Employed but not as a TA
inc_d = get_include_array("SAL9(SQ001)", "Yes")
inc_e = get_include_array("SAL9(SQ002)", "Yes")
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
