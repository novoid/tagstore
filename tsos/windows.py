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

import win32com.client
import os
from tscore.enums import EOS

class FileSystem():

    def __init__(self):
        self.__shell = win32com.client.Dispatch("WScript.Shell")
    
    def get_type(self):
        return EOS.Windows
    
    def create_link(self, source, link_name):
        """
        creates a .lnk link with given link_name using an absolute path to the source
        """
        
        name = unicode(link_name + ".lnk")
        source = unicode(source)
        
        shortcut = self.__shell.CreateShortCut(name)
        shortcut.Targetpath = source
        shortcut.save()

    def remove_link(self, link):
        """
        removes a windows .lnk link from file system and empty folders as well
        """
        file_path = unicode(link+".lnk")
        if os.path.exists(file_path):
            os.remove(file_path)

        ## delete folder if empty
        parent_path = os.path.dirname(unicode(link))
        if os.path.exists(parent_path):             #existing
            if len(os.listdir(parent_path)) == 0:   #empty
                os.rmdir(parent_path)                       
        
    def inode_shortage(self, file_path, threshold_pct):
        """
        returns True (on Linux), if the free number of inodes (non-root) < threshold_pct of all available
        Caution: Windows does not support this functionality, that's why it returns False in any case
        """
        return False
                
## end