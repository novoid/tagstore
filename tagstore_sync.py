#!/usr/bin/env python

# -*- coding: utf-8 -*-

## this file is part of tagstore_admin, an alternative way of storing and retrieving information
## Copyright (C) 2010  Karl Voit, Christoph Friedl, Wolfgang Wintersteller, Johannes Anderwald
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

import sys
import os
import filecmp
import logging
import shutil
import datetime
import time
from PyQt4 import QtCore, QtGui

from optparse import OptionParser

from tscore.loghelper import LogHelper
from tscore.configwrapper import ConfigWrapper
from tscore.tsconstants import TsConstants
from tscore.store import Store
from tsgui.syncdialog import SyncDialogController

class SyncController(QtCore.QObject):
    
    def __init__(self, application, source_store_path, target_store_path, auto_sync, verbose = False):
        """
        initialize the controller
        """
        QtCore.QObject.__init__(self)
        
        # init components
        self.__application = application
        self.__source_store_path = source_store_path
        self.__target_store_path = target_store_path
        self.__auto_sync = auto_sync

        self.__main_config = None
        self.__store_config = None
        self.__source_store = None
        self.__target_store = None
        self.__sync_dialog = None
        self.__conflict_file_list = None
        self.__source_items = None
        self.__target_items = None
        self.__target_sync_items = None
        
        
        # default values
        self.STORE_CONFIG_DIR = TsConstants.DEFAULT_STORE_CONFIG_DIR
        self.STORE_CONFIG_FILE_NAME = TsConstants.DEFAULT_STORE_CONFIG_FILENAME
        self.STORE_TAGS_FILE_NAME = TsConstants.DEFAULT_STORE_TAGS_FILENAME
        self.STORE_VOCABULARY_FILE_NAME = TsConstants.DEFAULT_STORE_VOCABULARY_FILENAME
        self.STORE_SYNC_FILE_NAME = TsConstants.DEFAULT_STORE_SYNC_TAGS_FILENAME
        
        # load translators
        locale = unicode(QtCore.QLocale.system().name())[0:2]
        self.__translator = QtCore.QTranslator()
        if self.__translator.load("ts_" + locale + ".qm", "tsresources/"):
            self.__application.installTranslator(self.__translator)

        #get dir names for all available languages
        self.CURRENT_LANGUAGE = self.trUtf8("en")
        self.STORE_STORAGE_DIRS = []
        self.STORE_DESCRIBING_NAV_DIRS = []
        self.STORE_CATEGORIZING_NAV_DIRS = []
        self.STORE_EXPIRED_DIRS = []
        self.STORE_NAVIGATION_DIRS = []
        self.SUPPORTED_LANGUAGES = TsConstants.DEFAULT_SUPPORTED_LANGUAGES
        self.__store_dict = {}
        
        for lang in self.SUPPORTED_LANGUAGES: 
            self.change_language(lang)
            self.STORE_NAVIGATION_DIRS.append(self.trUtf8("navigation")) 
            self.STORE_STORAGE_DIRS.append(self.trUtf8("storage"))#self.STORE_STORAGE_DIR_EN))  
            self.STORE_DESCRIBING_NAV_DIRS.append(self.trUtf8("descriptions"))#self.STORE_DESCRIBING_NAVIGATION_DIR_EN))  
            self.STORE_CATEGORIZING_NAV_DIRS.append(self.trUtf8("categories"))#self.STORE_CATEGORIZING_NAVIGATION_DIR_EN)) 
            self.STORE_EXPIRED_DIRS.append(self.trUtf8("expired_items"))#STORE_EXPIRED_DIR_EN)) 
            
        ## reset language 
        self.change_language(self.CURRENT_LANGUAGE)
            
        # init logger component
        self.LOG_LEVEL = logging.INFO
        if verbose:
            self.LOG_LEVEL = logging.DEBUG 
        
        # get logger
        self.__log = LogHelper.get_app_logger(self.LOG_LEVEL)
        
    def start(self):
        """
        call this method to launch the sync dialog
        """
        self.__init_configuration()
        
    def __init_configuration(self):
        """
        initializes the configuration
        """
        
        # informal debug
        self.__log.info("__init_configuration")
        
        # construct config wrapper
        self.__main_config = ConfigWrapper(TsConstants.CONFIG_PATH)
        if self.__main_config is None:
            self.__emit_not_syncable(self.trUtf8("No config file found for the given path"))
            return


        search_source_path = False
        found_source_path = False
        if self.__source_store_path != None and self.__source_store_path != "":
            search_source_path = True

        search_target_path = False
        found_target_path = False
        if self.__target_store_path != None and self.__target_store_path != "":
            search_target_path = True

        ## create a temporary store list
        ## add the desc and cat tags which are needed in the admin-dialog
        tmp_store_list = []
        store_list = self.__main_config.get_stores()
        
        # add android store
        # when registered
        android_source_path = self.__main_config.get_android_store_path()
        if android_source_path != None and android_source_path != "":
            store_item = {}
            store_item["path"] = android_source_path
            store_item["name"] = "Android"
            store_list.append(store_item)
        
        # enumerate all stores and add their names and paths
        store_name = None
        for current_store_item in store_list:
            
            if current_store_item.has_key("name"):
                store_name = current_store_item["name"]
            else:
                store_name = current_store_item["path"].split("/").pop()
                
            store_path = current_store_item["path"]
            current_store_item["name"] = store_name
            current_store_item["path"] = store_path
            
            tmp_store_list.append(current_store_item)
            # find source target list
            if search_source_path:
                if store_path == self.__source_store_path:
                    found_source_path = True
                    
            if search_target_path:
                if store_path == self.__target_store_path:
                    found_target_path = True
        
        if search_source_path and found_source_path == False:
            # source store is not registered
            self.__emit_not_syncable(self.trUtf8("Source tagstore not registered in main config"))
            return
        
        if search_target_path and found_target_path == False:
            # source store is not registered
            self.__emit_not_syncable(self.trUtf8("Target tagstore not registered in main config"))
            return
        
        if self.__sync_dialog is None:
            self.__sync_dialog = SyncDialogController(tmp_store_list, self.__source_store_path, self.__target_store_path, self.__auto_sync)
            self.__sync_dialog.get_view().setModal(True)
            #self.__tag_dialog.set_parent(self.sender().get_view())
            self.__sync_dialog.connect(self.__sync_dialog, QtCore.SIGNAL("sync_store"), self.__sync_store_action)
            self.__sync_dialog.connect(self.__sync_dialog, QtCore.SIGNAL("sync_conflict"), self.__handle_resolve_conflict)
            self.__sync_dialog.connect(self.__sync_dialog, QtCore.SIGNAL("handle_cancel()"), self.__handle_sync_cancel)

        self.__sync_dialog.show_dialog()
        if self.__auto_sync:
            self.__sync_dialog.start_auto_sync()

    def __handle_resolve_conflict(self, file_item, action):

        # remove item from conflict list        
        self.__conflict_file_list.remove(file_item)
        
        source_item = file_item["source_item"]
        target_item = file_item["target_item"]
        source_store = file_item["source_store"]
        target_store = file_item["target_store"]
        target_file_path = self.__create_target_file_path(target_store, target_item)
        
        self.__log.info("handle_resolve_conclict: source_item %s target_item %s action % s" %(source_item, target_item, action))
        
        
        
        if action == "replace":
            # sync the file and their tags
            self.__sync_conflict_file(source_store, target_store, source_item, target_item, target_file_path)

        # launch conflict dialog
        self.__show_conflict_dialog() 
            
    def __remove_lock_file(self):
        """
        removes the lock from the affected tagstores
        """
        
        self.__source_store.remove_sync_lock_file()
        self.__target_store.remove_sync_lock_file()
    
    def __create_lock_file(self):
        """
        creates the lock files for the affected tagstores
        """
        
        # check if the store is in use by another sync operation
        if self.__source_store.is_sync_active() or self.__target_store.is_sync_active():
            # sync is already active
            return False
        
        # create lock file in source tagstore
        result = self.__source_store.create_sync_lock_file()
        if not result:
            # failed to create lock file
            return result
        
        # create lock in target tagstore
        result = self.__target_store.create_sync_lock_file()
        if not result:
            # delete lock file from source tagstore
            self.__source_store.remove_sync_lock_file()


        # done
        return result
                
    def __show_conflict_dialog(self):
        """
        displays the conflict dialogs when there are one or more conflicts
        """
        
        while len(self.__conflict_file_list) > 0:
        
            # get first item
            current_item = self.__conflict_file_list[0]
            
            # extract paramters
            source_item = current_item["source_item"]
            target_item = current_item["target_item"]
            source_store = current_item["source_store"]
            target_store = current_item["target_store"]
            target_items = current_item["target_items"]
            target_sync_items = current_item["target_sync_items"]
            
            # do we need to sync
            sync_success = self.__sync_item(source_store, target_store, target_items, target_sync_items, source_item, False)
            if sync_success:
                # remove item
                # conflict has been solved by a previous conflict resolution
                self.__conflict_file_list.remove(current_item)
                continue

            # update status dialog
            message = ("Syncing %s" % source_item)            
            self.__sync_dialog.set_status_msg(message)
            
            # replace dialog message
            message = ("Do you want to replace file %s with %s" % (self.__get_full_file_path(target_store, target_item), self.__get_full_file_path(source_store, source_item))) 
            self.__sync_dialog.show_conflict_dialog("Conflict", message, current_item)
            
            return
        # end while
        
        # conflict list empty
        msg = "Sync completed on " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # flush all changes
        self.__flush_changes()


        self.__sync_dialog.set_status_msg(msg)
        self.__sync_dialog.toggle_sync_button(True)
        self.__sync_dialog.set_close_button_text(self.trUtf8("Finish"))
        self.__remove_lock_file()
            
    def __create_source_store(self, source_store):
        
        """
        create the source store object
        """
    
        # construct config wrapper for the tagstore
        self.__store_config = ConfigWrapper(source_store)
        if self.__store_config is None:    
            self.__emit_not_syncable(self.trUtf8("No source store found for the given path"))
            return    
    
        # construct store object
        self.__source_store = Store(self.__store_config.get_store_id(), source_store, 
              self.STORE_CONFIG_DIR + "/" + self.STORE_CONFIG_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_TAGS_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_VOCABULARY_FILE_NAME,
              self.STORE_NAVIGATION_DIRS,
              self.STORE_STORAGE_DIRS, 
              self.STORE_DESCRIBING_NAV_DIRS,
              self.STORE_CATEGORIZING_NAV_DIRS,
              self.STORE_EXPIRED_DIRS,
              self.__main_config.get_expiry_prefix())
        self.__source_store.init()
    
    def __flush_changes(self):
        
        if self.__source_store != None:
            self.__source_store.finish_sync()
        
        if self.__target_store != None:
            self.__target_store.finish_sync()
            
    def __create_target_store(self, target_store):
        """
        create the target store object
        """

        # construct target store config object
        self.__target_store_config = ConfigWrapper(target_store)
        if self.__target_store_config is None:    
            self.__emit_not_syncable(self.trUtf8("No target store found for the given path"))
            return
        
        # construct target store object
        self.__target_store = Store(self.__target_store_config.get_store_id(), target_store, 
              self.STORE_CONFIG_DIR + "/" + self.STORE_CONFIG_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_TAGS_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_VOCABULARY_FILE_NAME,
              self.STORE_NAVIGATION_DIRS,
              self.STORE_STORAGE_DIRS, 
              self.STORE_DESCRIBING_NAV_DIRS,
              self.STORE_CATEGORIZING_NAV_DIRS,
              self.STORE_EXPIRED_DIRS,
              self.__main_config.get_expiry_prefix())
        self.__target_store.init()        

    def __get_file_items_with_sync_tag(self):
        """
        returns all files which have the associated sync tag
        """
        
        # get source items
        source_items = self.__source_store.get_items()

        # get current sync tag
        sync_tag = self.__main_config.get_sync_tag()
       
        # build empty result list
        source_sync_items = []
       
        # enumerate all items
        for source_item in source_items:
            
            if self.__has_sync_tag(self.__source_store, source_item, sync_tag):
                # item is tagged with sync tag
                source_sync_items.append(source_item)
                continue
        
        # done
        return source_sync_items


    def __prepare_sync(self, source_store, target_store):
        """
        prepares the sync
        """
        
        # initialize the store objects
        self.__init_stores(source_store, target_store)
        
        # get sync style
        android_sync = self.__source_store.is_android_store() or self.__target_store.is_android_store()
        
        # get source items
        if android_sync:
            self.__source_items = self.__get_file_items_with_sync_tag()
        else:
            self.__source_items = self.__source_store.get_items()

        # get target items
        self.__target_items = self.__target_store.get_items()

        # get target sync items
        self.__target_sync_items = self.__target_store.get_sync_items()

    def __sync_store_action(self, source_store, target_store):
        """
        initializes the sync
        """

        # conflict list
        self.__conflict_file_list = []

        # prepare the sync
        self.__prepare_sync(source_store, target_store)

        # now create the lock files
        lock_file = self.__create_lock_file()
        if not lock_file:
            self.__log.info("another sync is in progress please wait until it is finished")
            self.__sync_dialog.set_status_msg("Another sync is pending, please wait until it is finished")
            self.__sync_dialog.set_close_button_text(self.trUtf8("Finish"))
            return

        # start with source tagstore -> target tagstore
        self.__handle_sync()

        # switch stores
        self.__prepare_sync(target_store, source_store)

        # push changes from target store to source tagstore
        self.__handle_sync()
        
        self.__log.info("Number of conflicts %d" %(len(self.__conflict_file_list)))
        
        # launch conflict dialog
        self.__show_conflict_dialog()
        
    def __handle_sync(self):
        """
        executes a sync
        """

        # start the sync
        self.__start_sync(self.__source_store, self.__target_store, self.__source_items, self.__target_items, self.__target_sync_items)

    def __sync_item(self, source_store, target_store, target_items, target_sync_items, source_item, add_conflict_list=True):
        
        # is there such an item in the target tagstore
        target_item = self.__find_item_in_store(target_items, source_item)
        
        # does the file exist in the target tagstore
        if target_item != None:
            return self.__sync_existing_item(source_store, target_store, target_items, target_sync_items, source_item, target_item, add_conflict_list)    
        else:
            return self.__sync_new_item(source_store, target_store, target_items, target_sync_items, source_item, add_conflict_list)

    def __sync_new_item(self, source_store, target_store, target_items, target_sync_items, source_item, add_conflict_list):   


        # file does not exist
        # was it already synced once?
        target_sync_item = self.__find_item_in_store(target_sync_items, source_item)
        if target_sync_item:
            #the file was already synced once, skipping
            self.__log.info("[SKIP] File '%s' was already synced once" % target_sync_item)
            return True

        # file was not synced before, lets check if it exists in the target destination store
        # create target path
        target_file_path = self.__create_target_file_path(target_store, source_item)
        
        # check if file already exists
        if not os.path.exists(target_file_path):
            # file does not yet exist
            self.__log.info("[SYNC] New File: '%s' is synced" % source_item)
            self.__sync_new_file(source_store, target_store, source_item, target_file_path)
            return True
        
        # create target item
        target_item = self.__create_target_file_item(target_store, source_item)
            
        # the file already exists
        # is it the same file
        files_equal = self.__are_files_equal(source_store, target_store, source_item, target_item)
        if files_equal:
            # file is present, just sync the tags
            self.__log.info("[SYNC] File '%s' already present in target, syncing tags only" % source_item)
            self.__sync_new_file(source_store, target_store, source_item, target_file_path, copy_file=False)
            return False
            
        # sync conflict
        self.__log.info("[Conflict] File: '%s' already exists" % target_file_path)
        if add_conflict_list:
            self.__add_conflict_item(source_store, target_store, target_items, target_sync_items, source_item, target_item)
        return False
        
        
    def __sync_existing_item(self, source_store, target_store, target_items, target_sync_items, source_item, target_item, add_conflict_list):
        """
        syncs an existing item
        """
        
        # check if the source file is equal
        files_equal = self.__are_files_equal(source_store, target_store, source_item, target_item)
        if files_equal:
            # files are equal
            # sync tags
            self.__log.info("[SYNC] Tags of file '%s' are synced" % source_item)
            self.__sync_new_tags(source_store, target_store, source_item, target_item)
            return True

        # okay files are not equal, lets get a sync date
        target_sync_item = (target_item in target_sync_items)
        if not target_sync_item:
            # there is no sync item for file
            self.__log.info("[Conflict] File '%s' -> %s' was added in the tagstore simultaneously" % (source_item, target_item))
            if add_conflict_list:
                self.__add_conflict_item(source_store, target_store, target_items, target_sync_items, source_item, target_item)
            return False

        # get sync time
        str_sync_gm_time = target_store.get_sync_file_timestamp(target_item)
        sync_gm_time = time.strptime(str_sync_gm_time, "%Y-%m-%d %H:%M:%S")

        # get source modification time
        mod_time = os.path.getmtime(self.__get_full_file_path(source_store, source_item))
        source_gm_time = time.gmtime(mod_time)
                    
        # get target modification time
        mod_time = os.path.getmtime(self.__get_full_file_path(target_store, target_item))
        target_gm_time = time.gmtime(mod_time)
               
        # was source file modified
        if source_gm_time <= sync_gm_time:
            # file was not modified since last sync 
            # sync new tags
            self.__log.info("[SYNC] No source modification, tags of file '%s' are synced" % source_item)
            self.__sync_new_tags(source_store, target_store, source_item, target_item)
            return True

        # source modified, lets check target file
        if target_gm_time <= sync_gm_time:
            # target file was not modified
            self.__log.info("[SYNC] Updating file '%s' and tags" % source_item)
            shutil.copy2(self.__get_full_file_path(source_store, source_item), self.__get_full_file_path(target_store, target_item))
            self.__sync_new_tags(source_store, target_store, source_item, target_item)            
            return True

        # source and target file have been modified, do their tags match
        if self.__are_all_tags_equal(source_store, target_store, source_item, target_item):
            # sync the file
            self.__log.info("[Conflict] Both files have been modified '%s'" % target_item)
            if add_conflict_list:
                self.__add_conflict_item(source_store, target_store, target_items, target_sync_items, source_item, target_item)
            return False

        # both files and tags are modified
        self.__log.info("[Conflict] Both files and tags are modified '%s'" % target_item)
        if add_conflict_list:
            self.__add_conflict_item(source_store, target_store, target_items, target_sync_items, source_item, target_item)
        return False

    def __start_sync(self, source_store, target_store, source_items, target_items, target_sync_items):
        """
        starts the sync
        """
        
        for source_item in source_items:
            
            # sync item
            self.__log.info("[SYNC] Current Item: %s" % source_item)
            self.__sync_item(source_store, target_store, target_items, target_sync_items, source_item)
        
    
    def __are_all_tags_equal(self, source_store, target_store, source_item, target_item):
        """
        checks if all tags from the source item and target item are equal
        """
        
        source_describing_tags = source_store.get_describing_tags_for_item(source_item)
        target_describing_tags = target_store.get_describing_tags_for_item(target_item)
        
        if source_describing_tags != target_describing_tags:
            return False
        
        # get categorizing tags
        source_categorising_tags = source_store.get_categorizing_tags_for_item(source_item)
        target_categorising_tags = target_store.get_categorizing_tags_for_item(target_item)

        if source_categorising_tags != target_categorising_tags:
            return False
        
        # all equal
        return True
    
    def __sync_new_tags(self, source_store, target_store, source_item, target_item):
        """
        syncs new tags
        """

        # get describing tags
        target_describing_sync_tags = set(target_store.get_describing_sync_tags_for_item(target_item))
        target_describing_tags = set(target_store.get_describing_tags_for_item(target_item))
        source_describing_tags = set(source_store.get_describing_tags_for_item(source_item))
        
        # get categorizing tags
        target_categorizing_sync_tags = set(target_store.get_categorizing_sync_tags_for_item(target_item))
        target_categorizing_tags = set(target_store.get_categorizing_tags_for_item(target_item))
        source_categorizing_tags = set(source_store.get_categorizing_tags_for_item(source_item))
    
        if target_describing_tags == source_describing_tags and\
            target_categorizing_tags == source_categorizing_tags:
            self.__log.info("no changes found")
            target_store.set_sync_tags(target_item, source_describing_tags, source_categorizing_tags)
            return

        new_describing_tags = (source_describing_tags - target_describing_sync_tags) | target_describing_tags
        
        # remove tag support
        #removed_describing_tags = target_describing_sync_tags - source_describing_tags
        #new_describing_tags -= removed_describing_tags
        
        #if len(removed_describing_tags) > 0:
        #    for item in removed_describing_tags:
        #        self.__log.info("removed tag: '%s'" %item)
        new_categorizing_tags = (source_categorizing_tags - target_categorizing_sync_tags) | target_categorizing_tags
    
        # now sync the tags
        target_store.add_item_with_tags(target_item, new_describing_tags, new_categorizing_tags)
        
        # update the sync tags
        target_store.set_sync_tags(target_item, source_describing_tags, source_categorizing_tags)
    
    def __sync_conflict_file(self, source_store, target_store, source_item, target_item, target_file_path):
        """
        replaces the target file with the source file
        """
        
        # get describing tags from file
        describing_tag_list = source_store.get_describing_tags_for_item(source_item)
        
        # get categorizing tags from file
        categorizing_tag_list = source_store.get_categorizing_tags_for_item(source_item)

        # replace file
        shutil.copy2(self.__get_full_file_path(source_store, source_item), target_file_path)

        # replace current entry
        target_store.add_item_with_tags(target_item, describing_tag_list, categorizing_tag_list)

        # set the sync tags
        target_store.set_sync_tags(target_item, describing_tag_list, categorizing_tag_list)
    
    def __sync_new_file(self, source_store, target_store, source_item, target_file_path, copy_file=True):
        """
        copies the new file and its associated tags
        """
        
        # get describing tags from file
        describing_tag_list = source_store.get_describing_tags_for_item(source_item)
        
        # get categorizing tags from file
        categorizing_tag_list = source_store.get_categorizing_tags_for_item(source_item)
        
        if copy_file:
            # copy file
            shutil.copy2(self.__get_full_file_path(source_store, source_item), target_file_path)
        
        # create target file item name
        target_item = self.__create_target_file_item(target_store, source_item)
        
        # add to tagstore
        target_store.add_item_with_tags(target_item, describing_tag_list, categorizing_tag_list)
        
        # set the sync tags
        target_store.set_sync_tags(target_item, describing_tag_list, categorizing_tag_list)
        
    def __create_target_file_item(self, target_store, source_item):
        """
        creates the target file name
        """
        
        position = source_item.rfind("\\")
        if position != -1:
            source_item = source_item[position+1:len(source_item)]

        if target_store.is_android_store():
            # get directories
            storage_dir = target_store.get_android_root_directory()
            tagstore_dir = target_store.get_storage_directory()
            
            # extract storage directory name
            # replace path seperators with %5C which is required
            directory = tagstore_dir[len(storage_dir)+1:len(tagstore_dir)] + "\\" + source_item
            directory = directory.replace("/", "\\")
            return directory
        else:
            return source_item


    def __create_target_file_path(self, target_store, source_item):
        """
        creates the target file path
        """
        position = source_item.rfind("\\")
        if position != -1:
            source_item = source_item[position+1:len(source_item)]
  
        return target_store.get_storage_directory() + "/" + source_item
    
    def __get_full_file_path(self, store, file_item):
    
        # check if it is an android store
        if store.is_android_store():
            # android store items have the full path encoded from the root directory
            return store.get_android_root_directory() + "/" + file_item
        else:
            # normal tagstores include their files in the storage directory
            return store.get_storage_directory() + "/" + file_item
            
    def __are_files_equal(self, source_store, target_store, source_file, target_file):
        """
        compares both files if there are equal
        """
        
        # get file locations
        source_path = self.__get_full_file_path(source_store, source_file)
        target_path = self.__get_full_file_path(target_store, target_file)
        
        # check for equality        
        return filecmp.cmp(source_path, target_path, 0)
        
    def __find_item_in_store(self, store_items, source_item):
        """
        finds an item which has the same name
        It is required to remove directory from the searched entries. The reasons is that 
        an Android tagstore has multiple virtual directories attached. 
        """
        
        position = source_item.rfind("\\")
        if position != -1:
            source_item = source_item[position+1:len(source_item)]
        

        
        # look up all items in the target store
        for file_name in store_items:

            # is there a directory in the path
            position  = file_name.rfind("\\")
            if position != -1:
                fname = file_name[position+1:len(file_name)]
            else:
                fname = file_name
            
            # does the name now match
            if fname == source_item:
                return file_name
        
        # no item found
        return None
    
    def __emit_not_syncable(self, err_msg):
        self.__log.error(err_msg)
        self.emit(QtCore.SIGNAL("sync_error"))

        
    def set_application(self, application):
        """
        if the manager is called from another qt application (e.g. tagstore.py)
        you must set the calling application here for proper i18n
        """
        self.__application = application
        
    def __handle_sync_cancel(self):
        """
        the cancel button has been pressed
        """
        self.emit(QtCore.SIGNAL("sync_cancel"))
        #self.__tag_dialog.hide_dialog()

    def __prepare_store_params(self):
        """
        initializes all necessary parameters for creating a store object
        """
    
        for lang in self.SUPPORTED_LANGUAGES: 
            #self.change_language(lang) 
            self.STORE_STORAGE_DIRS.append(self.trUtf8("storage"))  
            self.STORE_DESCRIBING_NAV_DIRS.append(self.trUtf8("navigation"))  
            self.STORE_CATEGORIZING_NAV_DIRS.append(self.trUtf8("categorization")) 
            self.STORE_EXPIRED_DIRS.append(self.trUtf8("expired_items")) 
        ## reset language 
        #self.change_language(store_current_language) 
        
        config_dir = self.__main_config.get_store_config_directory()
        if config_dir != "":
            self.STORE_CONFIG_DIR = config_dir
        config_file_name = self.__main_config.get_store_configfile_name()
        if config_file_name != "":
            self.STORE_CONFIG_FILE_NAME = config_file_name
        tags_file_name = self.__main_config.get_store_tagsfile_name()
        if tags_file_name != "":
            self.STORE_TAGS_FILE_NAME = tags_file_name
        vocabulary_file_name = self.__main_config.get_store_vocabularyfile_name()
        if vocabulary_file_name != "":
            self.STORE_VOCABULARY_FILE_NAME = vocabulary_file_name

    def change_language(self, locale):
        """
        changes the current application language
        please notice: this method is used to find all available storage/navigation directory names
        this is why it should not be extended to call any UI update methods directly
        """
        
        ## delete current translation to switch to default strings
        self.__application.removeTranslator(self.__translator)

        ## load new translation file        
        self.__translator = QtCore.QTranslator()
        language = unicode(locale)
        if self.__translator.load("ts_" + language + ".qm", "tsresources/"):
            self.__application.installTranslator(self.__translator)
            
        ## update current language
