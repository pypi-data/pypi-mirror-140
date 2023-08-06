#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

class working_dir:
    def __init__(self, newdir):
        self.newdir = newdir
        self.olddir = os.getcwd()
    def __enter__(self):
        os.chdir(self.newdir)
        sys.path.insert(0, self.newdir)
        return self
    def __exit__(self, ex_type, ex_value, trace):
        os.chdir(self.olddir)
        sys.path.remove(self.newdir)