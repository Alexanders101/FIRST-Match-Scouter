__author__ = 'alex'

import sys
from cx_Freeze import setup, Executable

# # Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

options = {
    'build_exe': {
        'compressed': True,
        'includes': [
            'FRC_Event_Scouter',
            'Blue_Alliance_API',
            'add_window',
            'main_window',
            'start_window',
            'utils'
        ],
        'path': sys.path + ['frc_scouter']
    }
}


if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Event Scouter",
        version = "0.96",
        description = "A Scouter for the 2015 FRC season",
        author= 'Alex Shmakov',
        author_email= "alexanders101@gmail.com",
        packages=['frc_scouter'],
        options = options,
        executables = [Executable("frc_scouter/FRC_Event_Scouter.py", base=base)])

