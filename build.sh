#!/bin/bash

#nuitka3 --standalone --disable-console --enable-plugin=pyside6 --show-progress --show-memory --nofollow-imports --recurse-all -i ./images/cutter.ico ./src/main.py

pyinstaller --exclude-module PySide6 --exclude-module PyQt5 --exclude-module matplotlib  --exclude-module IPython -i ./images/cutter.ico src/main.py 
