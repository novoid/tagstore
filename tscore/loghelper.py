#!/usr/bin/env python
from tscore.tsconstants import TsConstants

# -*- coding: iso-8859-15 -*-
## this file is part of tagstore, an alternative way of storing and retrieving information
## Copyright (C) 2010  Karl Voit, Christoph Friedl, Wolfgang Wintersteller
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.org/licenses/>.
'''
Created on Nov 25, 2010
'''
import logging.handlers


class LogHelper(object):
    """
    small class to get various logger objects easily
    """

    def __init__(self, params):
        self.__log = None

    @staticmethod
    def get_app_logger(level):
        '''
        create a logger object with appropriate settings
        '''
        # TODO create a class for doing this
        LOG_FILENAME = TsConstants.LOG_FILENAME
        log = logging.getLogger(TsConstants.LOGGER_NAME)
        ## if this is a fresh not yet configured logger, continue with configuring
        ## otherwise just return the already existing logger
        if log.level != logging.NOTSET:
            return log
        log.setLevel(level)

        #logging.basicConfig(level=logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s")

        ## create console handler and set level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        ## create filehandler
        file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, 
            maxBytes=TsConstants.LOG_FILESIZE, backupCount=TsConstants.LOG_BACKUP_COUNT)
        file_handler.setFormatter(formatter)

        ## add handlers to logger
        log.addHandler(console_handler)
        log.addHandler(file_handler)
        
        log.info("APPlogger does not exist - created a new one")
        return log

    
    @staticmethod
    def get_store_logger(path, level):
        '''
        create a logger object with appropriate settings
        '''
        
        store_name = str(path).split("/")[-1]
        
        log = logging.getLogger(TsConstants.STORE_LOGGER_NAME + "_" + store_name)
        
        ## if this is a fresh not yet configured logger, continue with configuring
        ## otherwise just return the already existing logger
        if log.level != logging.NOTSET:
            return log
        
        log.setLevel(level)


        #logging.basicConfig(level=logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s")

        ## create console handler and set level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)


        config_file_path = path + "/" + TsConstants.DEFAULT_STORE_CONFIG_DIR + "/" + TsConstants.STORE_LOG_FILENAME

        ## create filehandler
        file_handler = logging.handlers.RotatingFileHandler(config_file_path, 
            maxBytes=TsConstants.LOG_FILESIZE, backupCount=TsConstants.LOG_BACKUP_COUNT)
        file_handler.setFormatter(formatter)

        ## add handlers to logger
        log.addHandler(console_handler)
        log.addHandler(file_handler)
        
        log.info("STORElogger for %s does not exist - created a new one" % store_name)
        return log
        