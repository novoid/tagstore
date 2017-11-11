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


import datetime
import re
import shutil
from PyQt4.QtCore import QSettings
from tscore.tsconstants import TsConstants
import logging
from tscore import loghelper
from tscore.loghelper import LogHelper


class TagWrapper():

    GROUP_FILES_NAME = "files"
    
    KEY_TAGS = "tags"
    KEY_TIMESTAMP = "timestamp"
    KEY_CATEGORIES = "category"
    KEY_HASHSUM = "hashsum"

    TAG_SEPARATOR = ","
    
    def __init__(self, file_path):#, store_id=None):
        """
        constructor
        """
        path_list = str(file_path).split("/")[:-2]
        logging_path = unicode("/").join(path_list)
        self.__log = LogHelper.get_store_logger(logging_path, logging.INFO)
        
        #if store_id is not None:
        #    self.__create_file_structure(file_path, store_id)
        self.__settings = QSettings(file_path, QSettings.IniFormat)
        self.__settings.setIniCodec(TsConstants.DEFAULT_ENCODING)
        if self.__settings.iniCodec() is None:
            self.__log.info("no such encoding: " + TsConstants.DEFAULT_ENCODING)
        self.__path = file_path
#    def __create_file_structure(self, file_path, store_id):
#        """
#        creates the default file structure in a given file
#        """
#        file = open(file_path, "w")
#        file.write("[store]\n")
#        file.write("store_id=%s\n" % store_id)
#        file.write("\n")
#        file.write("[files]\n")
#        file.write("\n")
#        file.write("[categories]\n")
#        file.close()
    
    @staticmethod
    def create_tags_file(file_path):
        """
        create a new tags file structure in the given file
        this  method has to be used in a static way
        the file must be opened with write permission
        """
        ## copy the config template to the new store config dir
        shutil.copyfile(TsConstants.STORE_TAGFILE_TEMPLATE_PATH, file_path)
          
    def __get_file_list(self):
        """
        returns a list of file dictionaries sorted by timestamp descending
        """
        file_list = []
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        for file in self.__settings.childGroups():
            self.__settings.beginGroup(file)            
            tags = unicode(self.__settings.value(self.KEY_TAGS, "").toString()).split(self.TAG_SEPARATOR)
            categories = unicode(self.__settings.value(self.KEY_CATEGORIES, "").toString()).split(self.TAG_SEPARATOR)
            timestamp = unicode(self.__settings.value(self.KEY_TIMESTAMP, "").toString())
            hashsum = unicode(self.__settings.value(self.KEY_HASHSUM, "").toString())            
            file_list.append(dict(filename=file, tags=tags, category=categories, timestamp=timestamp, hashsum=hashsum))
            self.__settings.endGroup()
        self.__settings.endGroup()
        return sorted(file_list, key=lambda k:k[self.KEY_TIMESTAMP], reverse=True)
        
    def get_files_with_tag(self, tag):
        """
        returns a list of file dictionaries including filename, tags, categories, timestamp
        """
        file_list = self.__get_file_list()
        filtered_list = []
        for file in file_list:
            if tag in file[self.KEY_TAGS] or tag in file[self.KEY_CATEGORIES]:
                filtered_list.append(file)
        return filtered_list
    
    def get_files_with_expiry_tags(self, prefix):
        """
        returns all file with a valid expiry timestamp
        """
        file_list = self.__get_file_list()
        filtered_list = []
        for file in file_list:
            file_added = False
            for tag in file[self.KEY_TAGS]:
                match = re.match("^("+prefix+")([0-9]{4})(-)([0-9]{2})", tag)
                if match: 
                    filtered_list.append(dict(filename=file["filename"], tags=file["tags"], category=file["category"], exp_year=match.groups()[1], exp_month=match.groups()[3]))
                    file_added = True
                    break
            
            if not file_added:
                for tag in file[self.KEY_CATEGORIES]:
                    match = re.match("^("+prefix+")([0-9]{4})(-)([0-9]{2})", tag)
                    if match:
                        filtered_list.append(dict(filename=file["filename"], tags=file["tags"], category=file["category"], exp_year=match.groups()[1], exp_month=match.groups()[3]))
                        break

        return filtered_list
        
    def __get_tag_dictionary(self, attribute=KEY_TAGS):
        """
        iterates through all files and creates a dictionary with tags + counter
        attribute is used to define if it returns describing tags or categorizing tags (categories)
        attribute can be KEY_TAGS|KEY_CATEGORIES
        """
        dictionary = dict()
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        for file in self.__settings.childGroups():
            self.__settings.beginGroup(file)
            tags = unicode(self.__settings.value(attribute, "").toString()).split(self.TAG_SEPARATOR)
            self.__settings.endGroup()
            for tag in tags:
                if tag in dictionary:
                    dictionary[unicode(tag)] += 1
                else:
                    dictionary[unicode(tag)] = 1
        self.__settings.endGroup()
        return dictionary

    def get_file_timestamp(self, file_name):
        """
        returns the timestamp value of a given file
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.beginGroup(file_name)
        timestamp = unicode(self.__settings.value(self.KEY_TIMESTAMP, "").toString())
        self.__settings.endGroup()        
        self.__settings.endGroup()
        return timestamp

    def get_file_hashsum(self, file_name):
        """
        returns the hashsum value of a given file
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.beginGroup(file_name)
        timestamp = unicode(self.__settings.value(self.KEY_TIMESTAMP, "").toString())
        self.__settings.endGroup()        
        self.__settings.endGroup()
        return timestamp

    def get_file_tags(self, file_name):
        """
        returns the describing tag list of a given file
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.beginGroup(file_name)
        tags = unicode(self.__settings.value(self.KEY_TAGS, "").toString()).split(self.TAG_SEPARATOR)
        self.__settings.endGroup()        
        self.__settings.endGroup()    
        return tags    
    
    def get_file_categories(self, file_name):
        """
        returns the categorizing tag list of a given file
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.beginGroup(file_name)
        categories = unicode(self.__settings.value(self.KEY_CATEGORIES, "").toString()).split(self.TAG_SEPARATOR)
        self.__settings.endGroup()        
        self.__settings.endGroup()    
        return categories
    
    def get_files(self):
        """
        returns a list of all files stored in the config file
        """
        
        files = []
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        for file in self.__settings.childGroups():
            files.append(unicode(file))
        self.__settings.endGroup()
        return files

    def set_file_path(self, file_path):
        """
        sets the internal path to the source file
        """
        self.__settings = QSettings(file_path, QSettings.IniFormat)

