#!/usr/bin/env python

# -*- coding: utf-8 -*-

## this file is part of tagstore_tag, an alternative way of storing and retrieving information
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
import sys
import logging
from PyQt4 import QtCore, QtGui
from optparse import OptionParser
from tscore.configwrapper import ConfigWrapper
from tscore.enums import EDateStampFormat, EConflictType, EFileEvent
from tscore.exceptions import NameInConflictException, InodeShortageException
from tscore.loghelper import LogHelper
from tscore.pathhelper import PathHelper
from tscore.store import Store
from tscore.tsconstants import TsConstants
from tsgui.tagdialog import TagDialogController

class ReTagController(QtCore.QObject):
    """
    object for calling the re-tag view.
    ************************
    MANDATORY parameters: 
    ************************
    * application -> the parent qt-application object ()for installing the translator properly
    * store_path -> absolute path to the store of the item to be retagged (TIP: use the PathHelper object to resolve a relative path.)
    * item_name -> the name of the item to be renamed (exactly how it is defined in the tagfile)

    ************************
    TIP: use the PathHelper object to resolve a relative path AND to extract the item name out of it. 
    ************************
    
    ************************
    OPTIONAL parameters:
    ************************
    * standalone_application -> default = False; set this to true if there
    * verbose -> set this to true for detailed output
    (DEVEL * retag_mode -> this application could even be used for a normal tagging procedure as well.)
    
    ************************
    IMPORTANT!!!
    ************************
    the start() method must be called in order to begin with the tagging procedure
    """

    def __init__(self, application, store_path, item_name, retag_mode = True, verbose = False):
        QtCore.QObject.__init__(self)
        
        self.__log = None
        self.__main_config = None
        self.__store_config = None
        self.__tag_dialog = None
        self.__store = None
        
        self.__retag_mode = retag_mode
        
        self.__no_store_found = False

        self.__item_name = unicode(item_name)
        self.__store_path = store_path

        # the main application which has the translator installed
        self.__application = application

        self.LOG_LEVEL = logging.INFO
        if verbose:
            self.LOG_LEVEL = logging.DEBUG
            

        self.STORE_CONFIG_DIR = TsConstants.DEFAULT_STORE_CONFIG_DIR
        self.STORE_CONFIG_FILE_NAME = TsConstants.DEFAULT_STORE_CONFIG_FILENAME
        self.STORE_TAGS_FILE_NAME = TsConstants.DEFAULT_STORE_TAGS_FILENAME
        self.STORE_VOCABULARY_FILE_NAME = TsConstants.DEFAULT_STORE_VOCABULARY_FILENAME
        
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
        self.MAX_CLOUD_TAGS = TsConstants.DEFAULT_MAX_CLOUD_TAGS
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
        
        self.__log = LogHelper.get_app_logger(self.LOG_LEVEL)
        
    def start(self):
        """
        call this method to actually start the tagging procedure
        """
        self.__init_configuration()
        
    
    def __init_configuration(self):
        """
        initializes the configuration. This method is called every time the config file changes
        """
        self.__log.info("initialize configuration")
        
        
        self.__main_config = ConfigWrapper(TsConstants.CONFIG_PATH)
        
        if self.__main_config is None:
            self.__emit_not_retagable(self.trUtf8("No config file found for the given path"))
            return
        
        ## check if there has been found an appropriate store_path in the config 
        if self.__store_path is None:
            self.__emit_not_retagable(self.trUtf8("No store found for the given path"))
            return
        else:
            self.__store_config = ConfigWrapper(self.__store_path)
        
        self.__prepare_store_params()
        
        self.CURRENT_LANGUAGE = self.__main_config.get_current_language();
        self.change_language(self.CURRENT_LANGUAGE)
        #self.__main_config.connect(self.__main_config, QtCore.SIGNAL("changed()"), self.__init_configuration)

        self.__store = Store(self.__store_config.get_store_id(), self.__store_path, 
              self.STORE_CONFIG_DIR + "/" + self.STORE_CONFIG_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_TAGS_FILE_NAME,
              self.STORE_CONFIG_DIR + "/" + self.STORE_VOCABULARY_FILE_NAME,
              self.STORE_NAVIGATION_DIRS,
              self.STORE_STORAGE_DIRS, 
              self.STORE_DESCRIBING_NAV_DIRS,
              self.STORE_CATEGORIZING_NAV_DIRS,
              self.STORE_EXPIRED_DIRS,
              self.__main_config.get_expiry_prefix())
        self.__store.init()
        
        if self.__tag_dialog is None:
            self.__tag_dialog = TagDialogController(self.__store.get_name(), self.__store.get_id(), self.__main_config.get_max_tags(), self.__main_config.get_tag_seperator(), self.__main_config.get_expiry_prefix())
            self.__tag_dialog.get_view().setModal(True)
            #self.__tag_dialog.set_parent(self.sender().get_view())
            self.__tag_dialog.connect(self.__tag_dialog, QtCore.SIGNAL("tag_item"), self.__tag_item_action)
            self.__tag_dialog.connect(self.__tag_dialog, QtCore.SIGNAL("handle_cancel()"), self.__handle_tag_cancel)


        ## configure the tag dialog with the according settings
        format_setting = self.__store.get_datestamp_format()
        datestamp_hidden = self.__store.get_datestamp_hidden()
        ## check if auto datestamp is enabled
        if format_setting != EDateStampFormat.DISABLED:
            self.__tag_dialog.show_datestamp(True)
            ## set the format
            format = None
            if format_setting == EDateStampFormat.DAY:
                format = TsConstants.DATESTAMP_FORMAT_DAY
            elif format_setting == EDateStampFormat.MONTH:
                format = TsConstants.DATESTAMP_FORMAT_MONTH
            
            self.__tag_dialog.set_datestamp_format(format, datestamp_hidden)
        
        self.__tag_dialog.show_category_line(self.__store.get_show_category_line())
        self.__tag_dialog.set_category_mandatory(self.__store.get_category_mandatory()) 
        
        ## check if the given item really exists in the store
        if not self.__store.item_exists(self.__item_name):
            self.__emit_not_retagable(self.trUtf8("%s: There is no such item recorded in the store" % self.__item_name))
            return 

        self.__set_tag_information_to_dialog(self.__store)
        
        if self.__retag_mode:
            self.__handle_retag_mode()
        
        self.__tag_dialog.show_dialog()
    
    def __emit_not_retagable(self, err_msg):
        self.__log.error(err_msg)
        self.emit(QtCore.SIGNAL("retag_error"))
    
    def __handle_retag(self, store_name, file_name_list, new_describing_tags, new_categorizing_tags):
        
        for file_name in file_name_list:
            ## first of all remove the old references
            self.__store.remove_file(file_name)
            ## now create the new navigation structure
            try:
                self.__store.add_item_with_tags(file_name, new_describing_tags, new_categorizing_tags)
            except InodeShortageException, e:
                self.__tag_dialog.show_message(self.trUtf8("The Number of free inodes is below the threshold of %s%" % e.get_threshold()))
                #raise
            except Exception, e:
                self.__tag_dialog.show_message(self.trUtf8("An error occurred while tagging"))
                raise
            else:
                ## 2. remove the item in the gui
                self.__tag_dialog.remove_item_list(list(file_name))
                ## 3. refresh the tag information of the gui
                self.__set_tag_information_to_dialog(self.__store)
        self.emit(QtCore.SIGNAL("retag_success"))

    def set_application(self, application):
        """
        if the manager is called from another qt application (e.g. tagstore.py)
        you must set the calling application here for proper i18n
        """
        self.__application = application
        
    def __handle_retag_mode(self):
        
        self.__tag_dialog.set_retag_mode()

        ## remove the tag command        
        self.__tag_dialog.disconnect(self.__tag_dialog, QtCore.SIGNAL("tag_item"), self.__tag_item_action)
        ## reconnect the signal to the re-tag action and not the default tag action
        self.__tag_dialog.connect(self.__tag_dialog, QtCore.SIGNAL("tag_item"), self.__handle_retag)
        
        cat_content = ""
        cat_tags = self.__store.get_describing_tags_for_item(self.__item_name)
        for tag in cat_tags:
            if cat_content == "":
                cat_content = tag
            else:
                cat_content = "%s%s%s" %(cat_content,", ", tag) 
        self.__tag_dialog.set_describing_line_content(cat_content)
        desc_content = ""
        desc_tags = self.__store.get_categorizing_tags_for_item(self.__item_name)
        for tag in desc_tags:
            if desc_content == "":
                desc_content = tag
            else:
                desc_content = "%s%s%s" %(desc_content,", ", tag) 
        self.__tag_dialog.set_category_line_content(desc_content)
        
        self.__tag_dialog.add_pending_item(self.__item_name)
        
        return True


    def __set_tag_information_to_dialog(self, store):
        """
        convenience method for setting the tag data at the gui-dialog
        """
        self.__tag_dialog.set_tag_list(store.get_tags())
        
        num_pop_tags = self.__main_config.get_num_popular_tags()
        
        cat_list = []

        
        #self.__tag_dialog.set_popular_categories(cat_list)
        #self.__tag_dialog.set_popular_tags(tag_list)
        

        if store.get_tagline_config() == 1 or store.get_tagline_config() == 2 or store.get_tagline_config() == 3:
            tmp_cat_list = store.get_cat_recommendation(num_pop_tags, self.__item_name)
            if store.is_controlled_vocabulary():
                allowed_set = set(store.get_controlled_vocabulary())
                self.__tag_dialog.set_category_list(list(allowed_set))
                ## just show allowed tags - so make the intersection of popular tags ant the allowed tags
                for cat in tmp_cat_list:
                    if cat in list(allowed_set):
                        cat_list.append(cat)
                #for cat in list(allowed_set):
                #    if cat not in cat_list:
                #        cat_list.append(cat)
            else:
                self.__tag_dialog.set_category_list(store.get_categorizing_tags())
                cat_list = tmp_cat_list
            
            #if len(cat_list) > num_pop_tags:
            #    cat_list = cat_list[:num_pop_tags]    
                
            dict = store.get_cat_cloud(self.__item_name)
            self.__tag_dialog.set_cat_cloud(dict, cat_list, self.MAX_CLOUD_TAGS)
    
        if store.get_tagline_config() == 1 or store.get_tagline_config() == 2 or store.get_tagline_config() == 0:
            tag_list = store.get_tag_recommendation(num_pop_tags, self.__item_name)
            #if len(tag_list) > num_pop_tags:
            #    tag_list = tag_list[:num_pop_tags]
            dict = store.get_tag_cloud(self.__item_name)
            self.__tag_dialog.set_tag_cloud(dict, tag_list, self.MAX_CLOUD_TAGS)
        
        if not self.__retag_mode:
            self.__tag_dialog.set_item_list(store.get_pending_changes().get_items_by_event(EFileEvent.ADDED))
            
        self.__tag_dialog.set_store_name(store.get_name())
    
    def __tag_item_action(self, item_name, tag_list, category_list):
        """
        the "tag!" button in the re-tag dialog has been clicked
        """
        try:
            ## 1. write the data to the store-file
            self.__store.add_item_with_tags(item_name, tag_list, category_list)
            self.__log.debug("added item %s to store-file", item_name)
        except NameInConflictException, e:
            c_type = e.get_conflict_type()
            c_name = e.get_conflicted_name()
            if c_type == EConflictType.FILE:
                self.__tag_dialog.show_message(self.trUtf8("The filename - %s - is in conflict with an already existing tag. Please rename!" % c_name))
            elif c_type == EConflictType.TAG:
                self.__tag_dialog.show_message(self.trUtf8("The tag - %s - is in conflict with an already existing file" % c_name))
            else:
                self.trUtf8("A tag or item is in conflict with an already existing tag/item")
            #raise
        except InodeShortageException, e:
            self.__tag_dialog.show_message(self.trUtf8("The Number of free inodes is below the threshold of %s%" % e.get_threshold()))
            #raise
        except Exception, e:
            self.__tag_dialog.show_message(self.trUtf8("An error occurred while tagging"))
            raise
        else:
            ## 2 remove the item in the gui
            self.__tag_dialog.remove_item(item_name)
            self.__tag_dialog.hide_dialog()
    
    def __handle_tag_cancel(self):
        """
        the "postpone" button in the re-tag dialog has been clicked
        """
        self.emit(QtCore.SIGNAL("retag_cancel"))
        #self.__tag_dialog.hide_dialog()
    
    def show_tag_dialog(self):
        self.__tag_dialog.show_dialog()

    def hide_tag_dialog(self):
        self.__tag_dialog.hide_dialog()
    
    def set_parent(self, parent):
        """
        set the parent for the admin-dialog if there is already a gui window
        """
        self.__admin_dialog.set_parent(parent)
    
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

