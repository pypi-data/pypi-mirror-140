import pandas as pd
import os
import logging
from analysishelper.utils import customlog
from configparser import ConfigParser

class CategoryMap:
    """
    Build Mapping of 
    - db_category 
    - panel_id(Large Group)
    - description(Large Group)
    - panel_id(Implemented Group)
    - description(Implemented Group)
    """
    
    def __init__(self):

        self.configpath = "../metadata/config.ini"

        print("DEBUGGING: " + self.configpath)

        #configure log setting
        customlog.configure()

    def update(self, inputpath = r"C:\Users\lich1003\OneDrive - Nielsen IQ\KReCom5\input_py\fin_inputs\default\info", catalogfile = "Catalog_new_220105.xlsx", outputrootpath = None):

        catalogpath = os.path.join(inputpath, catalogfile)

        if os.path.exists(catalogpath) is False:

            logging.warning(f"Catalog file f{catalogpath} not exist. Update abort")
            return

        if os.path.exists(self.configpath) is False:

            logging.warning(f"Config path {self.configpath} not exist")

        #read in input
        config = ConfigParser()
        config.read(self.configpath) 

        if outputrootpath is None: 

            homedir = config.get("default", 'homedir')

            outrootpath = os.path.join(os.path.expanduser('~'), homedir)
            
        outcategorypath = os.path.join(outrootpath, config.get("default", "category_mapping_file"))

        #main ops
        df_large = pd.read_excel(catalogpath, sheet_name = "panel(Large Group)")
        df_impl = pd.read_excel(catalogpath, sheet_name = "panel(Implemented Group)")
        df_info = pd.read_excel(catalogpath, sheet_name = "category(Implemented Group)")

        df_info = df_info[["db_category", "panel_id", "panel_group"]]

        df_large = df_large.rename({"panel_id": "panel_id(Large Group)", "description": "description(Large Group)"}, axis = 1)
        df_impl = df_impl.rename({"panel_id": "panel_id(Implemented Group)", "description": "description(Implemented Group)"}, axis = 1)
        df_info = df_info.rename({"panel_id": "panel_id(Implemented Group)", "panel_group": "description(Large Group)"}, axis = 1)

        df_sub = df_info.merge(df_impl, on = "panel_id(Implemented Group)")
        df_category_table = df_sub.merge(df_large, on = "description(Large Group)")

        df_category_rearranged = df_category_table[["db_category", 'panel_id(Large Group)', 'description(Large Group)', 'panel_id(Implemented Group)', 'description(Implemented Group)']]

        if df_category_rearranged.shape[0] < 1:

            logging.critical("Category mapping table is empty. Output invalid. Validate this")


        df_category_rearranged.to_csv(outcategorypath, index = False)

        logging.info(f"Path of mapping file: {outcategorypath}")