#!/usr/bin/env python
from tscore.tsconstants import TsConstants

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
'''
A helper class for conveniently getting the current PID or checking if a given PID currently exists 
'''

import logging
import os
import sys
import errno
if sys.platform[:3] == "win":
    import win32api
    import win32con


from tscore.loghelper import LogHelper

class PidHelper(object):
    '''
    classdocs
    '''
    

    def __init__(self, params):
        '''
        Constructor
        '''
    
    @staticmethod
    def get_current_pid():
        """
        returns the PID of the current process
        """
        pid = os.getpid()
        return pid
        
    @staticmethod
    def pid_exists(pid):
        """
        check if the given pid number is an currently running process
        """
        LOG = LogHelper.get_app_logger(logging.INFO)

        if pid != None and pid == "android":
            # android serialization workaround
            return True

        if sys.platform[:3] == "win":

            # check if process exists
            hProc = None
            try:
                hProc = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, int(pid))
            except Exception:
                LOG.info("exception while quering")
                return False
            finally:
                if hProc != None:
                    # close handle the process exist
                    LOG.info("process exists %s handle ", pid)
                    win32api.CloseHandle(hProc)
                    return True
                else:
                    LOG.info("process failed to get handle")
                    return False
            
        try:
            # the second parameter is the signal code
            # If sig is 0, then no signal is sent, but error checking is still performed.
            # if "os.kill" throws no exception, the process exists
            os.kill(int(pid), 0)
            # if no exception is thrown kill the current process
            return True 
        except OSError, e:
            # the process with the provided pid does not exist enymore
            # so an exception is thrown
            # ESRCH means "no such process"
            print errno.ESRCH 
            if e.errno == errno.ESRCH:
                return False
            else:
                raise

## end     
