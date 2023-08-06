#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Chia Wei Lim
# Created Date: 2021-12-10
# version ='1.0'
# ---------------------------------------------------------------------------
"""File system read in/out"""
# ---------------------------------------------------------------------------
import os
import shutil

def copyFileTo(self, filepath, outpath):
    """
    outputpath: can be file path or folder path (where same file name be used)

    Return False
    - inpath not exist
    - outdirpath not exist
    """
 
    if os.path.exists(filepath) is False:

        print("Input file path to copy not valid: " + filepath)

        return False

    elif os.path.exists(outpath) is False:

        print("Output file path not valid: " + outpath)

        return False

    # if is directory, use back original file name
    if os.path.isdir(outpath):
        pass
        #https://datatofish.com/copy-file-python/
        # FIXME: ADD CODE
        ##find file name 
        ## append 
        ## become new outpath

    shutil.copyfile(filepath, outpath)

    return True