#    def set_store_id(self, id):
#        """
#        writes the stores id to the configuration file
#        """
#        self.__settings.beginGroup(self.GROUP_STORE_NAME)
#        self.__settings.setValue("store_id", id)
#        self.__settings.endGroup()
    
#    def get_store_id(self):
#        """
#        returns the store id of the current file to identify the store during rename
#        """
#        self.__settings.beginGroup(self.GROUP_STORE_NAME)
#        id = unicode(self.__settings.value(self.KEY_STORE_ID, "").toString())
#        self.__settings.endGroup()
#        return id
    
    def get_all_tags(self):
        """
        returns a list of all tags of the current store sorted by name asc
        """
        dictionary = self.__get_tag_dictionary()
        return sorted(dictionary.keys())
        
    def get_all_categorizing_tags(self):
        """
        returns a list of all categorizing tags of the current store sorted by name asc
        """
        dictionary = self.__get_tag_dictionary(self.KEY_CATEGORIES)
        return sorted(dictionary.keys())

    def get_recent_tags(self, no_of_tags):
        """
        returns a defined number of recently entered tags
        """
        tags = set()
        files = self.__get_file_list()
        position = 0
        while len(tags) < no_of_tags and position < len(files) and files[position] is not None:
            tags = tags.union(set(files[position]["tags"]))
            position +=1
        return sorted(tags)[:no_of_tags]

    def get_recent_files_tags(self, no_of_files):
        """
        returns all tags of a number of recently entered files
        """
        tags = set()
        files = self.__get_file_list()
        position = 0
        while position < no_of_files and position < len(files) and files[position] is not None:
            tags = tags.union(set(files[position]["tags"]))
            position +=1
        return sorted(tags)

    def get_popular_tags(self, no_of_tags):
        """
        returns a defined number of the most popular tags
        """
        dictionary = self.__get_tag_dictionary()
        list = sorted(dictionary.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        return_list = []
        for item in list[:no_of_tags]:
            return_list.append(item[0])
        return return_list

    def get_popular_categories(self, no_of_tags):
        """
        returns a defined number of the most popular categories
        """
        dictionary = self.__get_tag_dictionary(self.KEY_CATEGORIES)
        list = sorted(dictionary.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        return_list = []
        for item in list[:no_of_tags]:
            return_list.append(item[0])
        return return_list

    def get_recent_categories(self, no_of_tags):
        """
        returns a defined number of recently entered tags
        """
        tags = set()
        files = self.__get_file_list()
        position = 0
        while len(tags) < no_of_tags and position < len(files) and files[position] is not None:
            tags = tags.union(set(files[position]["category"]))
            position +=1
        return sorted(tags)[:no_of_tags]

    def set_file(self, file_name, tag_list, category_list=None, timestamp=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")):
        """
        adds a file and its tags to the config file
        or overrides the tags of an existing file
        assumption: file_name and tag_list do not have to be checked
        for lower case upper case inconsistencies 
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.beginGroup(unicode(file_name))
        self.__settings.setValue(self.KEY_TAGS, unicode(self.TAG_SEPARATOR.join(tag_list)))
        self.__settings.setValue(self.KEY_TIMESTAMP, timestamp)
        if category_list is not None:
            self.__settings.setValue(self.KEY_CATEGORIES, unicode(self.TAG_SEPARATOR.join(category_list)))
        self.__settings.endGroup()
        self.__settings.endGroup()
        self.__settings.sync()

    def __set_tags(self, file_name, tag_list, category_list=None):
        """
        resets the files tag list without updating its timestamp
        this method is called during renaming/deleting tags to avoid changing the recent tags
        """
        if not self.file_exists(file_name):
            self.set_file(file_name, tag_list, category_list)
        else:
            self.__settings.beginGroup(self.GROUP_FILES_NAME)
            self.__settings.beginGroup(file_name)
            self.__settings.setValue(self.KEY_TAGS, self.TAG_SEPARATOR.join(tag_list))
            if category_list is not None:
                self.__settings.setValue(self.KEY_CATEGORIES, self.TAG_SEPARATOR.join(category_list))
            self.__settings.endGroup()
            self.__settings.endGroup()

#    def rename_file(self, old_file_name, new_file_name):
#        """
#        renames an existing file
#        """
#        self.__settings.beginGroup(self .GROUP_FILES_NAME)
#        self.__settings.beginGroup(old_file_name)            
#        tags = unicode(self.__settings.value(self.KEY_TAGS, "").toString()).split(self.TAG_SEPARATOR)
#        timestamp = unicode(self.__settings.value(self.KEY_TIMESTAMP, "").toString())
#        self.__settings.endGroup()
#        self.__settings.remove(old_file_name)
#        self.__settings.endGroup()
#        self.set_file(new_file_name, tags, timestamp)
        
    def remove_file(self, file_name):
        """
        removes a given file from the config file
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        self.__settings.remove(file_name)
        self.__settings.endGroup()
        self.__settings.sync()
    
    def file_exists(self, file_name):
        """ 
        checks if a file is already existing in the section "files"
        """
        self.__settings.beginGroup(self.GROUP_FILES_NAME)
        files = self.__settings.childGroups()
        self.__settings.endGroup()
        for name in files:
            name = unicode(name)
            if name == file_name:
                return True
        return False
    
#    def rename_tag(self, old_tag_name, new_tag_name):
#        """
#        renames all tags in the store
#        """
#        files = self.__get_file_list()
#        for file in files:
#            tags = file["tags"]
#            if old_tag_name in tags:
#                tags.remove(old_tag_name)
#                tags.append(new_tag_name)
#                self.__set_tags(file["filename"], tags)

    def sync_settings(self):
        """
        flushes all pending changes to disk and reloads the file in case it has been changed by another application, i.e. sync app
        """
        self.__settings.sync()

    def remove_tag(self, tag_name):
        """
        removes the given tag from all file entries
        """
        files = self.__get_file_list()
        for file in files:
            describing_tags = file["tags"]
            categorising_tags = file["category"]
            if tag_name in describing_tags or tag_name in categorising_tags:
                if tag_name in describing_tags:
                    describing_tags.remove(tag_name)
                if tag_name in categorising_tags:
                    categorising_tags.remove(tag_name)
                if len(describing_tags) >= 1 or len(categorising_tags) >= 1:
                    self.__set_tags(file["filename"], describing_tags, categorising_tags)
                else:
                    #delete file entry if there is no tag left
                    self.remove_file(file["filename"])

    def get_tag_dict(self, attribute=KEY_TAGS):
        """
        ADD from Georg
        TODO: Change function-name
        """
        return self.__get_tag_dictionary(attribute)
## end