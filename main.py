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
from mhw.config import all_respondents
from mhw.mhw_spring_2022 import mental_health_scores
from mhw.mhw_spring_2022 import mental_health_continuum_stats
from mhw.mhw_spring_2022 import impact_of_single_academics_on_mental_health
from mhw.mhw_spring_2022 import mean_impact_of_all_academics_on_health
from mhw.mhw_spring_2022 import ae0_and_ae1, ae2, ae21, ae3, ae4, ae5
from mhw.include_arrays import *
from mhw.include_arrays import get_true_count
import sys
import os

#Output_dict describes output directories by their relative path from the working directory
#Each key maps to a path, an include array, and a file description
#dict format  {key                   : [path,                         include,        description] }
path = '\\results\\'
output_dict = {'all'                    : [path+'all\\',                    include_all,    'all_respondents'],
               'coop_placement'         : [path+'coop_placement\\',         inc_coop,       'coop_placement'],
               'disabilities'           : [path+'disabilities\\',           inc_disa,       'respondents_with_disability'],
               'employed'               : [path+'employed\\',               inc_emp,        'employed(not_on_co-op)'],
               'employed_as_TA'         : [path+'employed_as_TA\\',         inc_TA,         'employed(as_TA)'],
               'employed_as_notTA'      : [path+'employed_notTA\\',         inc_emp_notTA,  'employed(not_TA_or_co-op)'],
               'female'                 : [path+'female\\',                 inc_fem,        'female_respondents'],
               'male'                   : [path+'male\\',                   inc_mal,        'male_respondents'],
               'grads'                  : [path+'grads\\',                  inc_grad,       'graduate_respondents'],
               'undergrads'             : [path+'undergrads\\',             inc_under,      'undergraduate_respondents'],
               'unemployed_not_coop'    : [path+'unemployed_not_coop\\',    inc_unem,       'unemployed_respondents'],
               'racialized'             : [path+'racialized\\',             inc_race,       'racialized_respondents'],
               'danger'                 : [path+'danger\\',                 inc_danger,     'struggling_or_in_crisis'],
               'grads_racialized'       : [path+'grads_racialized\\',       inc_grad_race,  'racialized_graduates'],
               'undergrads_racialized'  : [path+'undergrads_racialized\\',  inc_under_race, 'racialized_undergrads'],
               'undergrads_not_racialized' : [path+'undergrads_not_racialized\\',  inc_under_not_race, 'not_racialized_undergrads'],
               'undergrad_female'       :   [path+'undergrad_female\\',     inc_under_fem, 'female_undergraduate'],
               'undergrad_male'         :   [path+'undergrad_male\\',       inc_under_mal, 'male_undergraduate'],
               'graduate_female'        :   [path+'graduate_female\\',      inc_grad_fem, 'female_graduate'],
               'graduate_male'          :   [path+'graduate_male\\',        inc_grad_mal, 'male_graduate']
               }

output_keys = output_dict.keys()
top_working_dir = os.getcwd()
for key in output_keys:
    include = output_dict[key][1]
    #By default, include arrays are compared with their complement.
    #Give a value to other_include to instead compare with an arbitrary array.
    other_include = None        
    desc = output_dict[key][2]
    os.chdir(top_working_dir + output_dict[key][0])
        
    #Print to system file. Comment this line to print to python console.       
    #sys.stdout = open(desc+".txt", "w")
       
    valid_resp = get_true_count(include)

    print("Description:\t", desc)
    print("Total number of respondents:\t", all_respondents)
    print("Number of\t", desc+":", "\t", valid_resp )
    print("********************************************************************")
    impact_of_single_academics_on_mental_health(include, desc, other_include)
    mean_impact_of_all_academics_on_health(include, desc,  other_include)
    mental_health_continuum_stats(include, desc, other_include)
    ae0_and_ae1(include, desc, other_include)
    ae2(include, desc, other_include)
    ae21(include, desc, other_include)
    ae3(include, desc, other_include)
    ae4(include, desc, other_include)
    ae5(include, desc, other_include)
    mental_health_scores(include, desc, other_include)
print("END")