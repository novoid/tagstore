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

import os
import logging
import shutil
from stat import *
from PyQt4 import QtCore
from tscore.tsconstants import TsConstants
from tscore.enums import EDateStampFormat, ECategorySetting
from tscore.loghelper import LogHelper
from tsos.filesystem import FileSystemWrapper

class ConfigWrapper(QtCore.QObject):

    __pyqtSignals__ = ("changed()")

    GROUP_STORE_NAME = "store"
    KEY_STORE_ID = "store_id"

    def __init__(self, config_file_path):
        """
        constructor
        """
        QtCore.QObject.__init__(self)
        
        self.__config_file_path = config_file_path
        #this is the time of the last modification of the configfile
        self.__config_mtime = None
        
        self.__watcher = QtCore.QFileSystemWatcher(self)
        self.__watcher.addPath(config_file_path)
        self.__watcher.connect(self.__watcher,QtCore.SIGNAL("fileChanged(QString)"), self.__file_changed)
        self.__settings = QtCore.QSettings(config_file_path, QtCore.QSettings.IniFormat)
        
        self.__log = logging.getLogger(TsConstants.LOGGER_NAME)
    
    @staticmethod
    def create_store_config_file(file_path):
        """
        create a new store config file with the default settings provided in the app_config
        it just copies the template file to the new store config dir
        this  method has to be used in a static way
        """
        
        ## copy the config template to the new store config dir
        shutil.copyfile(TsConstants.STORE_CONFIG_TEMPLATE_PATH, file_path)
        """
        ## at first create the new file
        file = open(file_path, "w")
        file.write("[store]\n")
        file.write("store_id=0\n\n")
        file.write("[settings]\n")
        file.close()
        
        ## fill the config with defaulr settings
        store_conf_wrapper = ConfigWrapper(file_path)
        
        store_conf_wrapper.set_datestamp_format(self.get_datestamp_format())
        store_conf_wrapper.set_show_category_line(self.get_show_category_line())
        store_conf_wrapper.set_category_mandatory(self.get_category_mandatory())
        store_conf_wrapper.set_android_store(self.get_android_store())
        """
    @staticmethod
    def create_app_config_file(file_path):
        """
        create a new application config file structure in the given file
        this  method has to be used in a static way
        the file must be opened with write permission
        """
        file = open(file_path, "w")
        
        file.write("[settings]\n")
        file.write("store_config_directory=%s\n" % TsConstants.DEFAULT_STORE_CONFIG_DIR)
        file.write("store_config_filename=%s\n" % TsConstants.DEFAULT_STORE_CONFIG_FILENAME)
        file.write("store_tags_filename=%s\n" % TsConstants.DEFAULT_STORE_TAGS_FILENAME)
        file.write("store_vocabulary_filename=%s\n" % TsConstants.DEFAULT_STORE_VOCABULARY_FILENAME)
        file.write("tag_separator=\"%s\"\n" % TsConstants.DEFAULT_TAG_SEPARATOR)
        file.write("facet_separator=\"%s\"\n" % TsConstants.DEFAULT_FACET_SEPARATOR)
        file.write("supported_languages=\"en,de\"\n")
        file.write("current_language=de\n")
        file.write("show_category_line=%d\n" % TsConstants.DEFAULT_SHOW_CATEGORY_LINE)
        file.write("vocabulary_configurable=%d\n" % TsConstants.DEFAULT_VOCABULARY_CONFIGURABLE)
        file.write("datestamp_format=%s\n" % TsConstants.DEFAULT_DATESTAMP_FORMAT)
        file.write("datestamp_hidden=%d\n" % TsConstants.DEFAULT_DATESTAMP_HIDDEN)
        file.write("sync_tag=%d\n" % TsConstants.DEFAULT_SYNC_TAG)
        file.write("expiry_prefix=expiration\n")
        file.write("max_tags=5\n")
        file.write("num_popular_tags=5\n")
        file.write("additional_ignored_extensions=\"\"\n")
        ## store config defaults
        #file.write("datestamp_format=1\n")
        #file.write("show_category_line=1\n")
        #file.write("category_mandatory=false\n")

        file.write("[stores]\n")
        
        file.close()
    
    def print_store_config_to_log(self):
        pass
    
    def print_app_config_to_log(self):
        """
        take all application config parameters and put them into the logfile
        """
        self.__log.info("***************************************************************")
        self.__log.info("APPLICATION CONFIGURATION AT STARTUP")
        self.__log.info("***************************************************************")
        self.__log.info("[settings]")
        self.__log.info("store_config_directory=%s" % self.get_store_config_directory())
        self.__log.info("store_config_filename=%s" % self.get_store_configfile_name())
        self.__log.info("store_tags_filename=%s" % self.get_store_tagsfile_name())
        self.__log.info("store_vocabulary_filename=%s" % self.get_store_vocabularyfile_name())
        
        self.__log.info("tag_separator=\"%s\"" % self.get_tag_seperator())
        self.__log.info("facet_separator=\"%s\"" % self.get_facet_seperator())
        self.__log.info("supported_languages=%s" % self.get_supported_languages())
        self.__log.info("datestamp_format=%s" % self.get_datestamp_format())
        self.__log.info("datestamp_hidden=%s" % self.get_datestamp_hidden())
        self.__log.info("current_language=%s" % self.get_current_language())
        self.__log.info("show_category_line=%s" % self.get_show_category_line())
        self.__log.info("vocabulary_configurable=%s" % self.get_vocabulary_configurable())
        self.__log.info("expiry_prefix=%s" % self.get_expiry_prefix())
        self.__log.info("max_tags=%s" % self.get_max_tags())
        self.__log.info("num_popular_tags=%s" % self.get_num_popular_tags())
        self.__log.info("sync_tag=%s" % self.get_sync_tag())
        
        self.__log.info("show_wizard=%s" % self.get_show_wizard())
        self.__log.info("show_tag_help=%s" % self.get_show_tag_help())
        self.__log.info("show_my_tags_help=%s" % self.get_show_my_tags_help())
        self.__log.info("show_datestamps_help=%s" % self.get_show_datestamps_help())
        self.__log.info("show_expiry_date_help=%s" % self.get_show_expiry_date_help())
        self.__log.info("show_retagging_help=%s" % self.get_show_retagging_help())
        self.__log.info("show_rename_tags_help=%s" % self.get_show_rename_tags_help())
        self.__log.info("show_store_management_help=%s" % self.get_show_store_management_help())
        self.__log.info("show_sync_settings_help=%s" % self.get_show_sync_settings_help())
        self.__log.info("[stores]")
        self.__log.info("***************************************************************")
        self.__log.info("END - APPLICATION CONFIGURATION")
        self.__log.info("***************************************************************")
    
    def set_store_id(self, id):
        """
        writes the stores id to the configuration file
        """
        self.__settings.beginGroup(self.GROUP_STORE_NAME)
        self.__settings.setValue("store_id", id)
        self.__settings.endGroup()
    
    def get_store_id(self):
        """
        returns the store id of the current file to identify the store during rename
        """
        self.__settings.beginGroup(self.GROUP_STORE_NAME)
        id = unicode(self.__settings.value(self.KEY_STORE_ID, "").toString())
        self.__settings.endGroup()
        return id

    def __file_changed(self, signal_param):
        """
        event handler: called when file was changed
        """
        self.__settings.sync()
        
        # somehow, the config file to be watched gets lost in the self.__watcher object
        # so check everytime if there is a file to be watched
        # if not, just add it again to the watchlist 
        files = str(self.__watcher.files().join(","))
        if files == "":
            self.__watcher.addPath(self.__config_file_path)
        
        filesystem = FileSystemWrapper()
        if not filesystem.path_exists(self.__config_file_path):
            self.__log.debug("configwrapper - cannot find file anymore: %s" % self.__config_file_path)
            self.__watcher.removePath(self.__config_file_path)
            return
        
        config_file_props = os.stat(self.__config_file_path)
        tmp_mtime = config_file_props[ST_MTIME]
        
        # in case of the first start
        if self.__config_mtime is None:
            self.__config_mtime = tmp_mtime 
            return 
        
        if tmp_mtime != self.__config_mtime:
            self.__log.debug("configwrapper: file changed ... %s" % signal_param)
            self.__log.debug("old modified-time: %s, new: %s" % (self.__config_mtime, tmp_mtime))
            self.__config_mtime = tmp_mtime 
        
            self.emit(QtCore.SIGNAL("changed()"))
    
    def get_current_language(self):
        return self.__get_setting(TsConstants.SETTING_CURRENT_LANGUAGE)
     
    def get_store_config_directory(self):
        """
        returns the parameter: stores config directory name
        """
        directory = self.__get_setting("store_config_directory")
        return directory.strip("/")
        
    def get_store_tagsfile_name(self):
        """
        returns the parameter: stores config file name
        """
        config_file = self.__get_setting("store_tags_filename")
        return config_file.strip("/")

    def get_store_configfile_name(self):
        """
        returns the parameter: stores config file name
        """
        config_file = self.__get_setting("store_config_filename")
        return config_file.strip("/")
        
    def get_store_vocabularyfile_name(self):
        """
        returns the parameter: stores vocabulary file name
        """
        config_file = self.__get_setting("store_vocabulary_filename")
        return config_file.strip("/")
        
    def get_tag_seperator(self):
        """
        returns the parameter: tag separator for user interface 
        """
        return self.__get_setting("tag_separator")

    def get_facet_seperator(self):
        """
        returns the parameter: facet separator for user interface 
        """
        return self.__get_setting("facet_separator")

    def get_supported_languages(self):
        """
        returns a list of all supported languages
        """
        lang_string = self.__get_setting(TsConstants.SETTING_SUPPORTED_LANGUAGES)
        return lang_string.split(",")

    def get_additional_ignored_extension(self):
        """
        returns a list of all ignored file extensions
        """
        lang_string = self.__get_setting(TsConstants.SETTING_ADDITIONAL_IGNORED_EXTENSIONS)
        return lang_string.split(",")

    def set_expiry_prefix(self, setting_value):
        self.__put_setting(TsConstants.SETTING_EXPIRY_PREFIX, setting_value)
        
    def get_expiry_prefix(self):
        """
        returns the prefix to be used for marking the expiration dates of items
        """
        return self.__get_setting(TsConstants.SETTING_EXPIRY_PREFIX)
        
    def set_sync_tag(self, setting_value): 
        """
        stores the sync tag
        """
        self.__put_setting(TsConstants.SETTING_SYNC_TAG, setting_value)
        
    def get_sync_tag(self):
        """
        returns the sync tag whose associated files can be synced with other stores
        """
        return self.__get_setting(TsConstants.SETTING_SYNC_TAG)
    
    def set_android_store(self, setting_value):
        """
        stores setting if store is an android store
        """
        return self.__put_setting(TsConstants.SETTING_ANDROID_STORE, setting_value)
    
    def get_android_store(self):
        """
        returns setting if the current store is an android store
        """
        return self.__get_setting(TsConstants.SETTING_ANDROID_STORE)
    
    def get_android_store_path(self):
        """
        returns the android storage path
        """
        return self.__get_setting(TsConstants.SETTING_ANDROID_STORE_PATH)
    
    def set_android_store_path(self, setting_value):
        """
        stores setting of the android store path
        """
        return self.__put_setting(TsConstants.SETTING_ANDROID_STORE_PATH, setting_value)
    
    def get_datestamp_hidden(self):
        """
        returns "True" or "False" in case date-stamps are requested
        """
        if self.__get_setting(TsConstants.SETTING_DATESTAMP_HIDDEN) == "true":
            return True
        else:    
            return False

    def get_vocabulary_configurable(self):
        """
        returns "True" or "False" in case the vocabulary options are configurable
        """
        setting = self.__get_setting(TsConstants.SETTING_VOCABULARY_CONFIGURABLE)
        if setting == "true":
            return True
        else:    
            return False
    
    def get_datestamp_format(self):
        """
        returns the timestamp setting that should be used for tagging
        """
        setting_value = self.__get_setting(TsConstants.SETTING_DATESTAMP_FORMAT)        
        if setting_value == "":
            return 0
        return int(setting_value.strip())
    
    def set_datestamp_format(self, setting_value):
        self.__put_setting(TsConstants.SETTING_DATESTAMP_FORMAT, setting_value)

    def set_datestamp_hidden(self, setting_value):
        self.__put_setting(TsConstants.SETTING_DATESTAMP_HIDDEN, setting_value)

    def get_show_category_line(self):
        """
        returns the enum code if the category line should be enabled in the tag dialog
        """
        
        setting_value = self.__get_setting(TsConstants.SETTING_SHOW_CATEGORY_LINE)
        if setting_value == "":
            return 0
        return int(setting_value.strip())

    def set_show_category_line(self, setting_value):
        self.__put_setting(TsConstants.SETTING_SHOW_CATEGORY_LINE, setting_value)

    def set_category_mandatory(self, setting_value):
        self.__put_setting(TsConstants.SETTING_CATEGORY_MANDATORY, setting_value)

    def get_category_mandatory(self):
        """
        returns True if the category line should be enabled in the tag dialog
        """
        setting = self.__get_setting(TsConstants.SETTING_CATEGORY_MANDATORY)
        if setting == "true":
            return True
        else:    
            return False

    def __put_setting(self, setting_name, setting_value):
        """
        writes a new value to a specified setting
        """
        self.__settings.beginGroup("settings")
        value = self.__settings.setValue(setting_name, setting_value)
        self.__settings.endGroup()
        
    def __get_setting(self, setting_name):
        """
        helper method to switch directly to the settings group of the config file
        """
        self.__settings.beginGroup("settings")
        value = unicode(self.__settings.value(setting_name).toString())
        self.__settings.endGroup()
        return value.strip()
    
    def get_show_wizard(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_WIZARD)
        if value == "false":
            return False
        return True
    
    def set_show_wizard(self, show):
        """
        set to false if the wizard should not be shown anymore on activation of the tag dialog
        set to "true" if you want to re-activate the wizard
        """
        self.__put_setting(TsConstants.SETTING_SHOW_WIZARD, show)

    def get_first_start(self):
        value = self.__get_setting(TsConstants.SETTING_FIRST_START)
        if value == "false":
            return False
        return True
    
    def set_first_start(self, first_start):
        """
        set to false after the first start of tagstore
        set to "true" if you want to re-activate the first-start behaviour
        """
        self.__put_setting(TsConstants.SETTING_FIRST_START, first_start)

    def get_num_popular_tags(self):
        """
        returns the number of popular tags shown to the user
        """
        number = self.__get_setting("num_popular_tags")
        if number == "":
            return 0
        return int(number.strip())
    
        
    def get_max_tags(self):
        """
        returns the parameter: max_tags: the max allowed number of tags to enter 
        """
        number = self.__get_setting("max_tags")
        if number == "":
            return 0
        return int(number.strip())

    def get_store_path(self, id):
        """
        returns the path of a given store id
        """
        self.__settings.beginGroup("stores")
        path = unicode(self.__settings.value(id, "").toString())
        self.__settings.endGroup()
        return path.rstrip("/")

    def get_store_path_list(self):
        """
        returns a list of all configured store paths
        """
        
        store_path_list = []
        
        self.__settings.beginGroup("stores")
        store_id_list = self.__settings.childKeys()
        for id in store_id_list:
            store_path_list.append(self.__settings.value(id, "").toString())
        self.__settings.endGroup()
        
        return store_path_list

    def get_stores(self):
        """
        returns a list of store objects (directories) including the stores id and path
        """
        self.__settings.beginGroup("stores")
        store_ids = self.__settings.childKeys()
        stores = []
        for id in store_ids:
            path = unicode(self.__settings.value(id, "").toString()).rstrip("/")
            stores.append(dict(id=unicode(id), path=path))
        self.__settings.endGroup()
        return stores
    
    def get_store_ids(self):
        """
        returns a list of all stores ids
        """
        self.__settings.beginGroup("stores")
        store_ids = self.__settings.childKeys()
        self.__settings.endGroup()
        stores = []
        for id in store_ids:
            stores.append(unicode(id))
        return stores
    
    def rename_store(self, id, new_name):
        """
        resets a stores path
        """
        self.__settings.beginGroup("stores")
        self.__settings.setValue(id, new_name)
        self.__settings.endGroup()

    def remove_store(self, id):
        """
        removes a store entry from the config file
        """
        self.__settings.beginGroup("stores")
        self.__settings.remove(id)
        self.__settings.endGroup()
    
    def add_new_store(self, store_path):
        """
        just write the new store-path to the config file
        the store structure will be created automatically
        returns the newly created store_id
        """
        ## get the highest id
        new_id_int = 1 
        id_list = self.get_store_ids()
        if(len(id_list) > 0):
            max_id = max(self.get_store_ids())
            max_id_int = int(max_id.strip())
            new_id_int = max_id_int + 1
        
        self.__settings.beginGroup("stores")
        self.__settings.setValue(str(new_id_int), store_path)
        self.__settings.endGroup()
        
        return str(new_id_int)

    def set_show_tag_help(self, state):
        """
        set to false if the tag help should not be automatically shown
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_TAG_HELP, state)
        
    def get_show_tag_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_TAG_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_my_tags_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "My Tag" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_MY_TAGS_HELP, state)
        
    def get_show_my_tags_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_MY_TAGS_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_datestamps_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Datestamps" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_DATESTAMPS_HELP, state)
        
    def get_show_datestamps_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_DATESTAMPS_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_expiry_date_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Expiry Date" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_EXPIRY_DATE_HELP, state)
        
    def get_show_expiry_date_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_EXPIRY_DATE_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_retagging_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Re-Tagging" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_RETAGING_HELP, state)
        
    def get_show_retagging_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_RETAGING_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_rename_tags_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Rename Tags" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_RENAME_TAGS_HELP, state)
        
    def get_show_rename_tags_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_RENAME_TAGS_HELP)
        if value == "false":
            return False
        return True
    
    def set_show_store_management_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Store Management" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_STORE_MANAGEMENT_HELP, state)
        
    def get_show_store_management_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_STORE_MANAGEMENT_HELP)
        if value == "false":
            return False
        return True
   
    def set_show_sync_settings_help(self, state):
        """
        set to false if the automatic help should not be shown on selection 
        of the "Sync Settings" tab
        set to "true" if you want to re-activate
        """
        self.__put_setting(TsConstants.SETTING_SHOW_SYNC_SETTINGS_HELP, state)
        
    def get_show_sync_settings_help(self):
        value = self.__get_setting(TsConstants.SETTING_SHOW_SYNC_SETTINGS_HELP)
        if value == "false":
            return False
        return True
## end
