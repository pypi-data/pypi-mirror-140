#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Read the configuration file.
"""

import os
from configparser import ConfigParser

# read client configuration from:
# 1. The location with deployed package, e.g. ./config/client.ini
# 2. Could be overriden with ~/.phantasy-rest/client.ini if exists
#

_CWD = os.path.dirname(os.path.abspath(__file__))
_USER_CONFIG_PATH = "~/.phantasy-rest/client.ini"

def get_config_file():
    """Get the file path of the configuration file.
    """
    user_config_fullpath = os.path.abspath(
            os.path.expanduser(_USER_CONFIG_PATH))
    if os.path.isfile(user_config_fullpath):
        return user_config_fullpath
    return os.path.join(_CWD, "client.ini")


def read_config():
    """Read out the configuration as a dict.
    """
    filepath = get_config_file()
    config = ConfigParser()
    config.read(filepath)
    svr_conf = config[config['default']['use']]
    return dict(svr_conf.items())
