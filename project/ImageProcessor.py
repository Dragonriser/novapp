# -*- coding: utf-8 -*-
from ExceptionManager import new_exception
from SatelliteImage import SatelliteImage
import os.path
import Logger

__author__ = 'emontenegro'


class ImageProcessor:
    #Attributes
    source_file_path = None
    error_pixels = 6

    #Constructor
    def __init__(self, source_file_path):
        if not source_file_path or not os.path.isfile(source_file_path):
            raise new_exception("ImageProcessor",
                                "Constructor",
                                "The file given is not valid as an input file")
        else:
            self.source_file_path = source_file_path
            #llamar al modulo de image


    #Methods
    def start_processing(self):
        pass

    def save_image_metadata(self):
        pass

    def load_image_metadata(self):
        pass