class ApplicationController(QtCore.QObject):
    """
    a small helper class to launch the retag-dialog as a standalone application
    this helper connects to the signals emitted by the retag controller and does the handling
    """
    def __init__(self, application, path, retag_mode, verbose):
        QtCore.QObject.__init__(self)
        
        self.LOG_LEVEL = logging.INFO
        if verbose:
            self.LOG_LEVEL = logging.DEBUG
        
        self.__log = LogHelper.get_app_logger(self.LOG_LEVEL)
        
        ## create a config object to get the registered store paths
        self.__main_config = ConfigWrapper(TsConstants.CONFIG_PATH)
        
        if self.__main_config is None:
            self.__log.info("No config file found for the given path")
            self.__handle_retag_error()
        else:
            self.__store_path = PathHelper.resolve_store_path(path, self.__main_config.get_store_path_list())
        
        self.__item_name = PathHelper.get_item_name_from_path(path)
        
        ## create the object
        self.__retag_widget = ReTagController(application, self.__store_path, self.__item_name, True, verbose_mode)
        ## connect to the signal(s)
        self.connect(self.__retag_widget, QtCore.SIGNAL("retag_cancel"), self.__handle_retag_cancel)
        self.connect(self.__retag_widget, QtCore.SIGNAL("retag_error"), self.__handle_retag_error)
        self.connect(self.__retag_widget, QtCore.SIGNAL("retag_success"), self.__handle_retag_success)
        ## start the retagging
        self.__retag_widget.start()
        
    def __handle_retag_error(self):
        """
        exit the program if there is an error
        """
        sys.exit(-1)
        
    def __handle_retag_success(self):
        """
        exit the application gracefully
        """
        sys.exit(0)

    def __handle_retag_cancel(self):
        """
        exit the application gracefully
        """
        sys.exit(0)
   
