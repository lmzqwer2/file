#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import os
import filetype
import chardet
import config

def chain(path):
    '''
    break a unix like path @path into array.
    each cell of this array contains two key
        @url    the absolute path of current place
        @name   the folder or file name

    >>> chain("/path/to/some/file")
    [{'url': '/', 'name': ''}, {'url': '/path/', 'name': 'path'}, {'url': '/path/to/', 'name': 'to'}, {'url': '/path/to/some/', 'name': 'some'}, {'url': '/path/to/some/file/', 'name': 'file'}]
    >>> chain("./relative/file/path")
    [{'url': '/', 'name': ''}, {'url': '/relative/', 'name': 'relative'}, {'url': '/relative/file/', 'name': 'file'}, {'url': '/relative/file/path/', 'name': 'path'}]
    >>> chain("")
    [{'url': '/', 'name': ''}]
    >>> chain(".")
    [{'url': '/', 'name': ''}]
    '''
    folder = path.split('/')
    if folder[0]=='.':
        folder[0] = ''
    L = []
    link = ''
    for item in folder:
        link += item + '/'
        L.append(dict(name=item, url=link))
    return L

def exists(path, file):
    '''
    check the existence of @file at @path
    if @path is a file, just try to find @file as its silbing.
    if found @file
        return the relative path to @file base on @path
    else
        return None

    >>> exists("./.test_dir_py", ".info")
    './.test_dir_py/.info'
    >>> exists("./.test_dir_py/.info", ".upload")
    './.test_dir_py/.upload'
    >>> exists("./.test_dir_py", "NoFoundFile.py") # the return value, None

    >>> exists("./.test_dir_py/NotFoundFolder", ".info") # the return value, None

    >>> exists("./.test_dir_py/", "emptyFolder") # check a folder, None

    >>> exists("./.test_dir_py/../.test_dir_py/emptyFolder/../..", ".test_dir_py/.upload")
    './.test_dir_py/../.test_dir_py/emptyFolder/../../.test_dir_py/.upload'
    '''
    if os.path.isfile(path):
        path = os.path.dirname(path)
    filename = os.path.join(path, file)
    if os.path.isfile(filename):
        return filename
    return None

