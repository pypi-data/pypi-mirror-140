#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

class working_dir:
    def __init__(self, newdir):
        self.newdir = newdir
        self.olddir = os.getcwd()
    def __enter__(self):
        os.chdir(self.newdir)
        return self
    def __exit__(self, ex_type, ex_value, trace):
        os.chdir(self.olddir)