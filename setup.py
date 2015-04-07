__author__ = 'alex'

from distutils.core import setup

setup(  name = "Event Scouter",
        version = "0.96",
        description = "A Scouter for the 2015 FRC season",
        author= 'Alex Shmakov',
        author_email= "alexanders101@gmail.com",
        url="https://github.com/Alexanders101/FIRST-Match-Scouter",
        requires=['joblib', 'PySide', 'matplotlib', 'numpy'],
        packages=['event_scouter']
        )