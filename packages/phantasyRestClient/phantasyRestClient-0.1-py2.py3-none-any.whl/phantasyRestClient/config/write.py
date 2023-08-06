#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

_CWD = os.path.dirname(os.path.abspath(__file__))

def write_config(filepath):
    """Write a sample configuration into a file.
    """
    fullpath = os.path.abspath(os.path.expanduser(filepath))
    with open(os.path.join(_CWD, "client.ini"), "r") as fin:
        with open(fullpath, "w") as fout:
            fout.write(fin.read())