def size(path):
    '''
    check the size of @path
    if @path is file
        return its size
    elseif @path is folder
        return sum of all its directly chilren file size
    else
        return -1

    >>> size("./.test_dir_py/")
    47L
    >>> size("./.test_dir_py/.info")
    21
    >>> size("./.test_dir_py/.upload")
    17
    >>> size("./.test_dir_py/emptyFolder")
    0L
    >>> size("./.test_dir_py/NotFoundFolder")
    -1
    '''
    if os.path.isfile(path):
        return os.path.getsize(path)
    if os.path.isdir(path):
        size = 0L
        for root, dirs, files in os.walk(path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size
    return -1

def num(path):
    '''
    check the file and folder number in a folder.
    regard a path to file as a one file folder.

    >>> num("./.test_dir_py")
    4
    >>> num("./.test_dir_py/emptyFolder")
    0
    >>> num("./.test_dir_py/.info")
    1
    >>> num("./.test_dir_py/NotFoundFolder")
    0
    '''
    if os.path.isfile(path):
        return 1
    if os.path.isdir(path):
        return len(os.listdir(path))
    return 0

def info(path):
    '''
    check the infomation file of a folder
    if exists then return its content, already cut into array by paragraph.
    else return None.

    >>> info("./.test_dir_py")
    ['Welcome!', 'Dir testing.']
    >>> info("./.test_dir_py/emptyFolder") # None

    '''
    infoname = exists(path, '.info')
    if infoname:
        L = []
        with open(infoname, 'r') as f:
            for line in f.readlines():
                L.append(line.strip("\n"))
        return L
    return None

def upload(path):
    '''
    check the target folder is uploadable or not.
    specified by the file named ".upload" in that folder.

    >>> upload("./.test_dir_py")
    True
    >>> upload("./.test_dir_py/emptyFolder")
    False
    '''
    uploadname = exists(path, '.upload')
    if uploadname is not None:
        return True
    return False

def status(path):
    '''
    return the status of the given @path

    >>> status("./.test_dir_py/")
    {'info': ['Welcome!', 'Dir testing.'], 'link': '/', 'name': '/', 'exists': True, 'type': {'ext': '', 'readable': False, 'js': None}, 'filetype': 'dir', 'isfile': False, 'upload': True}
    >>> status("./.test_dir_py/emptyFolder")
    {'link': 'emptyFolder/', 'name': 'emptyFolder/', 'exists': True, 'type': {'ext': 'emptyfolder', 'readable': False, 'js': None}, 'filetype': 'dir', 'isfile': False, 'upload': False}
    >>> status("./.test_dir_py/.info")
    {'link': '.info', 'name': '.info', 'exists': True, 'type': {'ext': 'info', 'readable': True, 'js': None}, 'filetype': 'file', 'isfile': True, 'size': 21}
    >>> status("./.test_dir_py/NotFoundFolder")
    {'exists': False}
    '''
    if not os.path.exists(path):
        return dict(
            exists = False
        )
    (filepath, filename) = os.path.split(path)
    isfile = os.path.isfile(path)
    linkname = filename + ('/' if not isfile else '')
    displayname = linkname + ('@' if os.path.islink(path) else '')
    filetypename = 'file' if isfile else 'dir'
    d = dict(
        exists = True,
        isfile = isfile,
        link = linkname,
        name = displayname,
        filetype = filetypename,
        type = filetype.filetype(path),
    )
    if isfile:
        d['size'] = size(path)
    else:
        textinfo = info(path)
        if textinfo is not None:
            d['info'] = textinfo
        d['upload'] = upload(path)
    return d

def list(path):
    '''
    return a list of the files and folders in @path.
    Any file or folder start with '.' would be ignored.
    retuan an empty array as answer when path point to a file.

    >>> list("./.test_dir_py")
    [{'link': 'emptyFolder/', 'name': 'emptyFolder/', 'exists': True, 'type': {'ext': 'emptyfolder', 'readable': False, 'js': None}, 'filetype': 'dir', 'isfile': False, 'upload': False}, {'link': 'normalName', 'name': 'normalName', 'exists': True, 'type': {'ext': 'normalname', 'readable': True, 'js': None}, 'filetype': 'file', 'isfile': True, 'size': 9}]
    >>> list("./.test_dir_py/emptyFolder")
    []
    >>> list("./.test_dir_py/.upload")
    []
    '''
    if os.path.isfile(path):
        return []
    dir = os.listdir(path)
    folder = []
    file = []
    for name in dir:
        if name.startswith('.'):
            continue
        fullname = os.path.join(path, name)
        d = status(fullname)
        if d.get('isfile', False):
            file.append(d)
        else:
            folder.append(d)
    return folder + file

def get(expath, path):
    '''
    return the more detail of the @expath with relative @path

    >>> path = os.getcwd()
    >>> def callGet(relpath):
    ...     return get(os.path.join(path, relpath), relpath)
    >>> callGet("./.test_dir_py")
    {'info': ['Welcome!', 'Dir testing.'], 'list': [{'link': 'emptyFolder/', 'name': 'emptyFolder/', 'exists': True, 'type': {'ext': 'emptyfolder', 'readable': False, 'js': None}, 'filetype': 'dir', 'isfile': False, 'upload': False}, {'link': 'normalName', 'name': 'normalName', 'exists': True, 'type': {'ext': 'normalname', 'readable': True, 'js': None}, 'filetype': 'file', 'isfile': True, 'size': 9}], 'chain': [{'url': '/', 'name': 'LM file'}, {'url': '/.test_dir_py/', 'name': '.test_dir_py'}], 'link': '.test_dir_py/', 'name': '.test_dir_py/', 'exists': True, 'type': {'ext': 'test_dir_py', 'readable': False, 'js': None}, 'filetype': 'dir', 'isfile': False, 'upload': True}
    >>> callGet("./.test_dir_py/.info")
    {'link': '.info', 'name': '.info', 'exists': True, 'type': {'ext': 'info', 'readable': True, 'js': None}, 'filetype': 'file', 'isfile': True, 'chain': [{'url': '/', 'name': 'LM file'}, {'url': '/.test_dir_py/', 'name': '.test_dir_py'}, {'url': '/.test_dir_py/.info', 'name': '.info'}], 'size': 21}
    >>> callGet("./.test_dir_py/NotFoundFolder")
    {'exists': False}
    '''
    selfdict = status(expath)
    if selfdict['exists']:
        if not selfdict['isfile']:
            selfdict['list'] = list(expath)
        chainpath = chain(path)
        chainpath[0]['name'] = config.root
        if selfdict['isfile']:
            chainpath[-1]['url'] = chainpath[-1]['url'][:-1]
        selfdict['chain'] = chainpath
    return selfdict

if __name__ == '__main__':
    testFolder = './.test_dir_py'
    uploadFile = os.path.join(testFolder, ".upload")
    infoFile = os.path.join(testFolder, ".info")
    normalFile = os.path.join(testFolder, "normalName")
    emptyFolder = os.path.join(testFolder, "./emptyFolder")

    # before testing, preparing a folder with some file.
    os.mkdir(testFolder);
    with open(uploadFile, 'w') as f:
        f.write("non-sense content");
    with open(infoFile, 'w') as f:
        f.write("Welcome!\n")
        f.write("Dir testing.")
    with open(normalFile, 'w') as f:
        f.write("Nothing!\n")
    os.mkdir(emptyFolder);

    # begin to test
    import doctest
    print __file__
    print doctest.testmod()

    # clean all file and folder
    os.remove(uploadFile)
    os.remove(infoFile)
    os.remove(normalFile)
    os.rmdir(emptyFolder)
    os.rmdir(testFolder)
