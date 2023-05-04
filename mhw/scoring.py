"""
Created on May 18, 2022

@author: Devin Burke
"""

# Store dictionaries that map responses to arbitrary
# numerical values valid for a list of questions.
def get_value_dict(code):
    agree_list = ['AE1(SQ001)',
                  'AE1(SQ001)',
                  'AE1(SQ002)',
                  'AE1(SQ003)',
                  'AE1(SQ004)',
                  'AE1(SQ005)']                  
    freq_list = ['MH0(SQ001)',
                 'MH0(SQ002)',
                 'MH0(SQ003)',
                 'MH0(SQ004)',
                 'MH0(SQ005)',
                 'MH1(SQ001)',
                 'MH1(SQ002)',
                 'MH1(SQ003)',
                 'MH1(SQ004)',
                 'MH1(SQ005)',
                 'MH1(SQ006)',
                 'AE0(SQ001)',
                 'AE0(SQ002)',
                 'AE0(SQ003)',
                 'AE0(SQ004)',
                 'AE0(SQ005)',
                 'AE0(SQ006)',                 
                 'AE2(SQ001)',
                 'AE2(SQ002)',
                 'AE2(SQ003)',
                 'AE2(SQ004)',
                 'AE2(SQ005)',
                 'AE2(SQ006)',
                 'AE2(SQ007)',
                 'AE2(SQ008)',
                 'AE2(SQ009)',
                 'AE2(SQ016)',
                 'AE21(SQ001)',
                 'AE21(SQ002)',
                 'AE21(SQ003)',
                 'AE21(SQ004)',
                 'AE21(SQ005)',
                 'AE21(SQ006)',
                 'AE3(SQ001)',
                 'AE3(SQ002)',
                 'AE3(SQ003)',
                 'AE3(SQ004)',
                 'AE3(SQ005)',
                 'AE3(SQ006)',
                 'AE4(SQ001)',
                 'AE4(SQ002)',
                 'AE4(SQ003)',
                 'AE4(SQ004)',
                 'AE4(SQ005)',
                 'AE4(SQ006)',
                 'AE5(SQ001)',
                 'AE5(SQ002)',
                 'AE5(SQ003)',
                 'AE5(SQ004)',
                 'AE5(SQ005)']    
    pos_neg_list = ['AE6(SQ001)',
                    'AE6(SQ002)',
                    'AE6(SQ003)',
                    'AE6(SQ004)',
                    'AE6(SQ005)',
                    'AE6(SQ006)',
                    'AE6(SQ007)',
                    'AE6(SQ008)',
                    'AE6(SQ009)',
                    'AE6(SQ010)']
    if code in freq_list:
        return {'None of the time': 0,
                'Rarely': 1,
                'Some of the time': 2,
                'Most of the time': 3,
                'All of the time': 4} 
    if code in pos_neg_list:   
        return {'Strongly negative': -2,
                'Negative': -1,
                'Neutral': 0,
                'Positive': 1,
                'Strongly positive': 2}
    if code == 'MH2':
        return {'In crisis': -2,
                'Struggling': -1,
                'Surviving': 0,
                'Thriving': 1,
                'Excelling': 2}
    if code in agree_list:
        return {'Strongly disagree': -3,
                'Disagree': -2,
                'Somewhat disagree': -1,
                'Neither agree nor disagree': 0,
                'Somewhat agree': 1,
                'Agree': 2,
                'Strongly agree': 3}


# An array of responses passed returns an array of scored values using value_dict
def get_scored_data(code, responses):
    value_dict = get_value_dict(code)
    scores = []
    for response in responses:
        if response in value_dict.keys():
            scores.append(value_dict[response])
    return scores
