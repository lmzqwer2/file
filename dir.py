import os

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

def list(path):
    '''
    return a list of the files and folders in @path.
    Any file or folder start with '.' would be ignored.
    retuan an empty array as answer when path point to a file.

    >>> list("./.test_dir_py")
    [('emptyFolder/', 'emptyFolder/', 'dir'), ('normalName', 'normalName', 'file')]
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
        fullname = os.path.join(path,name)
        if os.path.isdir(fullname):
            displayname = name + '/'
            linkname = name + '/'
            filetype = 'dir'
            folder.append((linkname,displayname,filetype))
            continue
        displayname = linkname = name
        filetype = 'file'
        if os.path.islink(fullname):
            displayname = name + '@'
            filetype = 'link'
        file.append((linkname,displayname,filetype))
    return folder + file


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
