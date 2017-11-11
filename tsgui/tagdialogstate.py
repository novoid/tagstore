#!/usr/bin/env python

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
Created on Oct 17, 2010
'''

from PyQt4 import QtCore

class TagDialogState(QtCore.QObject):
    """
    class to check the state of the tag-dialog.
    has a method to tell whether all prerequisites are met 
    to allow the tagging-process 
    """


    def __init__(self):
        """
        if one of these flags is True - the tagging process cannot be allowed 
        """        
        QtCore.QObject.__init__(self)
        
        self.__item_not_selected = False
        self.__no_tag_entered = False
        self.__no_category_entered = False
        self.__category_limit_exceeded = False
        self.__not_allowed_category = False
        self.__tag_limit_exceeded = False
        self.__not_allowed_category = False
        
        self.__check_category_entered = False
        self.__check_controlled_vocab = False
      
        self.__everything_ok = False
    
    def set_item_not_selected(self, not_selected):
        self.__item_not_selected = not_selected
        self.__check_and_emit()
        
    def set_no_tag_entered(self, no_tag_entered):
        self.__no_tag_entered = no_tag_entered
        self.__check_and_emit()
        
    def set_no_category_entered(self, no_category_entered):
        self.__no_category_entered = no_category_entered
        self.__check_and_emit()
        
    def set_category_limit_exceeded(self, limit_exceeded):
        self.__category_limit_exceeded = limit_exceeded
        self.__check_and_emit()
        
    def set_tag_limit_exceeded(self, limit_exceeded):
        self.__tag_limit_exceeded = limit_exceeded
        self.__check_and_emit()
    
    def set_not_allowed_category(self, not_allowed):
        self.__not_allowed_category = not_allowed
        self.__check_and_emit()
      
    def set_category_mandatory(self, mandatory):
        self.__check_category_entered = True

    def set_check_vocab(self, mandatory):
        self.__check_controlled_vocab = True
        
    def check_tag_prerequisites(self):
        if not self.__item_not_selected and not self.__no_tag_entered and not self.__category_limit_exceeded and not self.__tag_limit_exceeded: 
                        
            ## check the category, if enabled
            if self.__check_category_entered:
                if self.__no_category_entered:
                    return False
            ## check the used vocabulary, if enabled
            if self.__check_controlled_vocab:
                if self.__not_allowed_category:
                    return False
            return True
        else:
            return False
        
    def __check_and_emit(self):
        """
        check the current state and emit the corresponding signal to the parent object
        """
        self.emit(QtCore.SIGNAL("tagging_state_updated"), self.check_tag_prerequisites())
        
## end        