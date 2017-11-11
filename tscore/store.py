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

#import time #for performance tests only
from time import time
from PyQt4 import QtCore
from tscore.configwrapper import ConfigWrapper
from tscore.enums import EFileType, EFileEvent, EOS, EConflictType, \
    ECategorySetting
from tscore.exceptions import StoreInitError, StoreTaggingError, \
    NameInConflictException, InodeShortageException
from tscore.loghelper import LogHelper
from tscore.pendingchanges import PendingChanges
from tscore.specialcharhelper import SpecialCharHelper
from tscore.tagwrapper import TagWrapper
from tscore.tsconstants import TsConstants
from tscore.tsrestrictions import TsRestrictions
from tscore.vocabularywrapper import VocabularyWrapper
from tscore.recommender import Recommender
from tscore.tagcloud import TagCloud
from tsos.filesystem import FileSystemWrapper
from pidhelper import PidHelper
import datetime
import logging.handlers
import os
import re
import sys
#from tscore.tsconstants import TsConstants

class Store(QtCore.QObject):

    __pyqtSignals__ = ("removed(PyQt_PyObject)",
                       "renamed(PyQt_PyObject, QString)",
                       "file_renamed(PyQt_PyObject, QString, QString)",
                       "file_removed(PyQt_PyObject, QString)",
                       "pending_operations_changed(PyQt_PyObject)")

    def __init__(self, id, path, config_file_name, tags_file, vocabulary_file, navigation_dir_list, storage_dir_list, describing_nav_dir_list, categorising_nav_dir_list, expiry_dir_list, expiry_prefix):
        """
        constructor
        """
        QtCore.QObject.__init__(self)

        #self.__log = logging.getLogger("TagStoreLogger")#None##FIXXME
        self.__log = None

        self.__file_system = FileSystemWrapper(self.__log)
        self.__watcher = QtCore.QFileSystemWatcher(self)
        self.__watcher.connect(self.__watcher,QtCore.SIGNAL("directoryChanged(QString)"), self.__directory_changed)
        self.__tag_wrapper = None
        self.__sync_tag_wrapper = None
        self.__store_config_wrapper = None
        self.__pending_changes = PendingChanges()
        
        self.__sync_tags_file_name = TsConstants.DEFAULT_STORE_SYNC_TAGS_FILENAME
        
        self.__tagline_config = None
        self.__paths_to_maintain = []
        
        self.__id = unicode(id)
        self.__path = unicode(path)
        self.__config_file_name = unicode(config_file_name)
        self.__tags_file_name = unicode(tags_file)
        self.__vocabulary_file_name = unicode(vocabulary_file)
        
        self.__storage_dir_list = storage_dir_list
        self.__describing_nav_dir_list = describing_nav_dir_list
        self.__categorising_nav_dir_list = categorising_nav_dir_list
        self.__expiry_dir_list = expiry_dir_list
        self.__expiry_prefix = unicode(expiry_prefix)
        
        self.__storage_dir_name = self.trUtf8("storage")
        self.__navigation_dir_name = self.trUtf8("navigation")
        self.__describing_nav_dir_name = self.trUtf8("descriptions")
        self.__categorising_nav_dir_name = self.trUtf8("categories")
        self.__expiry_dir_name = self.trUtf8("expired_items")
        #self.__parent_path = None
        #self.__name = None
        #self.__config_path = None
        #self.__watcher_path = None
        #self.__describing_nav_path = None
        #self.__config_path = self.__path + "/" + self.__config_file_name
        #self.__watcher_path = self.__path + "/" + self.__storage_dir_name
        #self.__describing_nav_path = self.__path + "/" + self.__describing_nav_dir_name

        self.__create_wrappers()
        
        if self.__path.find(":/") == -1:
            self.__path = self.__path.replace(":", ":/")
        self.__name = unicode(self.__path.split("/")[-1])
        self.__parent_path = unicode(self.__path[:len(self.__path)-len(self.__name)-1])
        
        self.__tagcloud = TagCloud()
        self.__recommender = Recommender(self.get_store_path())
        
    def __create_wrappers(self):
        if self.__file_system.path_exists(self.__path + "/" + self.__tags_file_name):
            self.__tag_wrapper = TagWrapper(self.__path + "/" + self.__tags_file_name)
        if self.__file_system.path_exists(self.__path + "/" + self.__config_file_name):
            self.__store_config_wrapper = ConfigWrapper(self.__path + "/" + self.__config_file_name)

    def init(self):
        """
        init is called after event listeners were added to the store instance
        """
        ## throw exception if store directory does not exist
        if not self.__file_system.path_exists(self.__path):
            ## look for renamed or removed store folder
            self.__handle_renamed_removed_store()
        if not self.__file_system.path_exists(self.__path):
            #print self.__path
            raise StoreInitError, self.trUtf8("The specified store directory does not exist! %s" % self.__path)
            return
        
        
        ## look for store/describing_nav/categorising_nav/expire directories names (all languages) if they do not exist
        if not self.__file_system.path_exists(self.__path + "/" + self.__storage_dir_name):
            for dir in self.__storage_dir_list:
                if self.__file_system.path_exists(self.__path + "/" + dir):
                    self.__storage_dir_name = unicode(dir)
        if not self.__file_system.path_exists(self.__path + "/" + self.__describing_nav_dir_name):
            for dir in self.__describing_nav_dir_list:
                if self.__file_system.path_exists(self.__path + "/" + dir):
                    self.__describing_nav_dir_name = unicode(dir)
        if not self.__file_system.path_exists(self.__path + "/" + self.__categorising_nav_dir_name):
            for dir in self.__categorising_nav_dir_list:
                if self.__file_system.path_exists(self.__path + "/" + dir):
                    self.__categorising_nav_dir_name = unicode(dir)
        if not self.__file_system.path_exists(self.__path + "/" + self.__expiry_dir_name):
            for dir in self.__expiry_dir_list:
                if self.__file_system.path_exists(self.__path + "/" + dir):
                    self.__expiry_dir_name = unicode(dir)
        if not self.__file_system.path_exists(self.__path + "/" + self.__navigation_dir_name):
            for dir in self.__expiry_dir_list:
                if self.__file_system.path_exists(self.__path + "/" + dir):
                    self.__navigation_dir_name = unicode(dir)
        
        
        
        ## built stores directories and config file if they currently not exist (new store)
        self.__file_system.create_dir(self.__path + "/" + self.__storage_dir_name)
        self.__file_system.create_dir(self.__path + "/" + self.__expiry_dir_name)
        self.__file_system.create_dir(self.__path + "/" + self.__config_file_name.split("/")[0])
        self.__file_system.create_dir(self.__path + "/" + self.__navigation_dir_name)
        ## create config/vocabulary files if they don't exist
        if not self.__file_system.path_exists(self.__path + "/" + self.__config_file_name):
            ConfigWrapper.create_store_config_file(self.__path + "/" + self.__config_file_name)
            ## now create a new config_wrapper instance
            self.__store_config_wrapper = ConfigWrapper(self.__path + "/" + self.__config_file_name)
        if not self.__file_system.path_exists(self.__path + "/" + self.__tags_file_name):
            TagWrapper.create_tags_file(self.__path + "/" + self.__tags_file_name)
            ## now create a new tag_wrapper instance
            self.__tag_wrapper = TagWrapper(self.__path + "/" + self.__tags_file_name)
        if not self.__file_system.path_exists(self.__path + "/" + self.__vocabulary_file_name):
            self.__vocabulary_wrapper = VocabularyWrapper.create_vocabulary_file(self.__path + "/" + self.__vocabulary_file_name)


        ## 0 ... show just the describing tagline -> create the NAVIGATION dir 
        ## 3 ... show just the categorizing tagline - only restricted vocabulary is allowed -> create the CATEGORIES dir
        ## ELSE: two taglines with dirs: CATEGORIES/DESCRIPTIONS
        self.__tagline_config = self.__store_config_wrapper.get_show_category_line()
        
        # clear the old list (if there is already one)
        self.__paths_to_maintain = []
        
        if self.__tagline_config == 0:
            #self.__file_system.create_dir(self.__path + "/" + self.__navigation_dir_name)
            self.__paths_to_maintain.append(self.__path + "/" + self.__navigation_dir_name)
        elif self.__tagline_config == 3:
            #self.__file_system.create_dir(self.__path + "/" + self.__categorising_nav_dir_name)
            self.__paths_to_maintain.append(self.__path + "/" + self.__categorising_nav_dir_name)
        else:
            #self.__file_system.create_dir(self.__path + "/" + self.__categorising_nav_dir_name)
            self.__paths_to_maintain.append(self.__path + "/" + self.__categorising_nav_dir_name)
            #self.__file_system.create_dir(self.__path + "/" + self.__describing_nav_dir_name)
            self.__paths_to_maintain.append(self.__path + "/" + self.__describing_nav_dir_name)

        for path in self.__paths_to_maintain:
            self.__file_system.create_dir(path)

        self.__init_store()

    def init_sync_log(self, target_store_name):
        """
        initializes the sync log
        """
        # construct sync tags file path
        target_store_name = target_store_name.replace(":", "")
        
        self.__sync_tags_file_path = self.__path + "/" + TsConstants.DEFAULT_STORE_CONFIG_DIR + "/" + target_store_name + self.__sync_tags_file_name
        
        self.__log.info("init sync log path:%s" % self.__sync_tags_file_path)
        if not self.__file_system.path_exists(self.__sync_tags_file_path):
            # create default sync tags file
            TagWrapper.create_tags_file(self.__sync_tags_file_path)
            
        ## now create a new sync tag_wrapper instance
        self.__sync_tag_wrapper = TagWrapper(self.__sync_tags_file_path)

    def sync_item_exists(self, item_name):
        """
        checks an item exists in the sync log
        """
        return self.__sync_tag_wrapper.file_exists(item_name)

    def get_sync_items(self):
        """
        returns a list of all item names in the sync log 
        """
        return self.__sync_tag_wrapper.get_files()

    def get_sync_file_timestamp(self, file_name):
        """
        returns the timestamp value in the sync log
        """
        return self.__sync_tag_wrapper.get_file_timestamp(file_name)
        
    def get_describing_sync_tags_for_item(self, item_name):
        """
        returns all describing tags associated with the given item in the sync log
        """
        return self.__sync_tag_wrapper.get_file_tags(item_name)
        
    def get_categorizing_sync_tags_for_item(self, item_name):
        """
        returns all categorizing tags associated with the given item in the sync log
        """
        return self.__sync_tag_wrapper.get_file_categories(item_name)

        
    def __init_store(self):
        """
        initializes the store paths, config reader, file system watcher without instantiation of a new object
        """
        self.__name = self.__path.split("/")[-1]
        self.__parent_path = self.__path[:len(self.__path)-len(self.__name)]
        self.__tags_file_path = self.__path + "/" + self.__tags_file_name
        self.__sync_tags_file_path = self.__path + "/" + TsConstants.DEFAULT_STORE_CONFIG_DIR + "/" + self.__sync_tags_file_name
        self.__config_path = self.__path + "/" + self.__config_file_name
        self.__vocabulary_path = self.__path + "/" + self.__vocabulary_file_name #TsConstants.STORE_CONFIG_DIR + "/" + TsConstants.STORE_VOCABULARY_FILENAME
        self.__watcher_path = self.__path + "/" + self.__storage_dir_name
        self.__navigation_path = self.__path + "/" + self.__navigation_dir_name
        self.__describing_nav_path = self.__path + "/" + self.__describing_nav_dir_name
        self.__categorising_nav_path = self.__path + "/" + self.__categorising_nav_dir_name
        config_file_name = unicode(self.__config_path.split("/")[-1])
        self.__temp_progress_path = unicode(self.__config_path[:len(self.__config_path)-len(config_file_name)-1])
        
        self.__tag_wrapper = TagWrapper(self.__tags_file_path)
        self.__sync_tag_wrapper = TagWrapper(self.__sync_tags_file_path)
        
        ## update store id to avoid inconsistency
        config_wrapper = ConfigWrapper(self.__path + "/" + self.__config_file_name)#self.__tags_file_name)
        config_wrapper.set_store_id(self.__id)
        self.__vocabulary_wrapper = VocabularyWrapper(self.__vocabulary_path)
        self.connect(self.__vocabulary_wrapper, QtCore.SIGNAL("changed"), self.__handle_vocabulary_changed)
        self.__store_config_wrapper = ConfigWrapper(self.__config_path)
        self.connect(self.__store_config_wrapper, QtCore.SIGNAL("changed()"), self.__handle_store_config_changed)
        
        if len(self.__name) == 0:
            self.__name = self.__path[:self.__path.rfind("/")]
        
        if not self.__is_android_store():
            # no activity is required on android tag stores
            self.__watcher.addPath(self.__parent_path)
            self.__watcher.addPath(self.__watcher_path)
        
        ## all necessary files and dirs should have been created now - so init the logger
        self.__log = LogHelper.get_store_logger(self.__path, logging.INFO) 
        self.__log.info("parent_path: '%s'" % self.__name)

        ## handle offline changes
        self.__handle_unfinished_operation()
        self.__handle_file_expiry()
        self.__handle_file_changes(self.__watcher_path)
        
    
    def __handle_store_config_changed(self):
        self.emit(QtCore.SIGNAL("store_config_changed"), self)

    def __handle_vocabulary_changed(self):
        self.emit(QtCore.SIGNAL("vocabulary_changed"), self)
        
