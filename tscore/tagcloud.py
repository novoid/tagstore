#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
## this file is part of tagstore, an alternative way of storing and retrieving information
## Copyright (C) 2010  Karl Voit, Georg Schober
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


class TagCloud():
    '''
    classdocs
    '''


    def __init__(self):
        self.__NUM_OF_SIZES = 4.0
        
    
    def create_tag_cloud(self, dict):
        
        dictionary = dict.copy()
        number_of_tags = 0;
        for tag_name, counter in dictionary.iteritems():
       
            number_of_tags += counter
        if len(dictionary) > 0:
            max_value = max(dictionary.values())
            min_value = min(dictionary.values())
            if  len(dictionary) > 1 and max_value != min_value:
                num = (max_value - min_value) / self.__NUM_OF_SIZES
            else:
                num = (max_value) / self.__NUM_OF_SIZES

            dictionary = self.get_font_size(dictionary, max_value, number_of_tags)
        return dictionary   

    def get_font_size(self, dictionary, max_value, number_of_tags):
        for tag_name, num in dictionary.iteritems():
            counter = 3 * self.__NUM_OF_SIZES
            while (num) < max_value and counter != 0:
                num += self.__NUM_OF_SIZES
                counter -= 3
            dictionary[tag_name] = counter
        #print dictionary
        return dictionary

## end   
        