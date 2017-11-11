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

import unittest
from tscore.tagwrapper import TagWrapper
from tscore.enums import EFileEvent, EFileType
from tscore.pendingchanges import PendingChanges
from tscore.configwrapper import ConfigWrapper
from tscore import pathhelper
from tscore.pathhelper import PathHelper
import datetime
from tscore.tsconstants import TsConstants
from tscore.tsrestrictions import TsRestrictions
from tsos.filesystem import FileSystemWrapper
from tscore.store import Store

class Test(unittest.TestCase):

    TAGFILE_NAME = "./.TESTSUITE_TAGFILE"

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_tagwrapper_file_exists(self):
        tag_wrapper = self.get_fresh_tagwrapper()
        assert(tag_wrapper.file_exists("testfile.txt"))
        
    def test_tagwrapper_write_and_get(self):
        
        tag_wrapper = self.get_fresh_tagwrapper()
        ## write new files to the tagfile, use one existing file, and a new one
        tag_wrapper.set_file("testfile.txt", ["test", "fest", "klest"])
        tag_wrapper.set_file("second_new_testfile", ["gnusmas", "fest", "DA", "tagger"])
        assert(tag_wrapper.file_exists("second_new_testfile"))
        assert(not tag_wrapper.file_exists("second"))


    def test_tagwrapper_popular(self):
        
        tag_wrapper = self.get_fresh_tagwrapper()
        
        tag_list = tag_wrapper.get_popular_tags(5)
        ## the tag with the name "DA" must be the most popular one
        assert(tag_list[0] == "MT")
        assert(tag_list[1] == "TUG")

    def test_tagwrapper_get_all_tags(self):
        tag_wrapper = self.get_fresh_tagwrapper()
        all_tags_list = tag_wrapper.get_all_tags()
        ## the test-tagfile has got 7 different tags
        assert(len(all_tags_list) == 7)
        

    def test_tagwrapper_remove_file_and_tags(self):
        tag_wrapper = self.get_fresh_tagwrapper()
        
        tag_wrapper.remove_file("testfile.txt")
        assert(not tag_wrapper.file_exists("testfile.txt"))
        
        tag_wrapper.remove_tag("TUG")
        assert("TUG" not in tag_wrapper.get_all_tags())
        
    def test_tagwrapper_rename_file_and_tag(self):
        ## rename_file method has been removed!
        ## TODO: reimplement the method or remove testcase AND substitute with a new one
        
        #tag_wrapper = self.get_fresh_tagwrapper()

        #tag_wrapper.rename_file("testfile.txt", "ricewind")
        #assert(tag_wrapper.file_exists("ricewind"))
        
        #tag_wrapper.rename_file("ricewind", "mort")
        #assert(tag_wrapper.file_exists("mort"))
        #assert(not tag_wrapper.file_exists("ricewind"))

        #tag_wrapper.rename_tag("dagger", "sword")
        #assert("sword" in tag_wrapper.get_all_tags())
        #assert("dagger" not in tag_wrapper.get_all_tags())
        pass
        
    def test_tagwrapper_recent(self):
        tag_wrapper = self.get_fresh_tagwrapper()
        
        tag_list = tag_wrapper.get_recent_files_tags(5)
        assert(len(tag_list) == 7)
        
        tag_list = tag_wrapper.get_recent_files_tags(1)
        assert("tagstore" not in tag_list)
        assert("TUG" in tag_list)
        
        tag_list = tag_wrapper.get_recent_tags(4)
        
        assert(len(tag_list) == 4)
        assert("dagger" not in tag_list)
        

    def test_configreader(self):
        config = ConfigWrapper("../tsresources/conf/tagstore.cfg")
        extensions = config.get_ignored_extension()
        
        assert(extensions == TsRestrictions.IGNORED_EXTENSIONS)
    
    def get_fresh_tagwrapper(self):
        ## at first create a new and clean tagfile in the current directory ...
        self.create_initial_tagfile()
        return TagWrapper(Test.TAGFILE_NAME)
    
    def create_initial_tagfile(self):
        """ helper method to create an empty tagfile
        for testing the tagwrapper
        """
        
        filename = Test.TAGFILE_NAME
        file = open(filename, "w")
        #file.writelines(content)
        
        id = "007"
        
        file.write("[store]\n")
        file.write("store_id=%s\n" % id)
        file.write("[files]\n")

        file.write("testfile.txt/tags=\"tag,tagger,dagger,MT\"\n")
        file.write("testfile.txt/timestamp=\"2010-08-20 18:14:55\"\n")
        
        file.write("masterthesis.tex/tags=\"MT,TUG,tagstore\"\n")
        file.write("masterthesis.tex/timestamp=\"2010-08-21 18:14:50\"\n")
        
        file.write("timesheet.csv/tags=\"MT,TUG,controll\"\n")
        file.write("timesheet.csv/timestamp=\"2010-08-22 18:14:55\"\n")
        
        file.write("[categories]\n")
        file.close()
    
    def test_pending_changes_append_remove(self):
        
        test = PendingChanges()
        test.register("new.txt", EFileType.FILE, EFileEvent.ADDED)
        test.register("new2.txt", EFileType.DIRECTORY, EFileEvent.ADDED_OR_RENAMED)
        test.register("new3.txt", EFileType.DIRECTORY, EFileEvent.ADDED_OR_RENAMED)
        
        assert("new.txt" == test.get_first()["file"])
        assert("new.txt" == test.get_first(True)["file"])
        assert("new2.txt" == test.get_first(True)["file"])
        
        test.register("new4.txt", EFileType.FILE, EFileEvent.ADDED)
        test.remove("new2.txt")
        test.remove("new3.txt")
        assert("new4.txt" == test.get_first(True)["file"])
        assert(None == test.get_first())
        
    def test_pending_changes_get_names(self):
        test = PendingChanges()
        test.register("new.txt", EFileType.FILE, EFileEvent.ADDED)
        test.register("new2.txt", EFileType.DIRECTORY, EFileEvent.ADDED_OR_RENAMED)
        test.register("new3.txt", EFileType.FILE, EFileEvent.REMOVED)
        test.remove("new2.txt")
        test.register("new4.txt", EFileType.FILE, EFileEvent.REMOVED)
        test.register("new3.txt", EFileType.FILE, EFileEvent.ADDED_OR_RENAMED)
        
        assert(["new.txt","new3.txt", "new4.txt"] == test.get_names())
        
        assert("new.txt" == test.get_added_names()[0])
        assert("new3.txt" == test.get_added_names()[1])
        assert("new4.txt" == test.get_removed_names()[0])

    def test_pending_changes_edit_item(self):
        test = PendingChanges()
        test.register("new.txt", EFileType.FILE, EFileEvent.ADDED)
        test.register("new2.txt", EFileType.DIRECTORY, EFileEvent.ADDED_OR_RENAMED)
        test.register("new3.txt", EFileType.FILE, EFileEvent.REMOVED)
        
        test.edit("new2.txt", "new4.txt")
        assert(["new.txt","new4.txt", "new3.txt"] == test.get_names())

    def test_configwrapper(self):
        #test = ConfigWrapper()
        pass
    
    def test_pathcompleter(self):
        
        store_path_list = []
        
        store_path_list.append("/Users/chris/teststore")
        store_path_list.append("/Users/chris/Documents/workspace/tagstore")
        store_path_list.append("/karl/Documents/workspace")
        store_path_list.append("/Users/wolfgang/Documents/workspace")
        
        item_path = "/Users/chris/teststore/navigation/test/item.txt"
        result = PathHelper.resolve_store_path(item_path, store_path_list)
        assert(result == "/Users/chris/teststore")
        item_name = PathHelper.get_item_name_from_path(item_path)
        assert(item_name == "item.txt")

        ## this one should produce a None result
        item_path = "/Users/chris/navigation/test/"
        result = PathHelper.resolve_store_path(item_path, store_path_list)
        assert(result is None)

        item_path = ("../../tagstore/tstest/__init__.py")
        result = PathHelper.resolve_store_path(item_path, store_path_list)
        assert(result == "/Users/chris/Documents/workspace/tagstore")
        item_name = PathHelper.get_item_name_from_path(item_path)
        assert(item_name == "__init__.py")
    
    def test_set_merge(self):
        
        set_1 = set(["hi", "you", "nerd"])
        set_2 = set(["i'm", "a", "geek"])
        
        set_3 = set_1.union(set_2)
        
        assert("geek" in set_3)
        
    def test_exiry_rename(self):
        """
        looks for expired items and moves & renames them to filename including tags in the expiry_directory
        """
        
        file_list = []
        
        file_list.append(dict(filename="my expired file.txt", tags=["hallo", "test"], category=["category"], timestamp=""))
        
        now = datetime.datetime.now()
        for file in file_list:
            file_extension = "." + file["filename"].split(".")[-1]
            file_name = file["filename"]
            file_name = file_name[:len(file_name)-len(file_extension)]
            new_filename = file_name + " - " + "; ".join(file["category"]) + " - " + "; ".join(file["tags"]) + file_extension
            
            assert(new_filename == "my expired file - category - hallo; test.txt")
            
    def test_create_store_move_and_delete_dir(self):
        
        """
        1. create a new store
        2. store a new item in the store - manually
        3. move the store to a new location
        4. delete the whole directory
        """
        
        filesystem = FileSystemWrapper()
        
        NEW_ITEM_NAME = "test_item"
        
        STORE_PATH = "./test_store/"
        STORAGE_DIR = "storage"
        
        store = self.create_new_store_object(STORE_PATH, STORAGE_DIR)
        
        ## place a new item in the store
        file_path = "%s%s/%s" % (STORE_PATH, STORAGE_DIR, NEW_ITEM_NAME)
        filesystem.create_file(file_path)
        config = ConfigWrapper("../tsresources/conf/tagstore.cfg")
        ## write the new store also to the config
        store_id = config.add_new_store(STORE_PATH)
        
        ## now tag it manually
        store.add_item_with_tags(NEW_ITEM_NAME, ["should", "not"], ["get", "this"])
        
        ## now the tag "should" must be a folde in the describing dir