#        self.CURRENT_LANGUAGE = self.trUtf8("en")
        self.CURRENT_LANGUAGE = self.trUtf8(locale)

    def __init_stores(self, source_store, target_store):
        """
        initializes the store objects
        """
        
        # get current language from main config file and apply it
        self.CURRENT_LANGUAGE = self.__main_config.get_current_language();
        self.change_language(self.CURRENT_LANGUAGE)
        
        # prepare all parameters for creating the store object
        self.__prepare_store_params()
        
        # create the source store
        self.__create_source_store(source_store)
        
        # create the target store
        self.__create_target_store(target_store)

        #init sync log for the source store
        self.__source_store.init_sync_log(self.__target_store.get_name())
        
        # init sync log for the target store        
        self.__target_store.init_sync_log(self.__source_store.get_name())
        
    def __has_sync_tag(self, source_store, source_item, sync_tag):
        """
        checks if the file has the sync tag associated
        """
        
        # get describing tags
        source_item_describing_tags = source_store.get_describing_tags_for_item(source_item)
        
        if source_item_describing_tags != None:
            if sync_tag in source_item_describing_tags:
                return True
        
        # get categorising tags
        source_item_categorising_tags = source_store.get_categorizing_tags_for_item(source_item)
        if source_item_categorising_tags != None:
            if sync_tag in source_item_categorising_tags:
                return True
        
        # tag not found
        return False

    def __add_conflict_item(self, source_store, target_store, target_items, target_sync_items, source_item, target_item):
        """
        adds a conflict item to the conflict list
        """
        
        current_item = {}
        current_item["source_item"] = source_item
        current_item["target_item"] = target_item
        current_item["source_store"] = source_store
        current_item["target_store"] = target_store
        current_item["target_items"] = target_items
        current_item["target_sync_items"] = target_sync_items

        self.__conflict_file_list.append(current_item)

