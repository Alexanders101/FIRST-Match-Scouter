#!/usr/bin/env bash

pyside-uic main_window.ui -o ../frc_scouter/main_window.py
pyside-uic add_window.ui -o ../frc_scouter/add_window.py
pyside-uic start_window.ui -o ../frc_scouter/start_window.py