#        path_to_check = "%sdescribing/should" % STORE_PATH
        path_to_check = "%sdescriptions/should" % STORE_PATH
        print path_to_check 
        assert(filesystem.is_directory(path_to_check))
        
        self.move_store("./test_store/", store_id, "./new_test_store/")
        self.remove_dir("./new_test_store/", store_id)
    
    def move_store(self, store_path, store_id, new_store_path):
        store = self.create_new_store_object(store_path, "storage")
        
        store.move(new_store_path)
        ## rewrite the config with the new store dir
        config = ConfigWrapper("../tsresources/conf/tagstore.cfg")
        config.rename_store(store_id, new_store_path)
        
        filesystem = FileSystemWrapper()
        
        assert(filesystem.is_directory(new_store_path))
    
    def remove_dir(self, store_path, store_id):
        
        filesystem = FileSystemWrapper()
        
        filesystem.delete_dir(store_path)
        
        config = ConfigWrapper("../tsresources/conf/tagstore.cfg")
        config.remove_store(store_id)

        assert(not filesystem.is_directory(store_path))

    def test_remove_store(self):
        """
        create a store
        create an item with tags in the store
        place a "not allowed" item in the navigation hierarchy
        call the "remove" method of the store
        check if everything has been removed properly
        """
        
        STORE_PATH = "./test_store/"
        STORAGE_DIR = "storage"
        NEW_ITEM_NAME = "test_item"
        
        store = self.create_new_store_object(STORE_PATH, STORAGE_DIR)
        
        filesystem = FileSystemWrapper()

         ## place a new item in the store
        file_path = "%s%s/%s" % (STORE_PATH, STORAGE_DIR, NEW_ITEM_NAME)
        filesystem.create_file(file_path)
        config = ConfigWrapper("../tsresources/conf/tagstore.cfg")
        ## write the new store also to the config
        store_id = config.add_new_store(STORE_PATH)
        ## now tag it manually
        store.add_item_with_tags(NEW_ITEM_NAME, ["should", "not"], ["get", "this"])
        
        ## create a new file in a tag-dir to test if it is removed as well
        file_path = "%s%s/%s" % (STORE_PATH, "descriptions/should", "i_should_not_be_here.file")
        filesystem.create_file(file_path)
        
        ## now remove the store 
        store.remove()
        ##check if this is done properly
        ##this one should not exist ...
        assert(not filesystem.path_exists(file_path))
        ## this path should still exist
        assert(filesystem.path_exists(STORE_PATH))

        self.remove_dir(STORE_PATH, store_id)
        assert(not filesystem.path_exists(STORE_PATH))

        config.remove_store(store_id)
        
    def test_split_path(self):
        dir = "/Users/chris/test_store/"
         ## prepare path for a split("/")        
        if dir[-1] == "/":
            dir = dir[:-1]
        ## check if new store name is a duplicate
        store_name = dir.split("/")[-1]
        
        assert(store_name == "test_store")

    def create_new_store_object(self, path, storage_dir_name):
        
        STORE_CONFIG_DIR = TsConstants.DEFAULT_STORE_CONFIG_DIR
        STORE_CONFIG_FILE_NAME = TsConstants.DEFAULT_STORE_CONFIG_FILENAME
        STORE_TAGS_FILE_NAME = TsConstants.DEFAULT_STORE_TAGS_FILENAME
        STORE_VOCABULARY_FILE_NAME = TsConstants.DEFAULT_STORE_VOCABULARY_FILENAME
        
        STORE_STORAGE_DIRS = [storage_dir_name]
#        STORE_DESCRIBING_NAV_DIRS = ["describing"]
        STORE_DESCRIBING_NAV_DIRS = []
#        STORE_CATEGORIZING_NAV_DIRS = ["categorizing"]
        STORE_CATEGORIZING_NAV_DIRS = []
        STORE_EXPIRED_DIRS = []
        STORE_NAVIGATION_DIRS = []
        
        filesystem = FileSystemWrapper()
        
        if not filesystem.is_directory(path):
            filesystem.create_dir(path)
       
        
        ## create a new store just in the test dir
        store = Store(5, path, 
              STORE_CONFIG_DIR + "/" + STORE_CONFIG_FILE_NAME,
              STORE_CONFIG_DIR + "/" + STORE_TAGS_FILE_NAME,
              STORE_CONFIG_DIR + "/" + STORE_VOCABULARY_FILE_NAME,
              STORE_NAVIGATION_DIRS,
              STORE_STORAGE_DIRS, 
              STORE_DESCRIBING_NAV_DIRS,
              STORE_CATEGORIZING_NAV_DIRS,
              STORE_EXPIRED_DIRS,
              "")
        store.init()
        return store

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
## end