if __name__ == '__main__':  
  
    ## initialize and configure the optionparser
    usage = "\nThis program opens a dialog used for tagging an item placed in a tagstore directory."
    opt_parser = OptionParser("tagstore_tag.py -s <item_path>")
    opt_parser.add_option("-s", "--store", dest="store_path", help="absolute  or relative path to the item to be retagged")
    opt_parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="start programm with detailed output")

    (options, args) = opt_parser.parse_args()
    
    verbose_mode = False
    retag_mode = False
    dry_run = False
    
    store_name = None
    item_name = None
    
    if options.verbose:
        verbose_mode = True
    #if options.retag:
    #    retag_mode = True
    if options.store_path:
        store_path = options.store_path
    else:
        print "no store name given"
        opt_parser.print_help()
        sys.exit()
        
    tagstore_tag = QtGui.QApplication(sys.argv)
    tagstore_tag.setApplicationName("tagstore_retag")
    tagstore_tag.setOrganizationDomain("www.tagstore.org")
    tagstore_tag.UnicodeUTF8
    
    appcontroller = ApplicationController(tagstore_tag, store_path, True, verbose_mode)
    #tagstore_tag.connect(retag_widget, QtCore.SIGNAL("retag_error"), print("retag error caught in main"))
    
    tagstore_tag.exec_()
    
def quit_application():
    opt_parser.print_help()
    sys.exit()
## end