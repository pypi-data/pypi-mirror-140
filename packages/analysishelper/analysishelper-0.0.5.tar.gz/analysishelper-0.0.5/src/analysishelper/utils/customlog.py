#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : codenamewei
# Created Date: 2021-12-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""Logging for file analysis"""
# ---------------------------------------------------------------------------
import os
import logging
from configparser import ConfigParser
from .customdatetime import *

"""
Create logs 
DEBUG < INFO < WARNING < ERROR < CRITICAL

Configure in one file

import customlog
customlog.configure


the rest can be run in the normal wa

import logging

logging.info(<fill in your message>)
logging.warning(<fill in your message>)
"""

logformat = {
'notebook': '%(asctime)s %(levelname)s: %(message)s', 
'script': '%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(funcName)s(): %(message)s'
}

def configure(logfile = None, logpath = None, loglevel = logging.INFO, suppressmessage = False, isnotebook = False):

    if (logpath is None) or (os.path.exists(logpath) is False):

        config = ConfigParser()
        configpath = "../metadata/config.ini"
        config.read(configpath)

        homedir = config.get("default", 'homedir')

        defaultpath = os.path.join(os.path.expanduser('~'), homedir)

        if not suppressmessage:
            
            print("Log path assigned not exist. Reassign to current path: " + defaultpath)

        logpath = defaultpath

    if logfile is None:

        logfile = customdatetime.getstringdatetime() + ".log"#create with current date and time if not specified

    logfullpath = os.path.join(logpath, logfile)
    
    logging.basicConfig(filename = logfullpath, 
        level = loglevel,
        format= logformat["notebook"] if isnotebook is True else logformat["script"],
        datefmt='%Y-%m-%d %H:%M:%S') 
    
    if not suppressmessage:
        print("Loggingfile at " + logfullpath)  