class ApplicationController(QtCore.QObject):
    """
    a small helper class to launch the sync-dialog as a standalone application
    this helper connects to the signals emitted by the sync controller and does the handling
    """
    def __init__(self, application, source_store, target_store, auto_sync, verbose):
        QtCore.QObject.__init__(self)
        
        self.LOG_LEVEL = logging.INFO
        if verbose:
            self.LOG_LEVEL = logging.DEBUG
        
        self.__log = LogHelper.get_app_logger(self.LOG_LEVEL)
        
        ## create a config object to get the registered store paths
        self.__main_config = ConfigWrapper(TsConstants.CONFIG_PATH)
        
        ## create the object
        self.__sync_widget = SyncController(application, source_store, target_store, auto_sync, verbose_mode)
        
        ## connect to the signal(s)
        self.connect(self.__sync_widget, QtCore.SIGNAL("sync_cancel"), self.__handle_sync_cancel)
        self.connect(self.__sync_widget, QtCore.SIGNAL("sync_error"), self.__handle_sync_error)
        self.connect(self.__sync_widget, QtCore.SIGNAL("sync_success"), self.__handle_sync_success)
        
        ## start the sync controller
        self.__sync_widget.start()
        
    def __handle_sync_error(self):
        """
        exit the program if there is an error
        """
        sys.exit(-1)
        
    def __handle_sync_success(self):
        """
        exit the application gracefully
        """
        sys.exit(0)

    def __handle_sync_cancel(self):
        """
        exit the application gracefully
        """
        sys.exit(0)
   
