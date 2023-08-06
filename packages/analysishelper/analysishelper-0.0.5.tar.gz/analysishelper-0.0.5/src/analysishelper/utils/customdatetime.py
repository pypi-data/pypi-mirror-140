#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Chia Wei Lim
# Created Date: 2021-12-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""Module related to datetime formatting"""
# ---------------------------------------------------------------------------
from datetime import date

def getstringdatetime():

    current_time = date.today()
    strtime = current_time.strftime("%Y-%m-%d")
    return strtime


