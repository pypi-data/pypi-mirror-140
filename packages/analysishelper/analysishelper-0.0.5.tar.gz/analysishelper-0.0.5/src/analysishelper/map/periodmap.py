#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Chia Wei Lim
# Created Date: 2021-12-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""Module related to appending period time"""
# ---------------------------------------------------------------------------
import pandas as pd
from configparser import ConfigParser, ExtendedInterpolation
import os
import json

class PeriodMap:

    def __init__(self):

        metadatapath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata")

        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(os.path.join(metadatapath, 'config.ini'))

        self.periodmapfile = config.get("default", 'period_mapping_file')
        
        pathtofile = os.path.join(metadatapath, self.periodmapfile)
        self.perioddf = pd.read_excel(pathtofile, sheet_name="period_dict", engine="openpyxl")

        self.perioddf = self.perioddf.drop(['month_', 'quarter_', 'half_year_', 'db_month_'], axis = 1)

    def appendperiod(self, df, left_on = "period_code", right_on = "period_code"):

        if left_on not in self.perioddf.columns: 

            print(f"{left_on} not found in analysishelper dataframe. Cant append period")

        if right_on not in df.columns: 

            print(f"{right_on} not found in input dataframe. Cant append period")
            
        # add checking for df[refcolumn] datatype to check if compatible
        perioddftype = self.perioddf[left_on].dtypes
        inputdftype = df[right_on].dtypes

        if ((str(perioddftype).startswith("int") is False) or (str(inputdftype).startswith("int") is False)) and (perioddftype is not inputdftype): 

            print(f"Columns to merge period not of the same type {perioddftype} <> {inputdftype}. Merging failed.")
            return df
        
        mergeddf = self.perioddf.merge(df, left_on = left_on, right_on = right_on)

        if left_on is not right_on:

            #remove one of the column
            mergeddf = mergeddf.drop(columns = [right_on], axis = 1)

        return mergeddf
