#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    import file
    file.start(os.path.dirname(os.path.abspath(__file__)))
