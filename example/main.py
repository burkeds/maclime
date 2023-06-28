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

# Import some useful packages
import os
from textwrap import wrap

# Configure the mhw package. This must be done before importing anything from mhw.
import mhw.config
CONFIG = mhw.config.create_config()
CONFIG.set_results_file(io=r'working/results/results-survey265235_2023.xls', header=0, skiprows=[1], index_col=0)
CONFIG.set_statistics_file(io=r'working/results/statistic-survey265235_2023.xls', header=None)
CONFIG.set_population(350)

# Import your survey file
from mhw_spring_2023 import *
CONFIG.set_value_dict_callback(get_value_dict)

# Import your include arrays
from my_includes import *

# QuestionSection objects can be used to define survey sections and access questions.
from mhw.questions import QuestionSection

# Import figure callback functions
from mhw.figures import make_histo, plot_impact_statistics

sample_size = CONFIG.get_all_respondents()
population_size = CONFIG.get_population()

# Define question sections which contain a list of question codes.
# Questions and results can be accessed by calling the question code.
# QuestionSection.questions[code] returns a Question object.
mh2 = QuestionSection(top_code='MH2',
                      title='Mental Health Continuum',
                      codes=['MH2']
                      )

ae0 = QuestionSection(top_code='AE0',
                      title='Social Perception',
                      codes=['AE0(SQ001)',
                             'AE0(SQ002)',
                             'AE0(SQ003)',
                             'AE0(SQ004)',
                             'AE0(SQ005)',
                             'AE0(SQ006)']
                      )

ae1 = QuestionSection(top_code='AE1',
                      title='Department Perception',
                      codes=['AE1(SQ001)',
                             'AE1(SQ002)',
                             'AE1(SQ003)',
                             'AE1(SQ004)',
                             'AE1(SQ005)']
                      )
ae2 = QuestionSection(top_code='AE2',
                      title='Graduate student workload',
                      codes=['AE2(SQ001)',
                             'AE2(SQ002)',
                             'AE2(SQ003)',
                             'AE2(SQ004)',
                             'AE2(SQ005)',
                             'AE2(SQ006)',
                             'AE2(SQ007)']
                      )

ae21 = QuestionSection(top_code='AE21',
                       title='TA workload',
                       codes=['AE21(SQ001)',
                              'AE21(SQ002)',
                              'AE21(SQ003)',
                              'AE21(SQ004)',
                              'AE21(SQ005)',
                              'AE21(SQ006)']
                       )

ae3 = QuestionSection(top_code='AE3',
                      title='Undergraduate workload',
                      codes=['AE3(SQ001)',
                             'AE3(SQ002)',
                             'AE3(SQ003)',
                             'AE3(SQ004)',
                             'AE3(SQ005)',
                             'AE3(SQ006)']
                      )

ae4 = QuestionSection(top_code='AE4',
                      title='Co-op workload',
                      codes=['AE4(SQ001)',
                             'AE4(SQ002)',
                             'AE4(SQ003)',
                             'AE4(SQ004)',
                             'AE4(SQ005)',
                             'AE4(SQ006)']
                      )

ae5 = QuestionSection(top_code='AE5',
                      title='Undergraduate thesis experience',
                      codes=['AE5(SQ001)',
                             'AE5(SQ002)',
                             'AE5(SQ003)',
                             'AE5(SQ004)',
                             'AE5(SQ005)']
                      )
ae6 = QuestionSection(top_code='AE6',
                      title='Impact of academics on wellness',
                      codes=['AE6(SQ001)',
                             'AE6(SQ002)',
                             'AE6(SQ003)',
                             'AE6(SQ004)',
                             'AE6(SQ005)',
                             'AE6(SQ006)',
                             'AE6(SQ007)',
                             'AE6(SQ008)',
                             'AE6(SQ009)',
                             'AE6(SQ010)']
                      )

# Dictionary of each section
sections = [mh2, ae0, ae1, ae2, ae21, ae3, ae4, ae5, ae6]

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

# Create labels to use for AE6
xlabels = ["classwork",
           "labwork",
           "testing",
           "research/thesis",
           "co-op",
           "TAs",
           "faculty/admin",
           "non-P&A",
           "students",
           "not academic"]
xlabels = ['\n'.join(wrap(label, 20)) for label in xlabels]
ylabels = ["strongly negative", "negative", "neutral", "positive", "strongly positive"]
ylabels = ['\n'.join(wrap(label, 10)) for label in ylabels]

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

    print("Description:\t", description)
    print("Total number of respondents:\t", sample_size)
    print("Respondents meeting inclusion criteria:\t", len(include))
    print("Estimated population size:\t", population_size)
    print("********************************************************************")

    analyze_ae(include=include,
               codes=mh2.codes,
               title=mh2.title,
               description=description,
               include_other=other_include,
               print_table=False,
               figure_callback=make_histo,
               callback_args={'title': mh2.title,
                              'description': description,
                              'save_figure': False})

    for section in sections[1:]:
        if section.top_code == 'AE6':
            analyze_ae(include=include,
                       codes=section.codes,
                       title=section.title,
                       description=description,
                       include_other=other_include,
                       print_table=False,
                       figure_callback=plot_impact_statistics,
                       callback_args={'title': mh2.title,
                                      'description': description,
                                      'save_figure': False,
                                      'x_labels': xlabels,
                                      'y_labels': ylabels})

        else:
            analyze_ae(include=include,
                       codes=section.codes,
                       title=section.title,
                       description=description,
                       include_other=other_include,
                       print_table=False,
                       figure_callback=make_histo,
                       callback_args={'title': mh2.title,
                                      'description': description,
                                      'save_figure': False})
print("END")
