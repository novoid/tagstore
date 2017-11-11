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
Created on Oct 13, 2010
'''
import sys
import codecs
from PyQt4 import QtCore

class VocabularyWrapper(QtCore.QObject):
    """
    wrapper class for reading and writing the line based vocabulary dict
    """


    def __init__(self, file_path):
        QtCore.QObject.__init__(self)
        
        self.__watcher = QtCore.QFileSystemWatcher(self)
        self.__watcher.addPath(file_path)
#        self.__watcher.connect(self.__watcher,QtCore.SIGNAL("fileChanged(QString)"), QtCore.SIGNAL("changed"))
        self.__watcher.connect(self.__watcher,QtCore.SIGNAL("fileChanged(QString)"), self.__file_changed)
    
        self.__file_path = file_path
    
    @staticmethod
    def create_vocabulary_file(file_path):
        """
        create a new vocabulary file
        this  method has to be used in a static way
        the file must be opened with write permission
        """
        file = codecs.open(file_path, "w", TsConstants.DEFAULT_ENCODING)
        file.close()
        
    def __file_changed(self):
        """
        event handler: called when file was changed
        """
        self.emit(QtCore.SIGNAL("changed"))
    
    def get_vocabulary(self):
        """
        get all vocabulary stored in the vocabulary file
        returns a list
        """
        voc_list = []
        
        voc_file = codecs.open(self.__file_path,"r", TsConstants.DEFAULT_ENCODING)
        for line in voc_file:
            voc_list.append(line.strip("\n"))
        voc_file.close()
        
        return voc_list
    
    def add_vocable(self, single_vocable):
        """
        add a single word to the vocabulary file
        """
        ## using "a" (APPEND) as open parameter   
        voc_file = codecs.open(self.__file_path,"a", TsConstants.DEFAULT_ENCODING)
        voc_file.write("%s\n" % single_vocable)
        voc_file.close()

    def add_vocabulary(self, vocable_set):
        """
        add a set of words to the vocabulary file
        """
        voc_file = codecs.open(self.__file_path,"a", TsConstants.DEFAULT_ENCODING)
        for vocable in vocable_set:
            voc_file.write("%s\n" % vocable)
        voc_file.close()
        
    def set_vocabulary(self, vocable_set):
        """
        replace the current vocabulary and add the provided list of new vocabulary 
        """
        ## opening in write mode means the existing file content will be over-written
        voc_file = codecs.open(self.__file_path,"w", TsConstants.DEFAULT_ENCODING)
        for vocable in vocable_set:
            voc_file.write("%s\n" % vocable)
        voc_file.close()
## end