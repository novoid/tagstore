# -*- coding: utf-8 -*-

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
from tscore.enums import EConflictType
from PyQt4 import QtCore

class StoreInitError(Exception): pass
"""
custom error class to throw store specific error messages
this exception is thrown:
- during store initialization, if the expected store directory could not be found
"""

class StoreTaggingError(Exception): pass
"""
custom error class to throw store specific error messages during setting/updating/deleting tags
this exception is thrown:
- if a conflict occurs between tag names and link names (file names)
"""

class InodeShortageException(Exception):
    """
    use this exception if the number of free inodes has exceeded the defined threshold
    """
    def __init__(self, threshold):
        self.threshold = threshold
        
    def __str__(self):
        return "The Number of free inodes is below the threshld of %s%" % self.threshold
    
    def get_threshold(self):
        return self.threshold

class NameInConflictException(Exception):
    """
    this exception is thrown, when a tag has the same name as an already existing item
    """
    def __init__(self, name, conflict_type):
        self.name = name
        self.conflict_type = conflict_type
    
    def __str__(self):
        if self.conflict_type == EConflictType.FILE:
            return "The filename - %s - is in conflict with an already existing tag" % self.name
        elif self.conflict_type == EConflictType.TAG:
            return "The tag - %s - is in conflict with an already existing file" % self.name
        else:
            return "A tag or item is in conflict with an already existing tag/item"
        
    def get_conflict_type(self):
        return self.conflict_type
    def get_conflicted_name(self):
        return self.name


## end