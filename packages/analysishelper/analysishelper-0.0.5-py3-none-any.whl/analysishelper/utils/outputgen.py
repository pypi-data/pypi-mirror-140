from configparser import ConfigParser, ExtendedInterpolation, RawConfigParser
import os
import logging

class OutputGen:

    output_root_path = ""

    #TODO: Add ability to config output_path
    def __init__(self, output_path = None):

        if output_path is None:
            config = ConfigParser(interpolation=ExtendedInterpolation())
            configpath = "../metadata/config.ini"
            config.read(configpath)

            homedir = config.get("default", 'homedir')

            self.output_root_path = os.path.join(os.path.expanduser('~'), homedir)

        if not os.path.exists(self.output_root_path):
        
            os.makedirs(self.output_root_path)
            logging.info(f"Analysishelper directory created at f{self.output_root_path}")

    def get_output_path(self):

        return self.output_root_path