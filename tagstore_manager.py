#!/usr/bin/env python

# -*- coding: utf-8 -*-

## this file is part of tagstore_admin, an alternative way of storing and retrieving information
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
from PyQt4 import QtCore, QtGui
from optparse import OptionParser
from tagstore_retag import ReTagController
from tscore.configwrapper import ConfigWrapper
from tscore.enums import EDateStampFormat, EConflictType
from tscore.exceptions import NameInConflictException, InodeShortageException
from tscore.loghelper import LogHelper
from tscore.store import Store
from tscore.tsconstants import TsConstants
from tsgui.admindialog import StorePreferencesController
from tsgui.tagdialog import TagDialogController
import logging.handlers
import sys

class Administration(QtCore.QObject):

    def __init__(self, application, verbose):
        QtCore.QObject.__init__(self)
        
        self.__log = None
        self.__main_config = None
        self.__admin_dialog = None
        self.__retag_dialog = None
        self.__verbose_mode = verbose
        # the main application which has the translator installed
        self.__application = application

        self.LOG_LEVEL = logging.INFO
        if verbose:
            self.LOG_LEVEL = logging.DEBUG
            

        self.STORE_CONFIG_DIR = TsConstants.DEFAULT_STORE_CONFIG_DIR
        self.STORE_CONFIG_FILE_NAME = TsConstants.DEFAULT_STORE_CONFIG_FILENAME
        self.STORE_TAGS_FILE_NAME = TsConstants.DEFAULT_STORE_TAGS_FILENAME
        self.STORE_VOCABULARY_FILE_NAME = TsConstants.DEFAULT_STORE_VOCABULARY_FILENAME
        
        self.__system_locale = unicode(QtCore.QLocale.system().name())[0:2]
        self.__translator = QtCore.QTranslator()
        if self.__translator.load("ts_" + self.__system_locale + ".qm", "tsresources/"):
            self.__application.installTranslator(self.__translator)
        # "en" is automatically translated to the current language e.g. en -> de
        self.CURRENT_LANGUAGE = self.__get_locale_language()
        #dir names for all available languages
        self.STORE_STORAGE_DIRS = []
        self.STORE_DESCRIBING_NAV_DIRS = []
        self.STORE_CATEGORIZING_NAV_DIRS = []
        self.STORE_EXPIRED_DIRS = []
        self.STORE_NAVIGATION_DIRS = []
        self.SUPPORTED_LANGUAGES = TsConstants.DEFAULT_SUPPORTED_LANGUAGES
        self.__store_dict = {}
        
        # catch all "possible" dir-names
        for lang in self.SUPPORTED_LANGUAGES: 
            self.change_language(lang) 
            self.STORE_STORAGE_DIRS.append(self.trUtf8("storage"))#self.STORE_STORAGE_DIR_EN))  
            self.STORE_DESCRIBING_NAV_DIRS.append(self.trUtf8("descriptions"))#self.STORE_DESCRIBING_NAVIGATION_DIR_EN))  
            self.STORE_CATEGORIZING_NAV_DIRS.append(self.trUtf8("categories"))#self.STORE_CATEGORIZING_NAVIGATION_DIR_EN)) 
            self.STORE_EXPIRED_DIRS.append(self.trUtf8("expired_items"))#STORE_EXPIRED_DIR_EN))
            self.STORE_NAVIGATION_DIRS.append(self.trUtf8("navigation")) 
        
        self.__log = LogHelper.get_app_logger(self.LOG_LEVEL)
        self.__init_configuration()
        
    def __init_configuration(self):
        """
        initializes the configuration. This method is called every time the config file changes
        """
        self.__log.info("initialize configuration")
        if self.__main_config is None:
            self.__main_config = ConfigWrapper(TsConstants.CONFIG_PATH)
            #self.connect(self.__main_config, QtCore.SIGNAL("changed()"), self.__init_configuration)
        
        self.CURRENT_LANGUAGE = self.__main_config.get_current_language();
        
        if self.CURRENT_LANGUAGE is None or self.CURRENT_LANGUAGE == "":
            self.CURRENT_LANGUAGE = self.__get_locale_language()
        
        # switch back to the configured language
        self.change_language(self.CURRENT_LANGUAGE)

        ## connect to all the signals the admin gui is sending 
        if self.__admin_dialog is None:
            self.__admin_dialog = StorePreferencesController()
            self.connect(self.__admin_dialog, QtCore.SIGNAL("create_new_store"), self.__handle_new_store)
            self.connect(self.__admin_dialog, QtCore.SIGNAL("rename_desc_tag"), self.__handle_tag_rename)
            self.connect(self.__admin_dialog, QtCore.SIGNAL("rename_cat_tag"), self.__handle_tag_rename)
            self.connect(self.__admin_dialog, QtCore.SIGNAL("retag"), self.__handle_retagging)
            
            self.connect(self.__admin_dialog, QtCore.SIGNAL("rebuild_store"), self.__handle_store_rebuild)
            self.connect(self.__admin_dialog, QtCore.SIGNAL("rename_store"), self.__handle_store_rename)
            self.connect(self.__admin_dialog, QtCore.SIGNAL("delete_store"), self.__handle_store_delete)

            self.connect(self.__admin_dialog, QtCore.SIGNAL("synchronize"), self.__handle_synchronization)
            
        self.__admin_dialog.set_main_config(self.__main_config)
        
        
        self.__prepare_store_params()
        self.__create_stores()
        
        ## create a temporary store list
        ## add the desc and cat tags which are needed in the admin-dialog
        tmp_store_list = []
        for current_store_item in self.__main_config.get_stores():
            store_name = current_store_item["path"].split("/").pop()
            current_store_item["desc_tags"] = self.__store_dict[store_name].get_tags()
            current_store_item["cat_tags"] = self.__store_dict[store_name].get_categorizing_tags()
            tmp_store_list.append(current_store_item)
        
        self.__admin_dialog.set_store_list(tmp_store_list)
        if self.__main_config.get_first_start():
            self.__admin_dialog.set_first_start(True)
    
    def __handle_synchronization(self, store_name):
        """
        do all the necessary synchronization stuff here ...
        """
        store_to_sync = self.__store_dict[str(store_name)]
        print "####################"
        print "synchronize " + store_name
        print "####################"
        
        store_to_sync.add_item_list_with_tags(["item_one", "item_two"], ["be", "tough"])
            
    def __handle_store_delete(self, store_name):
        self.__admin_dialog.start_progressbar(self.trUtf8("Deleting store ..."))
        store = self.__store_dict[str(store_name)]
        self.__store_to_be_deleted = store_name
        self.connect(store, QtCore.SIGNAL("store_delete_end"), self.__handle_store_deleted)
        ## remove the directories 
        store.remove()
        self.disconnect(store, QtCore.SIGNAL("store_delete_end"), self.__dummy)
        ## remove the config entry 
        self.__main_config.remove_store(store.get_id())
    
    def __dummy(self):
        return "dummy"
    
    def __handle_store_deleted(self, id):
        #second remove the item in the admin_dialog 
        self.__admin_dialog.remove_store_item(self.__store_to_be_deleted)
        
    def __handle_store_rename(self, store_name, new_store_name):
        """
        the whole store directory gets moved to the new directory
        the store will be rebuilt then to make sure all links are updated
        """
        ## show a progress bar at the admin dialog
        self.__admin_dialog.start_progressbar(self.trUtf8("Moving store ..."))
        store = self.__store_dict.pop(str(store_name))        

        self.__main_config.rename_store(store.get_id(), new_store_name)
        ## connect to the rebuild signal because after the moving there is a rebuild routine started
        self.connect(store, QtCore.SIGNAL("store_rebuild_end"), self.__handle_store_rebuild)

        store.move(new_store_name)
        
        self.disconnect(store, QtCore.SIGNAL("store_rebuild_end"))
        
        self.__init_configuration()
        
        
    def __handle_store_rebuild(self, store_name):
        """
        the whole store structure will be rebuild according to the records in store.tgs file
        """
        ## show a progress bar at the admin dialog
        self.__admin_dialog.start_progressbar(self.trUtf8("Rebuilding store ..."))
        store = self.__store_dict[str(store_name)]
        self.connect(store, QtCore.SIGNAL("store_rebuild_end"), self.__handle_store_rebuild)
        store.rebuild()
        self.disconnect(store, QtCore.SIGNAL("store_rebuild_end"), self.__get_locale_language)
    
    def __hide_progress_dialog(self, store_name):
        self.__admin_dialog.stop_progressbar()
        
    
    def __get_locale_language(self):
        """
        returns the translation of "en" in the system language
        """
        return self.trUtf8("en")
    
    def __handle_tag_rename(self, old_tag, new_tag, store_name):
        store = self.__store_dict[store_name]

        old_ba = old_tag.toUtf8()
        old_str = str(old_ba)
        
        new_ba = new_tag.toUtf8()
        new_str = str(new_ba)
        store.rename_tag(unicode(old_str, "utf-8"), unicode(new_str, "utf-8"))
    
    def set_application(self, application):
        """
        if the manager is called from another qt application (e.g. tagstore.py)
        you must set the calling application here for proper i18n
        """
        self.__application = application
    
    def __handle_retagging(self, store_name, item_name):
        """
        creates and configures a tag-dialog with all store-params and tags
        """
        store = self.__store_dict[store_name]
        
        ## make a string object of the QListWidgetItem, so other methods can use it
        item_name = item_name.text()                
        self.__log.info("retagging item %s at store %s..." % (item_name, store_name))
        #if(self.__retag_dialog is None):
            
        ## create the object
        self.__retag_dialog = ReTagController(self.__application, store.get_store_path(), item_name, True, self.__verbose_mode)
        ## connect to the signal(s)
        self.connect(self.__retag_dialog, QtCore.SIGNAL("retag_error"), self.__handle_retag_error)
        self.connect(self.__retag_dialog, QtCore.SIGNAL("retag_cancel"), self.__handle_retag_cancel)
        self.connect(self.__retag_dialog, QtCore.SIGNAL("retag_success"), self.__handle_retag_success)
        self.__retag_dialog.start()

    def __kill_tag_dialog(self):
        """
        hide the dialog and set it to None
        """
        self.__retag_dialog.hide_tag_dialog()
        self.__retag_dialog = None
    
    def __handle_retag_error(self):
        self.__kill_tag_dialog()
        self.__admin_dialog.show_tooltip(self.trUtf8("An error occurred while re-tagging"))
    
    def __handle_retag_success(self):
        self.__kill_tag_dialog()
        self.__admin_dialog.show_tooltip(self.trUtf8("Re-tagging successful!"))
    
    def __handle_retag_cancel(self):
        """
        the "postpone" button in the re-tag dialog has been clicked
        """
        self.__kill_tag_dialog()
    
    def __set_tag_information_to_dialog(self, store):
        """
        convenience method for setting the tag data at the gui-dialog
        """
        self.__retag_dialog.set_tag_list(store.get_tags())
        
        num_pop_tags = self.__main_config.get_num_popular_tags()
        
        tag_set = set(store.get_popular_tags(self.__main_config.get_max_tags()))
        tag_set = tag_set | set(store.get_recent_tags(num_pop_tags))

        cat_set = set(store.get_popular_categories(num_pop_tags))
        cat_set = cat_set | set(store.get_recent_categories(num_pop_tags))

        cat_list = list(cat_set)
        if store.is_controlled_vocabulary():
            allowed_set = set(store.get_controlled_vocabulary())
            self.__retag_dialog.set_category_list(list(allowed_set))

            ## just show allowed tags - so make the intersection of popular tags ant the allowed tags
            cat_list = list(cat_set.intersection(allowed_set)) 
        else:
            self.__retag_dialog.set_category_list(store.get_categorizing_tags())
            
        if len(cat_list) > num_pop_tags:
            cat_list = cat_list[:num_pop_tags]
        self.__retag_dialog.set_popular_categories(cat_list)
        
        ## make a list out of the set, to enable indexing, as not all tags cannot be used
        tag_list = list(tag_set)
        if len(tag_list) > num_pop_tags:
            tag_list = tag_list[:num_pop_tags]
        self.__retag_dialog.set_popular_tags(tag_list)


        self.__retag_dialog.set_store_name(store.get_name())
    
    def __retag_item_action(self, store_name, item_name, tag_list, category_list):
        """
        the "tag!" button in the re-tag dialog has been clicked
        """
        store = self.__store_dict[store_name]
        try:
            ## 1. write the data to the store-file
            store.add_item_with_tags(item_name, tag_list, category_list)
            self.__log.debug("added item %s to store-file", item_name)
        except NameInConflictException, e:
            c_type = e.get_conflict_type()
            c_name = e.get_conflicted_name()
            if c_type == EConflictType.FILE:
                self.__retag_dialog.show_message(self.trUtf8("The filename - %s - is in conflict with an already existing tag. Please rename!" % c_name))
            elif c_type == EConflictType.TAG:
                self.__retag_dialog.show_message(self.trUtf8("The tag - %s - is in conflict with an already existing file" % c_name))
            else:
                self.trUtf8("A tag or item is in conflict with an already existing tag/item")
            #raise
        except InodeShortageException, e:
            self.__retag_dialog.show_message(self.trUtf8("The Number of free inodes is below the threshold of %s%" % e.get_threshold()))
            #raise
        except Exception, e:
            self.__retag_dialog.show_message(self.trUtf8("An error occurred while tagging"))
            raise
        else:
            ## 2 remove the item in the gui
            self.__retag_dialog.remove_item(item_name)
            self.__retag_dialog.hide_dialog()
    
    def show_admin_dialog(self, show):
        self.__admin_dialog.show_dialog()
    
    def set_parent(self, parent):
        """
        set the parent for the admin-dialog if there is already a gui window
        """
        self.__admin_dialog.set_parent(parent)
    
    def set_modal(self, modal):
        """
        True- if the admin dialog should be in modal-mode
        """
        self.__admin_dialog.set_modal(modal)
    
    def __prepare_store_params(self):
        """
        initialzes all necessary params for creating a store object
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
    
    def __create_stores(self):
        store_items = self.__main_config.get_stores()
        for current_store_item in store_items:
            ## use the store name as identifier in the dictionary.
            ## the admindialog just provides store names instead of ids later on
            store_name = current_store_item["path"].split("/").pop()
            tmp_store = Store(current_store_item["id"], current_store_item["path"], 
                  self.STORE_CONFIG_DIR + "/" + self.STORE_CONFIG_FILE_NAME,
                  self.STORE_CONFIG_DIR + "/" + self.STORE_TAGS_FILE_NAME,
                  self.STORE_CONFIG_DIR + "/" + self.STORE_VOCABULARY_FILE_NAME,
                  self.STORE_NAVIGATION_DIRS,
                  self.STORE_STORAGE_DIRS, 
                  self.STORE_DESCRIBING_NAV_DIRS,
                  self.STORE_CATEGORIZING_NAV_DIRS,
                  self.STORE_EXPIRED_DIRS,
                  self.__main_config.get_expiry_prefix())
            tmp_store.init()
            self.__store_dict[store_name] = tmp_store
            self.connect(tmp_store, QtCore.SIGNAL("store_rebuild_end"), self.__hide_progress_dialog)
            self.connect(tmp_store, QtCore.SIGNAL("store_delete_end"), self.__hide_progress_dialog)
            self.connect(tmp_store, QtCore.SIGNAL("store_rename_end"), self.__hide_progress_dialog)
    
    def __handle_new_store(self, dir):
        """
        create new store at given directory
        """
        store_id = self.__main_config.add_new_store(dir)
        
        self.__create_new_store_object(store_id, dir)
        
    def __create_new_store_object(self, store_id, path):
        
        ## create a store object since it builds its own structure 
        tmp_store = Store(store_id, path, 
              self.STORE_CONFIG_DIR + "/" + self.STORE_CONFIG_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_TAGS_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_VOCABULARY_FILE_NAME,
              self.STORE_NAVIGATION_DIRS,
              self.STORE_STORAGE_DIRS, 
              self.STORE_DESCRIBING_NAV_DIRS,
              self.STORE_CATEGORIZING_NAV_DIRS,
              self.STORE_EXPIRED_DIRS,
              self.__main_config.get_expiry_prefix())
        tmp_store.init()
        ## re-initialize the config
        self.__init_configuration()
        
if __name__ == '__main__':  
  
    ## initialize and configure the optionparser
    opt_parser = OptionParser("tagstore_manager.py [options]")
    opt_parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="start programm with detailed output")

    (options, args) = opt_parser.parse_args()
    
    verbose_mode = False
    dry_run = False
    
    if options.verbose:
        verbose_mode = True
    
    tagstore_admin = QtGui.QApplication(sys.argv)
    tagstore_admin.setApplicationName("tagstore_manager")
    tagstore_admin.setOrganizationDomain("www.tagstore.org")
    tagstore_admin.UnicodeUTF8
    
    admin_widget = Administration(tagstore_admin, verbose=verbose_mode)
    admin_widget.show_admin_dialog(True)
    tagstore_admin.exec_()
## end