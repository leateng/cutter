#!/bin/bash

nuitka3 --standalone --disable-console --enable-plugin=pyside6 --show-progress --show-memory --nofollow-imports --recurse-all ./src/main.py
