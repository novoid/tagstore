#!/usr/bin/env python
from tscore.loghelper import LogHelper
import logging

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
Created on April 1, 2011
'''

import os

class PathHelper(object):
    '''
    classdocs
    '''
    

    def __init__(self, params):
        '''
        Constructor
        '''
    
    @staticmethod
    def get_item_name_from_path(path):
        """
        returns the name of the substring after the most right slash
        """
        LOG = LogHelper.get_app_logger(logging.INFO)

        if path is None or path == "":
            LOG.error("there is no path given")
            return None
        
        item_name = os.path.split(path)[1]
        print item_name
        if item_name is None or item_name == "":
            LOG.error("there is no item name given: %s" % path)
            return None
        
        return item_name

    @staticmethod
    def resolve_store_path(path_to_be_resolved, store_path_list):
        """
        provide a absolute or an relative path to an item.
        this method returns the path to the containing store
        
        a list with all configured stores must be passed in order to identify the appropriate store
        
        RETURNS found resolved store_path
        
        RETURNS NONE if there is no appropriate store configured for the given path
        """
        LOG = LogHelper.get_app_logger(logging.INFO)
        
        if path_to_be_resolved is None or path_to_be_resolved == "":
            LOG.error("there is no path given")
            return None
        if store_path_list is None or len(store_path_list) == 0:
            LOG.error("there is no store list given")
            return None
            
        absolute_path = os.path.abspath(path_to_be_resolved)
        
        for store_path in store_path_list:
            store_path = os.path.abspath(store_path)
            if absolute_path.find(store_path) > -1:
                return store_path
        
        return None 

## end     