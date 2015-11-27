#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
fileFolder = os.path.split(os.path.abspath(__file__))[0]

def run():
    import file
    file.main(fileFolder)

if __name__ == '__main__':
    run()
