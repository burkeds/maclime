# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from mhw.utils import *

data = pd.read_excel('main/statistic-survey265235.xls', header=None)

codex = generate_codex(data)

#for code in codex:
#    pie_chart(code, 5, get_top_question(code) + " (" + code + ")", get_subquestion(code))

#for code in codex:
#    print("*********************************************************************************************************")
#    print(get_top_question(code))
#    print(get_subquestion(code))
#    print("Question code: ", code)
#    print("Possible answers: ", get_possible_answers(code))
#    print("Counts: ", get_counts(code))
#    print("Percentage: ", get_data(code))
#    arr = np.array(get_possible_answers(code))
#    arr = np.vstack([arr, get_counts(code)])
#    arr = np.vstack([arr, get_data(code)])
#    print(arr)
    





