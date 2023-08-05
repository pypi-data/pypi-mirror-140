#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import unittest
from nokogiri.working_dir import working_dir
import os

class test_working_dir(unittest.TestCase):
    def test_cwdが変更される(self):
        targetdir = "/tmp"
        with working_dir(targetdir):
            newdir = os.getcwd()
        self.assertEqual(targetdir, newdir)

    def test_cwdが元に戻る(self):
        beforedir = os.getcwd()
        with working_dir("/tmp"):
            pass
        afterdir = os.getcwd()
        self.assertEqual(beforedir, afterdir)
            

if __name__ == '__main__':
    unittest.main()
