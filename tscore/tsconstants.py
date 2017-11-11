#!/usr/bin/env python

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

from tsos.filesystem import FileSystemWrapper
from tscore.enums import EOS

class TsConstants(object):
    """
    class for providing internal used constants
    just do provide a single-point of access
    """
    
    CONFIG_DIR = "./tsresources/conf/"
    CONFIG_PATH = "./tsresources/conf/tagstore.cfg"
    
    LOGGER_NAME = "TagStoreLogger"
    LOG_FILENAME = "tagstore.log"
    LOG_BACKUP_COUNT = 3
    LOG_FILESIZE = 524288

    STORE_LOGGER_NAME = "StoreLogger"
    STORE_LOG_FILENAME = "store.log"
    
    ##overwrite settings path for windows, if the config exists in the AppData directory
    file_system = FileSystemWrapper()
    if file_system.get_os() == EOS.Windows:
        dir = file_system.get_user_profile_path()
        if file_system.path_exists(dir):
            CONFIG_DIR = dir + "/AppData/Local/tagstore"
            CONFIG_PATH = CONFIG_DIR + "/tagstore.cfg"
            LOG_FILENAME = dir + "/AppData/Local/tagstore/" + "tagstore.log"
    
    STORE_CONFIG_TEMPLATE_PATH = "./tsresources/conf/store.cfg.template"
    STORE_TAGFILE_TEMPLATE_PATH = "./tsresources/conf/store.tgs.template"

    #STORE_STORAGE_DIR_EN = "storage"#,Ablage"
    #STORE_DESCRIBING_NAVIGATION_DIR_EN = "navigation"#,Navigation"
    #STORE_CATEGORIZING_NAVIGATION_DIR_EN = "categorization"#,Kategorisierung"
    #STORE_EXPIRED_DIR_EN = "expired_items"#abgelaufene_Daten"
    
    SETTING_SUPPORTED_LANGUAGES = "supported_languages"
    SETTING_TAG_SEPARATOR = "tag_separator"
    SETTING_FACET_SEPARATOR = "facet_separator"
    
    SETTING_DATESTAMP_FORMAT = "datestamp_format"
    SETTING_DATESTAMP_HIDDEN = "datestamp_hidden"
    #SETTING_AUTO_DATESTAMP = "automatic_datestamp"
    
    #SETTING_CATEGORY_MANDATORY = "category_mandatory"
    SETTING_SHOW_CATEGORY_LINE = "show_category_line"
    SETTING_CATEGORY_MANDATORY = "category_mandatory"
    
    SETTING_VOCABULARY_CONFIGURABLE = "vocabulary_configurable"
    
    ## these constants are NOT used at the config file - it is a "gui setting name"
    SETTING_CATEGORY_VOCABULARY = "category_vocabulary"
    SETTING_ITEMS = "store_items"
    
    SETTING_DESC_TAGS = "describing_tags"
    SETTING_CAT_TAGS = "categorizing_tags"
    SETTING_FIRST_START = "first_start"
    SETTING_SHOW_WIZARD = "show_wizard"
    SETTING_CURRENT_LANGUAGE = "current_language"
    SETTING_SYNC_TAG = "sync_tag"
    SETTING_ANDROID_STORE ="android_store"
    SETTING_ANDROID_STORE_PATH="android_store_path"
    
    SETTING_ADDITIONAL_IGNORED_EXTENSIONS = "additional_ignored_extensions"
    
    SETTING_EXPIRY_PREFIX = "expiry_prefix"
    
    SETTING_SHOW_TAG_HELP = "show_tag_help"
    SETTING_SHOW_MY_TAGS_HELP = "show_my_tags_help"
    SETTING_SHOW_DATESTAMPS_HELP = "show_datestamps_help"
    SETTING_SHOW_EXPIRY_DATE_HELP = "show_expiry_date_help"
    SETTING_SHOW_RETAGING_HELP = "show_retagging_help"
    SETTING_SHOW_RENAME_TAGS_HELP = "show_rename_tags_help"
    SETTING_SHOW_STORE_MANAGEMENT_HELP = "show_store_management_help"
    SETTING_SHOW_SYNC_SETTINGS_HELP = "show_sync_settings_help"
    
    DATESTAMP_FORMAT_DAY = "%Y-%m-%d"
    DATESTAMP_FORMAT_MONTH = "%Y-%m"
    
    DEFAULT_EXPIRY_PREFIX = "exp_"
    DEFAULT_STORE_CONFIG_DIR = ".tagstore"
    DEFAULT_STORE_CONFIG_FILENAME = "store.cfg"
    DEFAULT_STORE_TAGS_FILENAME = "store.tgs"
    DEFAULT_STORE_SYNC_TAGS_FILENAME = "sync.tgs"
    DEFAULT_STORE_VOCABULARY_FILENAME = "vocabulary.txt"
    
    ## this file is created during a synchronization process
    DEFAULT_SYNCHRONIZATION_LOCKFILE_NAME = "tagstore.synchronization.lock"
    
    DEFAULT_RECENT_TAGS = 5
    DEFAULT_POPULAR_TAGS = 5
    DEFAULT_MAX_TAGS = 3
    DEFAULT_TAG_SEPARATOR = ","
    DEFAULT_FACET_SEPARATOR = "="
    DEFAULT_SUPPORTED_LANGUAGES = ["en", "de"]
    DEFAULT_ENCODING = "UTF-8"
    DEFAULT_FIRST_START = "true"
    DEFAULT_SHOW_WIZARD = "true"
    DEFAULT_VOCABULARY_CONFIGURABLE = "false"
    DEFAULT_SHOW_CATEGORY_LINE = 1
    DEFAULT_DATESTAMP_FORMAT = 1
    DEFAULT_DATESTAMP_HIDDEN = "false"
    DEFAULT_ADDITIONAL_IGNORED_EXTENSIONS = ""
    DEFAULT_SYNC_TAG = "android"
    
    DEFAULT_SHOW_TAG_HELP = "true"
    DEFAULT_SHOW_MY_TAGS_HELP = "true"
    DEFAULT_SHOW_DATESTAMPS_HELP ="true"
    DEFAULT_SHOW_EXPIRY_DATE_HELP ="true"
    DEFAULT_SHOW_RETAGING_HELP ="true"
    DEFAULT_SHOW_RENAME_TAGS_HELP ="true"
    DEFAULT_SHOW_STORE_MANAGEMENT_HELP ="true"
    DEFAULT_SHOW_SYNC_SETTINGS_HELP ="true"
    
    DEFAULT_MAX_CLOUD_TAGS = 20
    
    def __init__(self):
        pass
    
## end
