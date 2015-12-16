#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import os, re
import tornado

from tornado.options import define, options

define("folder", default = os.getcwd(), type=str,
 	help="root folder path of this program. Defaultly set to current folder.")

define("port", default = 8080, type=int,
    help="run on the given port")
define("hostname", default = None, type=str,
    help="valid hostname when access static file")

define("singlesize", default = 4 * 1024 * 1024, type=int,
    help="limit of single upload")
define("dirsize", default = 64 * 1024 * 1024, type=int,
    help="limit of directory size")
define("dirnum", default = 256, type=int,
    help="limit of file number in directory")

define("config", type=str,
    callback=lambda path: options.parse_config_file(path, final=False),
    help="path to config file")

define("root", default = "LM file", type=str,
    help="the name of root directory")

validUploadFileName = re.compile(r'^[^./\\<>|:"*?][^/\\<>|:"*?]*$')

options.parse_command_line()
hostname = options.hostname
port = options.port

UpperBoundSizeOfSingleUpload = options.singlesize
UpperBoundSizeOfDir = options.dirsize
UpperBoundFileNumberOfDir = options.dirnum

baseFolder = os.getcwd()
relativeFolder = os.path.expandvars(os.path.expanduser(options.folder))
folder = os.path.abspath(os.path.join(baseFolder, relativeFolder))

root = options.root

fileFolder = None
cssPath = None
jsPath = None
templatePath = None

def changeFileFolder(path):
    global fileFolder, cssPath, jsPath, templatePath
    fileFolder = os.path.abspath(path)
    cssPath = os.path.join(fileFolder, "css")
    jsPath = os.path.join(fileFolder, "js")
    templatePath = os.path.join(fileFolder, 'templates')

def show():
    print 'current directory: %s' % baseFolder
    print 'display folder: %s' % folder
    print
    print 'fileFolder: %s' % fileFolder
    print 'jsPath: %s' % jsPath
    print 'cssPath: %s' % cssPath
    print 'templatePath: %s' % templatePath
    print
    print 'listen port: %d' % port
    print 'hostname: %s' % hostname
    print
    print 'dir num: %d' % UpperBoundFileNumberOfDir
    print 'dir size: %d' % UpperBoundSizeOfDir
    print 'single upload: %d' % UpperBoundSizeOfSingleUpload
    print
    print 'root folder name: %s' % root

if __name__ == '__main__':
	changeFileFolder(os.path.dirname(os.path.abspath(__file__)))
	show()
