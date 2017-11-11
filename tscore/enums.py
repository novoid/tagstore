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


class Enum:
    def __init__(self, item_list):
        self.__data = dict()
        self.__uuid = 0
        for item in item_list:
            self.__data[item] = self.__uuid
            self.__uuid += 1

    def __getattr__(self, attribute):
        if not self.__data.has_key(attribute):
            raise AttributeError
        return self.__data[attribute]

    def get_enum(self, attribute):
        return self.__getattr__(attribute)
        
EFileEvent = Enum(["ADDED",
                   "RENAMED",
                   "REMOVED",
                   "ADDED_OR_RENAMED",
                   "REMOVED_OR_RENAMED"])

EFileType = Enum(["FILE",
                  "DIRECTORY"])

EConflictType = Enum(["FILE",
                  "TAG"])

ECategorySetting = Enum(["DISABLED",
                         "ENABLED",
                         "ENABLED_ONLY_PERSONAL",
                         "ENABLED_SINGLE_CONTROLLED_TAGLINE"])

EDateStampFormat = Enum(["DISABLED",
                  "MONTH",
                  "DAY"])

EOS = Enum(["Linux",
            "OSX",
            "Windows"])

ETagErrorEnum = Enum(["NO_DESCRIBING_TAG",
                      "NO_CATEGORIZING_TAG",
                      "LIMIT_EXCEEDED_DESRIBING_TAG",
                      "LIMIT_EXCEEDED_CATEGORIZING_TAG",
                      "NOT_ALLOWED_CHAR_DESCRIBING_TAG",
                      "NOT_ALLOWED_CHAR_CATEGORIZING_TAG",
                      "NOT_ALLOWED_DESCRIBING_TAG_NAME",
                      "NOT_ALLOWED_CATEGORIZING_TAG_NAME",
                      "NOT_DEFINED_CATEGORIZING_TAG_NAME",
                      "NO_ITEM_SELECTED",
                      "NO_ERROR"])


## end