#    def handle_offline_changes(self):
#        """
#        called after store and event-handler are created to handle (offline) modifications
#        """
#        self.__handle_file_changes(self.__watcher_path)

    def add_ignored_extensions(self, ignored_list):
        self.__file_system.add_ignored_extensions(ignored_list)

    def set_path(self, path, config_file=None, tags_file=None, vocabulary_file=None):
        """
        resets the stores path and config path (called if application config changes)
        """
        if self.__path == unicode(path) and (config_file is None or self.__config_file_name == unicode(config_file)):
            exit
        ## update changes
        self.__watcher.removePaths([self.__parent_path, self.__watcher_path])
        self.__path = unicode(path)
        if config_file is not None:
            self.__config_file_name = unicode(config_file)
        if tags_file is not None:
            self.__tags_file_name = unicode(tags_file)
        if vocabulary_file is not None:
            self.__vocabulary_file_name = unicode(vocabulary_file)
        self.__init_store()
        
    def __handle_renamed_removed_store(self):
        """
        searches the parents directory for renamed or removed stores
        """
        #print self.__parent_path
        #print self.__config_file_name
        #print ".."
        config_paths = self.__file_system.find_files(self.__parent_path, self.__config_file_name)
        #print "config paths: " + ",".join(config_paths)
        new_name = ""
        for path in config_paths:
            reader = ConfigWrapper(path)
            #print "found: " + path
            #print self.__id + ", " + reader.get_store_id()
            
            if self.__id == reader.get_store_id():
                new_name = path.split("/")[-3]
                #print "new name: " + new_name

        if new_name == "":      ## removed
            ## delete describing_nav directors
            #self.remove()
            self.emit(QtCore.SIGNAL("removed(PyQt_PyObject)"), self)
        else:                   ## renamed
            self.__path = self.__parent_path + "/" + new_name
            self.__navigation_path = self.__path + "/" + self.__navigation_dir_name
            self.__describing_nav_path = self.__path + "/" + self.__describing_nav_dir_name
            self.__categorising_nav_path = self.__path + "/" + self.__categorising_nav_dir_name
            ## update all links in windows: absolute links only
            #if self.__file_system.get_os() == EOS.Windows:
                #print "rebuild"
                #self.rebuild()
            #print "emit: " + self.__parent_path + "/" + new_name
            self.emit(QtCore.SIGNAL("renamed(PyQt_PyObject, QString)"), self, self.__parent_path + "/" + new_name)
    
    def __directory_changed(self, path):
        """
        handles directory changes of the stores directory and its parent directory 
        and finds out if the store itself was renamed/removed
        """
        if path == self.__parent_path:
            if not self.__file_system.path_exists(self.__path):
                ## store itself was changed: renamed, moved or deleted
                self.__watcher.removePath(self.__parent_path)
                self.__handle_renamed_removed_store()
        else:
            ## files or directories in the store directory have been changed
            self.__handle_file_changes(self.__watcher_path)

    def __handle_unfinished_operation(self):
        """
        looks for a opInProgress.tmp file to find out if the last operation was finished correctly
        this file is created before an operation starts and deleted afterwards
        """
        if self.__file_system.path_exists(self.__temp_progress_path + "/" + "opInProgress.tmp"):
            self.rebuild()
            
    def __create_inprogress_file(self):
        """
        creates a temporary file during an operation in progress to handle operation interruption
        """
        self.__file_system.create_file(self.__temp_progress_path + "/" + "opInProgress.tmp")

    def __remove_inprogress_file(self):
        """
        removes the temporary file after the operation succeeded
        """
        self.__file_system.remove_file(self.__temp_progress_path + "/" + "opInProgress.tmp")
        
    def __handle_file_expiry(self):
        """
        looks for expired items and moves & renames them to filename including tags in the expiry_directory
        """
        expiry_date_files = self.__tag_wrapper.get_files_with_expiry_tags(self.__expiry_prefix)
        now = datetime.datetime.now()
        for file in expiry_date_files:
            file_extension = "." + file["filename"].split(".")[-1]
            file_name = file["filename"]
            file_name = file_name[:len(file_name)-len(file_extension)]
            if int(file["exp_year"]) < now.year or (int(file["exp_year"]) == now.year and int(file["exp_month"]) < now.month):
                new_filename = file_name + " - " + "; ".join(file["category"]) + " - " + "; ".join(file["tags"]) + file_extension
                self.__file_system.rename_file(self.__watcher_path + "/" + file["filename"], self.__path + "/" + self.__expiry_dir_name + "/" + new_filename)
    
    def __get_lockfile_path(self):
        return self.__path + "/" + self.__storage_dir_name + "/" + TsConstants.DEFAULT_SYNCHRONIZATION_LOCKFILE_NAME
    
                    
    def __is_sync_active(self):
        """
        returns true when the sync is active
        """
  
        # get lock path
        path = self.__get_lockfile_path();
  
        # check if path exists        
        result = self.__file_system.path_exists(path)
        if result == False:
            return result
        
        
        # read pid from file
        old_pid = None 
        pid_file = open(path, "r")
        
        for line in pid_file.readlines():
            old_pid = line

        # close pid file
        pid_file.close()
        
        if old_pid is None or old_pid == "":
            # empty file remove
            self.__file_system.remove_file(path)
            return False
        
        # check if the pid still exists
        return PidHelper.pid_exists(old_pid)

    def __handle_file_changes(self, path):
        """
        handles the stores file and dir changes to find out if a file/directory was added, renamed, removed
        """
        if(path == self.__get_lockfile_path()):
            return
        
        ## if there is a synchronize procedure running - just do nothing
        #if(self.__is_synchronize_in_progress()):
        #    print "recognized a new file - but this must be from the sync-process"
        #    return
        
        if self.__is_sync_active():
            self.__log.info("__handle_file_changes: sync is active")
            return

        if self.__is_android_store():
            # no notifications on android stores
            self.__log.info("__handle_file_changes: no notifications on android stores")
            return
        
        # sync any changes if the´sync was active
        self.__tag_wrapper.sync_settings()
        
        ## this method does not handle the renaming or deletion of the store directory itself (only childs)
        existing_files = set(self.__file_system.get_files(path))
        existing_dirs = set(self.__file_system.get_directories(path))
        config_files = set(self.__tag_wrapper.get_files())
        captured_added_files = set(self.__pending_changes.get_added_names())
        captured_removed_files = set(self.__pending_changes.get_removed_names())

        data_files = (config_files | captured_added_files) - captured_removed_files 
        added = list((existing_files | existing_dirs) - data_files)
        removed = list(data_files - (existing_files | existing_dirs))
    
        #names = self.__pending_changes.get_added_names()
        #for name in names:
        #    self.__log.info(name)
    
        if len(added) == 1 and len(removed) == 1:
            self.__pending_changes.register(removed[0], self.__get_type(removed[0]), EFileEvent.REMOVED_OR_RENAMED)
            self.__pending_changes.register(added[0], self.__get_type(added[0]), EFileEvent.ADDED_OR_RENAMED)
            self.emit(QtCore.SIGNAL("file_renamed(PyQt_PyObject, QString, QString)"), self, removed[0], added[0])
        else:
            if len(removed) > 0:
                if len(added) == 0:
                    for item in removed:
                        self.__pending_changes.register(item, self.__get_type(item), EFileEvent.REMOVED)
                        self.emit(QtCore.SIGNAL("file_removed(PyQt_PyObject, QString)"), self, item)
                else:
                    for item in removed:
                        self.__pending_changes.register(item, self.__get_type(item), EFileEvent.REMOVED_OR_RENAMED)
                        self.emit(QtCore.SIGNAL("pending_operations_changed(PyQt_PyObject)"), self)
            if len(added) > 0:
                if len(removed) == 0:
                    for item in added:
                        self.__pending_changes.register(item, self.__get_type(item), EFileEvent.ADDED)
                        self.emit(QtCore.SIGNAL("pending_operations_changed(PyQt_PyObject)"), self)
                else:
                    for item in added:
                        self.__pending_changes.register(item, self.__get_type(item), EFileEvent.ADDED_OR_RENAMED)
                        self.emit(QtCore.SIGNAL("pending_operations_changed(PyQt_PyObject)"), self)                
        
    def __get_type(self, item):
        """
        returns the items type to be stored in pending_changes
        """
        if self.__file_system.is_directory(self.__watcher_path + "/" + unicode(item)):
            return EFileType.DIRECTORY
        return EFileType.FILE
    
    def get_name(self):
        """
        returns the stores name
        """
        return self.__name
    
    def get_id(self):
        """
        returns the stores id
        """
        return unicode(self.__id)
    def get_max_tags(self):
        return self.__store_config_wrapper.get_max_tags()
    def get_tag_separator(self):
        return self.__store_config_wrapper.get_tag_seperator()

    def get_store_path(self):
        """
        returns the root of the tagstore
        """
        return self.__path
    
    def get_pending_changes(self):
        """
        returns the stores unhandled changes 
        """
        return self.__pending_changes
    
    def move(self, new_path):
        """
        moves the whole path to the specified place 
        """
        ## first of all move the physical data to the new location 
        self.__file_system.move(self.__path, new_path)
        ## re-set the path variable
        self.__path = new_path
        ## initialize to update all necessary membervariables
        self.init()
        ## rebuild the whole store structure to make sure all links are updated
        self.rebuild()

    def remove(self):
        """
        removes all directories and links in the stores describing_nav path
        """
        for path in self.__paths_to_maintain:
            self.__file_system.delete_dir_content(path)
        
        self.emit(QtCore.SIGNAL("store_delete_end"), self.__id)
    
    def rebuild(self):
        """
        removes and rebuilds all links in the describing_nav path
        """
        self.__create_inprogress_file()
        self.__log.info("START rebuild progress")
        self.remove()
        for file in self.__tag_wrapper.get_files():
            describing_tag_list = self.__tag_wrapper.get_file_tags(file)
            categorising_tag_list = self.__tag_wrapper.get_file_categories(file)
            self.add_item_with_tags(file, describing_tag_list, categorising_tag_list)
        self.__remove_inprogress_file()
        self.emit(QtCore.SIGNAL("store_rebuild_end"), self.__name)
        self.__log.info("rebuild progress END")
    
    def rename_file(self, old_file_name, new_file_name):
        """
        renames an existing file: links and config settings 
        """
        self.__log.info("renaming: %s to %s" % (old_file_name, new_file_name))
        self.__create_inprogress_file()
        if self.__tag_wrapper.file_exists(old_file_name):
            describing_tag_list = self.__tag_wrapper.get_file_tags(old_file_name)
            categorising_tag_list = self.__tag_wrapper.get_file_categories(old_file_name)
            self.remove_file(old_file_name)
            self.add_item_with_tags(new_file_name, describing_tag_list, categorising_tag_list)

            self.__pending_changes.remove(old_file_name)
            self.__pending_changes.remove(new_file_name)
        else:
            self.__pending_changes.edit(old_file_name, new_file_name)
            self.emit(QtCore.SIGNAL("pending_operations_changed(PyQt_PyObject)"), self)
        self.__remove_inprogress_file()
        
    def remove_file(self, file_name):
        """
        removes a file: links and config settings 
        """
        self.__log.info("remove file: %s" % file_name)
        self.__create_inprogress_file()
        self.__pending_changes.remove(file_name)
        if self.__tag_wrapper.file_exists(file_name):
            describing_tag_list = self.__tag_wrapper.get_file_tags(file_name)
            categorising_tag_list = self.__tag_wrapper.get_file_categories(file_name)
            for path in self.__paths_to_maintain:
                if path == self.__describing_nav_path:
                    self.__delete_links(file_name, describing_tag_list, self.__describing_nav_path)
                if path == self.__categorising_nav_path:
                    self.__delete_links(file_name, categorising_tag_list, self.__categorising_nav_path)
                if path == self.__navigation_path:
                    #changed fron cat -> do desc tags because there are just descrbing tags when
                    #there is just the "navigation" folder
                    #self.__delete_links(file_name, categorising_tag_list, self.__navigation_path)
                    self.__delete_links(file_name, describing_tag_list, self.__navigation_path)
            self.__tag_wrapper.remove_file(file_name)
        else:
            self.emit(QtCore.SIGNAL("pending_operations_changed(PyQt_PyObject)"), self)
        self.__remove_inprogress_file()
        
    def __delete_links(self, file_name, tag_list, current_path):
        """
        deletes all links to the given file
        """
        self.__create_inprogress_file()
        for tag in tag_list:
            recursive_list = [] + tag_list
            recursive_list.remove(tag)
            self.__delete_links(file_name, recursive_list, current_path + "/" + tag)
            self.__file_system.remove_link(current_path + "/" + tag + "/" + file_name)
        self.__remove_inprogress_file()
    
    def change_expiry_prefix(self, new_prefix):
        """
        changes the expiry prefix and all existing expiry tags
        """
        ## handle changes only
        if self.__expiry_prefix == new_prefix:  
            return

        self.__log.info("changing the expiry prefix from %s to %s" % (self.__expiry_prefix, new_prefix))
        
        self.__create_inprogress_file()
        expiry_date_files = self.__tag_wrapper.get_files_with_expiry_tags(self.__expiry_prefix)
        
        for file in expiry_date_files:
            for tag in file["tags"]:
                match = re.match("^(" + self.__expiry_prefix + ")([0-9]{4})(-)([0-9]{2})", tag)
                if match:
                    self.rename_tag(tag, tag.replace(self.__expiry_prefix, new_prefix))
            
            for tag in file["category"]:
                match = re.match("^(" + self.__expiry_prefix + ")([0-9]{4})(-)([0-9]{2})", tag)
                if match:
                    self.rename_tag(tag, tag.replace(self.__expiry_prefix, new_prefix))

        ## set new prefix
        self.__expiry_prefix = new_prefix
        self.__remove_inprogress_file()
    
    def get_items(self):
        """
        returns a list of all item names in the store 
        """
        return self.__tag_wrapper.get_files()
    
    def get_tags(self):
        """
        returns a list of all describing  tags
        """
        return self.__tag_wrapper.get_all_tags()

    def get_categorizing_tags(self):
        """
        returns a list of categorizing all tags
        """
        return self.__tag_wrapper.get_all_categorizing_tags()

    def get_recent_tags(self, number):
        """
        returns a given number of recently entered tags
        """
        return self.__tag_wrapper.get_recent_tags(number)
    
    def get_popular_tags(self, number):
        """
        returns a given number of the most popular tags
        """
        return self.__tag_wrapper.get_popular_tags(number)

    def get_popular_categories(self, number):
        """
        returns a given number of the most popular tags
        """
        return self.__tag_wrapper.get_popular_categories(number)

    def get_recent_categories(self, number):
        """
        returns a given number of recently entered tags
        """
        return self.__tag_wrapper.get_recent_categories(number)

    def get_describing_tags_for_item(self, item_name):
        """
        returns all describing tags associated with the given item
        """
        return self.__tag_wrapper.get_file_tags(item_name)
        
    def get_categorizing_tags_for_item(self, item_name):
        """
        returns all categorizing tags associated with the given item
        """
        return self.__tag_wrapper.get_file_categories(item_name)
        

    def get_show_category_line(self):
        return self.__store_config_wrapper.get_show_category_line()

    def is_controlled_vocabulary(self):
        """
        return True if there is just controlled vocabulary allowed in the second tagline 
        """
        setting = self.__store_config_wrapper.get_show_category_line()
        if setting == ECategorySetting.ENABLED_ONLY_PERSONAL or setting == ECategorySetting.ENABLED_SINGLE_CONTROLLED_TAGLINE:
            return True
        return False
    
    def get_datestamp_format(self):
        return self.__store_config_wrapper.get_datestamp_format()

    def get_datestamp_hidden(self):
        return self.__store_config_wrapper.get_datestamp_hidden()
    
    def get_category_mandatory(self):
        return self.__store_config_wrapper.get_category_mandatory()

    def __name_in_conflict(self, file_name, describing_tag_list, categorising_tag_list):
        """
        checks for conflicts and returns the result as boolean
        """
        
        ## both lists could be none if there is just one tagline
        if(categorising_tag_list is None):
            categorising_tag_list = []
        if(describing_tag_list is None):
            describing_tag_list = []
        
        #TODO: extend functionality: have a look at #18 (Wiki)
        existing_files = self.__tag_wrapper.get_files()
        existing_tags = self.__tag_wrapper.get_all_tags()
        tag_list = list(set(describing_tag_list) | set(categorising_tag_list))

        file_name = unicode(file_name)        

        if file_name in existing_tags:
            return [file_name, EConflictType.FILE]
        for tag in tag_list:
            if tag in existing_files:
                return [tag, EConflictType.TAG]
        return ["", None]
    
    def add_item_list_with_tags(self, file_name_list, describing_tag_list, categorising_tag_list=None, silent=False):
        for item in file_name_list:
            self.add_item_with_tags(item, describing_tag_list, categorising_tag_list, silent)
        
    def add_item_with_tags(self, file_name, describing_tag_list, categorising_tag_list=None, silent=False):
        """
        adds tags to the given file, resets existing tags
        """
        #TODO: if file_name already in config, delete missing tags and recreate whole link structure
        #existing tags will not be recreated in windows-> linux, osx???
         
        #self.__log.info("add item with tags to navigation: itemname: %s" % file_name)
        #self.__log.info("describing tags: %s" % describing_tag_list)
        #self.__log.info("categorizing tags: %s" % categorising_tag_list)
        ## throw error if inodes run short
        if self.__file_system.inode_shortage(self.__config_path):
            self.__log.error("inode threshold has exceeded")
            raise InodeShortageException(TsRestrictions.INODE_THRESHOLD)
        ## throw error if item-names and tag-names (new and existing) are in conflict
        conflict = self.__name_in_conflict(file_name, describing_tag_list, categorising_tag_list)
        if conflict[0] != "":
            self.__log.error("name_in_conflict_error: %s, %s" % (conflict[0], conflict[1]))
            raise NameInConflictException(conflict[0], conflict[1])
        ## ignore multiple tags
        describing_tags = list(set(describing_tag_list))
        categorising_tags = []
        if categorising_tag_list is not None:
            categorising_tags = list(set(categorising_tag_list))


        #try:
        self.__create_inprogress_file()
        
        #print "-----"
        #print self.__describing_nav_path
        #print self.__categorising_nav_path
        #print self.__navigation_path
        # is it not an android store

        start = time()#time.clock() ## performance measure
        self.__log.info("starting to create TagTrees for item: %s" % file_name) ## FIXXME: remove this line if time measurement works

        if not self.__is_android_store():
            for path in self.__paths_to_maintain:
                if path == self.__describing_nav_path:
                    self.__build_store_navigation(file_name, describing_tags, self.__describing_nav_path)
                elif path == self.__categorising_nav_path:
                    self.__build_store_navigation(file_name, categorising_tags, self.__categorising_nav_path)
                elif path == self.__navigation_path:
                    self.__build_store_navigation(file_name, describing_tags, self.__navigation_path)
        #except:
        #    raise Exception, self.trUtf8("An error occurred during building the navigation path(s) and links!")
        #try:
        
        self.__tag_wrapper.set_file(file_name, describing_tags, categorising_tags)

        self.__pending_changes.remove(file_name)
        self.__remove_inprogress_file()
        #except:
        #    raise Exception, self.trUtf8("An error occurred during saving file and tags to configuration file!")
        ## scalability test
        ## print "number of tags: " + str(len(tags)) + ", time: " + str(time.clock()-start)
        self.__log.info("tagged item " + file_name + \
                            ", # descr tags: " + str(len(describing_tags)) + \
                            ", # categ tags: " + str(len(categorising_tags)) + \
                            "; %f" % (time()-start) )  ## performance measure
        ## CAUTION: time.clock() measures something weird, but not actual time
        
    def __build_store_navigation(self, link_name, tag_list, current_path):
        """
        builds the whole directory and link-structure (describing & categorising nav path) inside a stores filesystem
        """
        link_source = self.__watcher_path + "/" + link_name

        for tag in tag_list:
            self.__file_system.create_dir(current_path + "/" + tag)
            self.__file_system.create_link(link_source, current_path + "/" + tag + "/" + link_name)
            recursive_list = [] + tag_list
            recursive_list.remove(tag)
            self.__build_store_navigation(link_name, recursive_list, current_path + "/" + tag)
    
    def rename_tag(self, old_tag_name, new_tag_name):
        """
        renames a tag inside the store 
        """
        self.__create_inprogress_file()
        ##get all affected files per tag
        files = self.__tag_wrapper.get_files_with_tag(old_tag_name)
        self.delete_tags([old_tag_name])
        for file in files:
            if old_tag_name in file["tags"]:
                file["tags"].append(new_tag_name)
                file["tags"].remove(old_tag_name)
            if old_tag_name in file["category"]:
                file["category"].append(new_tag_name)
                file["category"].remove(old_tag_name)
            self.add_item_with_tags(file["filename"], file["tags"], file["category"]) 
        self.__remove_inprogress_file()
    
    def item_exists(self, item_name):
        """
        returns True or False if the item is entered in the store.tgs
        """
        return self.__tag_wrapper.file_exists(item_name)
    
    def delete_tags(self, tag_list):
        """
        delete tags inside the store
        """
        self.__create_inprogress_file()
        for tag_name in tag_list:
            ##get all affected files per tag
            files = self.__tag_wrapper.get_files_with_tag(tag_name)
            for file in files:
                for path in self.__paths_to_maintain:
                    if path == self.__describing_nav_path:
                        self.__delete_tag_folders(tag_name, file["tags"], self.__describing_nav_path)
                    if path == self.__categorising_nav_path:
                        self.__delete_tag_folders(tag_name, file["category"], self.__categorising_nav_path)
                    if path == self.__navigation_path:
                        self.__delete_tag_folders(tag_name, file["tags"], self.__navigation_path)
            ##remove tag from config file
            self.__tag_wrapper.remove_tag(tag_name)
        self.__remove_inprogress_file()
        
    def __delete_tag_folders(self, affected_tag, tag_list, current_path):
        """
        recursive function to delete the tag directories within the describing_nav structure
        """
        if affected_tag not in tag_list:
            return
        self.__file_system.delete_dir(current_path + "/" + affected_tag)
        diff_list = [] + tag_list
        diff_list.remove(affected_tag)
        for tag in diff_list:
            recursive_list = [] + tag_list
            recursive_list.remove(tag)
            self.__delete_tag_folders(affected_tag, recursive_list, current_path + "/" + tag)
        
    def get_controlled_vocabulary(self):
        """
        returns a predefined list of allowed strings (controlled vocabulary) to be used for categorizing
        """
        return self.__vocabulary_wrapper.get_vocabulary()
    
    def set_controlled_vocabulary(self, vocabulary_set):
        self.__vocabulary_wrapper.set_vocabulary(vocabulary_set)

    def get_storage_directory(self):
        """
        returns the path of the storage directory where the items are stored
        """        
        return self.__watcher_path
    
    def get_android_root_directory(self):
        """
        returns the root directory of the android removable storage drive
        """
        res = self.__path[:self.__path.find("/tagstore")] ###FIXME hardcoded constant
        return res
    
    def __is_android_store(self):
        """
        returns True if the store is an android store
        """
        
        # get 'android_store' store setting
        result = self.__store_config_wrapper.get_android_store()
        
        # is this setting active
        if result is None or result =="":
            return False
        
        if int(result) == 0:
            return False
        else:
            return True
        
    def is_android_store(self):
        return self.__is_android_store()
        
    def set_sync_tags(self, file_name, describing_tags, categorising_tags):
        """
        updates the sync tags
        """
        
        # is the and sync tag wrapper initialized
        if self.__sync_tag_wrapper != None:
            self.__sync_tag_wrapper.set_file(file_name, describing_tags, categorising_tags)

    
    def is_sync_active(self):
        """
        returns True when the sync is active
        """
        return self.__is_sync_active()
    
    def create_sync_lock_file(self):
        """
        creates the sync lock file
        """
        
        if self.__is_sync_active():
            # sync is already active
            return False
        
        # get sync lock file
        path = self.__get_lockfile_path()
        
        # get current pid
        pid = PidHelper.get_current_pid()
        
        # write new pid file
        pid_file = open(path, "w")
        pid_file.write(str(pid))
        pid_file.close()
        
        # done
        return True
    
    def remove_sync_lock_file(self):
        """
        removes the sync lock file
        """
        
        # sync lockfile
        path = self.__get_lockfile_path()
        
        # remove lock file
        self.__file_system.remove_file(path)

    def finish_sync(self):
        """
        writes all changes to the config file / sync file
        """
        
        if self.__tag_wrapper != None:
            self.__tag_wrapper.sync_settings()
        
        if self.__sync_tag_wrapper != None:
            self.__sync_tag_wrapper.sync_settings()


    def get_tag_recommendation(self, number, file_name):
        """
        Changes from Georg
        returns the recommendation
        """
        dictionary = self.__recommender.get_tag_recommendation(
                              self.__tag_wrapper,
                              file_name,
                              number,
                              self.__storage_dir_name)
        
        
        list_with_high_prio = []
        
        threshold = 0.9
        if len(dictionary) <= number:
            threshold = 0.5
        
        for tag_name, rating in dictionary.iteritems():
            if rating > threshold:
                list_with_high_prio.append(tag_name)
    
        
        
        list1 = sorted(dictionary.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        return_list = []
        #for item in list[:number]:
        for item in list1[:15]:
            if item[0] in list_with_high_prio:
                return_list.append(item[0])  
        return return_list

        #list = sorted(dictionary.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        #return_list = []
        #print list
        #for item in list[:number]:
        #for item in list:
        #    return_list.append(item[0])
        #print return_list
        #return return_list

        
    def get_cat_recommendation(self, number, file_name):
        """
        Changes from Georg
        returns the recommendation
        """
        allowed_dict = {}
        if self.is_controlled_vocabulary():
                allowed_dict = self.get_controlled_vocabulary()
        
        dictionary = self.__recommender.get_cat_recommendation(
                              self.__tag_wrapper,
                              file_name,
                              number,
                              self.__storage_dir_name,
                              allowed_dict)
        

        list_with_high_prio = []
        
        threshold = 0.9
        if len(dictionary) <= number:
            threshold = 0.5
        
        for tag_name, rating in dictionary.iteritems():
            if rating > threshold:
                list_with_high_prio.append(tag_name)
    
        
        
        list1 = sorted(dictionary.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        return_list = []
        #for item in list[:number]:
        for item in list1[:15]:
            if item[0] in list_with_high_prio:
                return_list.append(item[0])  
        
        return return_list
        '''
        if len(dictionary) > number/2:
            for item in list:
                if dictionary[item] < 0.6:
                    return_list.append(item[0])
            print "if"
            print return_list
            
        else:
            for item in list:
                return_list.append(item[0])
            print return_list
        return return_list
        '''
        
        
    def get_tag_cloud(self, name):
        dict = self.__tag_wrapper.get_tag_dict(self.__tag_wrapper.KEY_TAGS)
        if len(dict) < 10:
            extension = self.__recommender.get_file_extension(name)
            self.__recommender.recommend_new_tags(dict, extension)
        return self.__tagcloud.create_tag_cloud(dict)
    
    def get_cat_cloud(self, name):
        tmp_dict = self.__tag_wrapper.get_tag_dict(self.__tag_wrapper.KEY_CATEGORIES)
        
        if len(tmp_dict) < 10:
            extension = self.__recommender.get_file_extension(name)
            self.__recommender.recommend_new_tags(tmp_dict, extension)
        
        
        dict = {}
        if self.is_controlled_vocabulary():
            allowed_list = self.get_controlled_vocabulary()
            for cat, size in tmp_dict.iteritems():
                if cat in allowed_list:
                    dict.setdefault(cat, size)
            for cat in allowed_list:
                if cat not in dict:
                    dict.setdefault(cat, 0)
            return self.__tagcloud.create_tag_cloud(dict)
        else:
            return self.__tagcloud.create_tag_cloud(tmp_dict)
    
    def get_tagline_config(self):
        return self.__tagline_config    

## end
