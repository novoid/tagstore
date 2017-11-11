#!/usr/bin/env python
from PyQt4 import QtCore

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
Created on Oct 28, 2010
'''
import re


class SpecialCharHelper(object):
    '''
    classdocs
    '''
    DEFAULT_NOT_ALLOWED_CHARS = "/,?,<,>,\,:,*,|,\""
    DEFAULT_NOT_ALLOWED_STRINGS = "com1,com2,com3,com4,com5,com6,com7,com8,com9,lpt1,lpt2,lpt3,lpt4,lpt5,lpt6,lpt7,lpt8,lpt9,con,nul,prn"

    def __init__(self, params):
        '''
        Constructor
        '''

    @staticmethod
    def safe_unicode(obj, *args):
        try:
            return unicode(obj, *args)
        except UnicodeDecodeError:
            #obj is byte string
            ascii_text = str(obj).encode("string_escape")
            return unicode(ascii_text)

    @staticmethod
    def safe_str(obj):
        """
        convert the parameter to a python string object
        the param can be a normal unicode object OR a QString object 
        """
        try:
            return str(obj)
        except UnicodeEncodeError:
            # obj is unicode
            return unicode(obj).encode("unicode_escape")

    @staticmethod
    def get_not_allowed_strings_list():
        """
        tags are not allowed to be named like any of these strings
        """
        return unicode(SpecialCharHelper.DEFAULT_NOT_ALLOWED_STRINGS.split(","))
    
    @staticmethod
    def get_not_allowed_chars_list():
        """
        these chars are not allowed to appear in any of the tags
        """
        return SpecialCharHelper.DEFAULT_NOT_ALLOWED_CHARS.split(",")
    
    @staticmethod
    def contains_special_chars(tag_list):
        """
        check the given list, if any of its items contains a not allowed special character
        """
        char_list = SpecialCharHelper.get_not_allowed_chars_list()
        for tag in tag_list:
            for char in char_list:
                if tag.find(char) != -1:
                    return True
        return False
        
    @staticmethod
    def is_special_string(tag_list):
        """
        check the given list, if any of its items equals a reserved keyword (which is not allowed to be used)
        """
        string_list = SpecialCharHelper.get_not_allowed_strings_list()
        for tag in tag_list:
            if tag in string_list:
                return tag
        return ""

    @staticmethod
    def is_datestamp(string_to_check):
        match = re.match("^(([0-9]{4})-[0-1][0-9](-[0-3][0-9])?)$", string_to_check)
        #match = re.match("([0-9]{4})(-)([01,02,03,04,05,06,07,08,09,10,11,12]{1})((-)([0-3]{1})([0-9]{1})?)", string_to_check)
        if match:
            return True
        return False
    
    @staticmethod
    def is_partial_expiry_tag(prefix, tag):
        """
        returns TRUE if the tag is part of a valid expiry timestamp
        """
        match = None
        tag_length = len(tag);
        prefix_length = len(prefix)
        
        #if the give tag is shorter than the actual prefix
        if prefix_length >= tag_length:
            prefix = prefix[:len(tag)]
            match = re.match(prefix, tag)
        #this is the case when it comes to validate the date pattern
        else:
            post_expression = ""
            pre_expression = "^("+prefix+")"
            
            post_length = tag_length - prefix_length 
            if post_length == 1:
                post_expression = "[0-9]"
            elif post_length == 2:
                post_expression = "([0-9]{2})"
            elif post_length == 3:
                post_expression = "([0-9]{3})"
            elif post_length == 4:
                post_expression = "([0-9]{4})"
            elif post_length == 5:
                post_expression = "([0-9]{4})-"
            elif post_length == 6:
                post_expression = "([0-9]{4})-([0-1])"
            elif post_length == 7:
                post_expression = "([0-9]{4})-(0[0-9]|1[0-2])"
            else:
                # the tag is too long 
                return False
            match = re.match(pre_expression+post_expression, tag)
    
        if match: 
            return True
        else:
            return False
        
    @staticmethod
    def is_expiry_tag(prefix, tag):
        """
        returns TRUE if the tag contains a valid expiry timestamp
        """
        match = re.match("^("+prefix+")([0-9]{4})(-)([0-9]{2})", tag)
            
        if match: 
            return True
        else:
            return False

## end     