# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 14:50:54 2022

@author: Devin Burke, PhD. Department of Physics and Astronomy. McMaster University

This python project is designed to interpret statistics and results files exported by
limesurvey. Before the results file can be interpreted, you need to insert a row at the 
top of the results file and write in the question codes for each column. These are the codes
you assigned to each question and subquestion in limesurvey.

This file should be run as main. From here you import include arrays from the include_arrays file, and call functions
you have defined in a survey specific file such as mhw_spring_2022.
"""
import mhw.config
from mhw_spring_2023 import *
from mhw.include_arrays import *
import os

# Configure the package
CONFIG = mhw.config.get_config()
CONFIG.set_results_file('working/results/results-survey265235_2023.xls', header=0, skiprows=[1], index_col=0)
CONFIG.set_statistics_file('working/results/statistic-survey265235_2023.xls', header=None)
CONFIG.set_all_respondents(33)
CONFIG.set_population(350)

all_respondents = CONFIG.get_all_respondents()

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

# Output_dict describes output directories by their relative path from the working directory
# Each key maps to a path, an include array, and a file description
# dict format  {key                   : [path,                         include,        description] }

rpath = '\\working\\results\\'
output_dict = {'all'                    : [rpath+'all\\',                    include_all,    'all_respondents'],
               'coop_placement'         : [rpath+'coop_placement\\',         inc_coop,       'coop_placement'],
               'disabilities'           : [rpath+'disabilities\\',           inc_disa,       'respondents_with_disability'],
               'employed'               : [rpath+'employed\\',               inc_emp,        'employed(not_on_co-op)'],
               'employed_as_TA'         : [rpath+'employed_as_TA\\',         inc_TA,         'employed(as_TA)'],
               'employed_as_notTA'      : [rpath+'employed_notTA\\',         inc_emp_notTA,  'employed(not_TA_or_co-op)'],
               'female'                 : [rpath+'female\\',                 inc_fem,        'female_respondents'],
               'male'                   : [rpath+'male\\',                   inc_mal,        'male_respondents'],
               'grads'                  : [rpath+'grads\\',                  inc_grad,       'graduate_respondents'],
               'undergrads'             : [rpath+'undergrads\\',             inc_under,      'undergraduate_respondents'],
               'unemployed_not_coop'    : [rpath+'unemployed_not_coop\\',    inc_unem,       'unemployed_respondents'],
               'racialized'             : [rpath+'racialized\\',             inc_race,       'racialized_respondents'],
               'danger'                 : [rpath+'danger\\',                 inc_danger,     'struggling_or_in_crisis'],
               'grads_racialized'       : [rpath+'grads_racialized\\',       inc_grad_race,  'racialized_graduates'],
               'undergrads_racialized'  : [rpath+'undergrads_racialized\\',  inc_under_race, 'racialized_undergrads'],
               'undergrads_not_racialized' : [rpath+'undergrads_not_racialized\\',  inc_under_not_race, 'not_racialized_undergrads'],
               'undergrad_female'       :   [rpath+'undergrad_female\\',     inc_under_fem, 'female_undergraduate'],
               'undergrad_male'         :   [rpath+'undergrad_male\\',       inc_under_mal, 'male_undergraduate'],
               'graduate_female'        :   [rpath+'graduate_female\\',      inc_grad_fem, 'female_graduate'],
               'graduate_male'          :   [rpath+'graduate_male\\',        inc_grad_mal, 'male_graduate']
               }

output_keys = output_dict.keys()
top = os.getcwd()
for key in output_keys:
    include = output_dict[key][1]
    # By default, include arrays are compared with their complement.
    # Give a value to other_include to instead compare with an arbitrary array.
    other_include = None        
    description = output_dict[key][2]
    path = top + output_dict[key][0]
    if os.path.exists(path):
        os.chdir(path)
    else:
        os.mkdir(path)
        os.chdir(path)
        
    # Print to system file. Comment this line to print to python console.
    # sys.stdout = open(desc+".txt", "w")
       
    valid_resp = len(include)

    print("Description:\t", description)
    print("Total number of respondents:\t", all_respondents)
    print("Number of\t", description+":", "\t", valid_resp )
    print("********************************************************************")
    mh2(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae0(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae1(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae2(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae21(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae3(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae4(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae5(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
    ae6(include, description, other_include, print_table=False, make_figures=False, save_fig=False)
print("END")