if __name__ == '__main__':  
  
    ## initialize and configure the optionparser
    usage = "\nThis program opens a dialog used for syncing two distinct tagstores."
    opt_parser = OptionParser("tagstore_sync.py [-source_store=<source_store>] [-target_store=<target_store>]")
    
    
    opt_parser.add_option("-s", "--first_store", dest="first_store", help="absolute or relative path to the first tagstore")
    opt_parser.add_option("-t", "--second_store", dest="second_store", help="absolute or relative path to the second tagstore")
    opt_parser.add_option("-a", "--auto_sync", dest="auto_sync", action="store_true", help="automatically start the sync process")
    #opt_parser.add_option("-c", "--hide_conflict", dest="conflict", help="")
            
    opt_parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="start programm with detailed output")

    (options, args) = opt_parser.parse_args()

    source_store = None
    target_store = None
    auto_sync = False
    verbose_mode = False
    
    if options.verbose:
        verbose_mode = True
        
    if options.first_store:
        source_store = options.source_store

    if options.second_store:
        target_store = options.second_store

    if options.auto_sync:
        auto_sync = True
    
    # check if source store is the same as the target store
    if source_store != None and target_store != None:
        if source_store == target_store:
            print "Error: source and target store are the same"
            print source_store
            print target_store
            print auto_sync
            opt_parser.print_help()
            sys.exit()
        
    tagstore_tag = QtGui.QApplication(sys.argv)
    tagstore_tag.setApplicationName("tagstore_sync")
    tagstore_tag.setOrganizationDomain("www.tagstore.org")
    tagstore_tag.UnicodeUTF8
    
    appcontroller = ApplicationController(tagstore_tag, source_store, target_store, auto_sync, verbose_mode)
    tagstore_tag.exec_()
    
def quit_application():
    opt_parser.print_help()
    sys.exit()
## end
