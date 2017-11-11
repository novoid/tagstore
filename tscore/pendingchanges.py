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


import time
from tscore.enums import EFileEvent

class PendingChanges:
    def __init__(self):
        """
        constructor
        """
        self.__queue = []

    def length(self):
        """
        returns the number of existing items
        """
        return len(self.__queue)
    
    def get_first(self, delete=False):
        """
        returns first item of the list
        if parameter delete=True the item is deleted
        """
        if len(self.__queue) > 0:
            item = self.__queue[0]
            if delete:
                self.__queue.remove(item)
            return item
        return None    
        
    def to_string(self):
        """
        returns a comma-separated list of pending files in correct order
        """
        return ", ".join(self.get_names())
            
    def register(self, file_name, type_enum, event_enum):
        """
        adds/registers file with type, timestamp and event
        overwrites items with the same file name if they exist
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for item in self.__queue:
            if item["file"] == unicode(file_name):
                item["type"] = type_enum
                item["event"] = event_enum
                return
        self.__queue.append(dict(file=unicode(file_name), type=type_enum, timestamp=timestamp, event=event_enum))
    
    def edit(self, old_file_name, new_file_name):
        """
        edits an existing file object: needed to keep the objects storage position during rename
        """
        ## delete file before rename
        self.remove(unicode(new_file_name))      
        for item in self.__queue:
            if item["file"] == unicode(old_file_name):
                item["file"] = unicode(new_file_name)
    
    def remove(self, file_name):
        """
        removes file from instance
        """
        for item in self.__queue:
            if item["file"] == unicode(file_name):
                self.__queue.remove(item)
                return

    def get_names(self):
        """
        returns a list of all files currently stored
        """
        items = []
        for item in self.__queue:
            items.append(item["file"])
        return items
        
    def get_added_names(self):
        """
        returns a list of all added files: EFileEvent = ADDED or ADDED_OR_RENAMED
        """
        items = []
        for item in self.__queue:
            if item["event"] == EFileEvent.ADDED or item["event"] == EFileEvent.ADDED_OR_RENAMED:
                items.append(item["file"])
        return items
    
    def get_removed_names(self):
        """
        returns a list of all removed files: EFileEvent = REMOVED or REMOVED_OR_RENAMED
        """
        items = []
        for item in self.__queue:
            if item["event"] == EFileEvent.REMOVED or item["event"] == EFileEvent.REMOVED_OR_RENAMED:
                items.append(item["file"])
        return items
    
    def get_items_by_event(self, event_enum):
        """
        returns a list of files filtered by given event name
        """
        items = []
        for item in self.__queue:
            if item["event"] == event_enum:
                items.append(item["file"])
        return items
    
    
## end
