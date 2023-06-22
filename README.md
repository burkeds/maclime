# mhwpy
Code used to analyze the McMaster Department of Physics and Astronomy mental health and wellness survey.
Main is included as an example of how to use include arrays and the methods written for a given survey.
For a given survey, the user must create a main file and call methods from a dedicated module for that survey. 
An example of this is the mhw_spring_2023 module. This module contains methods that can be used to analyze the data
in a Limesurvey results and statistics output .csv file.

Before loading data, you should configure the package using mhw.config.

This code is not available in a package manager and can be installed manually by cloning the repository and running:

```python setup.py install```

From the root directory of the repository.

This code uses the pandas library to read in the data from the survey and then uses matplotlib to create plots of the
data. This code can be adapted to analyze other Limesurvey. Limesurvey statistics.csv files can
be used as is. The results .csv file will require the user add in question codes as column
headers. The question codes can be found in the Limesurvey statistics.csv file.
