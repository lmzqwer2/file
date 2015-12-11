#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import textwrap
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os, re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import filetype
import chardet
import dir

from tornado.options import define, options
fileFolder = os.path.abspath(__file__).strip(__file__)
cssPath = os.path.join(fileFolder, "css")
jsPath = os.path.join(fileFolder, "js")
templatePath = os.path.join(fileFolder, 'templates')
baseFolder = os.getcwd()
downloadPath = baseFolder
RedirectH = tornado.web.RedirectHandler
settings = {
#    "static_path": os.path.join( os.path.dirname(__file__),"static"),
    'template_path': templatePath,
}

listenPort = 8080
UpperBoundSizeOfSingleUpload = 4 * 1024 * 1024
UpperBoundSizeOfDir = 64 * 1024 * 1024
UpperBoundFileNumberOfDir = 256
hostname = None
define("port", default=listenPort, help="run on the given port", type=int)
define("singlesize", default=UpperBoundSizeOfSingleUpload, help="limit of single upload", type=int)
define("dirsize", default=UpperBoundSizeOfDir, help="limit of dir size", type=int)
define("dirnum", default=UpperBoundFileNumberOfDir, help="limit of file number in dir", type=int)
define("hostname", default=hostname, help="hostname accepted by StaticFileHandler", type=str)
define("folder", default=downloadPath, help="root folder path of this program", type=str)

validUploadFileName = re.compile(r'^[^./\\<>|:"*?][^/\\<>|:"*?]*$')

class ViewHandler(tornado.web.RequestHandler):
    def initialize(self, path):
        self.absolute_path = path;

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = os.path.normpath(tornado.escape.url_unescape(path))
        words = path.split('/')
        words = filter(None,words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir,os.pardir):
                continue
            path = os.path.join(path,word)
        return path

    def get(self,path=''):
        path = './' + path
        path = path.strip('/')
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath) \
            or not expath.startswith(downloadPath):
            raise tornado.web.HTTPError(404)
        chainpath = dir.chain(path)
        chainpath[0]['name'] = 'LM file'
        if os.path.isdir(expath):
            if not self.request.path.endswith('/'):
                self.redirect(self.request.path+'/')
                return
            names = dir.list(expath)
            htmlrender = 'dir.html'
            if dir.upload(expath):
                htmlrender = 'upload.html'
            self.render(htmlrender, names=names, path=chainpath, info=dir.info(expath))
            return
        else:
            chainpath[-1]['url'] = chainpath[-1]['url'][:-1]
            info = filetype.filetype(expath)
            if info.get('readable', False):
                with open(expath, 'r') as f:
                    text = f.read();
                t = chardet.detect(text)
                if t['confidence'] > 0.9 and t['encoding'] != 'utf-8':
                    text = text.decode(t['encoding']).encode('utf-8')
                self.render("code.html", text=text, path=chainpath, ext=info, info=None)
                return
            else:
                self.redirect('/static' + self.request.path)
                return
        super(ViewHandler, self).get(path)

    def post(self, path=''):
        path = './' + path
        path = path.strip('/')
        print path
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath)\
            or not expath.startswith(downloadPath):
            raise tornado.web.HTTPError(404)
        contentlength = int(self.request.headers.get('Content-Length'))
        if dir.upload(expath) is not None \
            and dir.size(expath) < UpperBoundSizeOfDir \
            and dir.num(expath) < UpperBoundFileNumberOfDir \
            and contentlength is not None \
            and contentlength < UpperBoundSizeOfSingleUpload:
                file_metas=self.request.files.get('file', [])
                for meta in file_metas:
                    filename = meta['filename']
                    baseFolder = os.path.join(expath, filename)
                    if os.path.exists(baseFolder)\
                        or validUploadFileName.match(filename) is None:
                        continue
                    with open(baseFolder,'wb') as f:
                        f.write(meta['body'])
        self.redirect(self.request.path);

class StaticFH(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        host = self.request.headers.get('host')
        if hostname is not None \
            and host != hostname:
            return
        return super(StaticFH, self).validate_absolute_path(root, absolute_path)

class DownloadFH(StaticFH):
    def set_extra_headers(self, path):
        self.set_header('Content-Disposition', 'attachment;')

def generateFileApp():
    return tornado.web.Application(
        handlers=[
            (r'/download/', ViewHandler, dict(path=downloadPath)),
            (r'/download/(.*)/', ViewHandler, dict(path=downloadPath)),
            (r'/download/(.*)', DownloadFH, dict(path=downloadPath)),
            (r'/static/', ViewHandler, dict(path=downloadPath)),
            (r'/static/(.*)/', ViewHandler, dict(path=downloadPath)),
            (r'/static/(.*)', StaticFH, dict(path=downloadPath)),
            (r'/css/(.*)', StaticFH, dict(path=cssPath)),
            (r'/js/(.*)', StaticFH, dict(path=jsPath)),
            #(r'/(.*)/', ViewHandler, dict(path=downloadPath)),
            (r'/', ViewHandler, dict(path=downloadPath)),
            (r'/(.*)', ViewHandler, dict(path=downloadPath)),
        ],
        **settings
    )
app = generateFileApp()

def load():
    global UpperBoundSizeOfSingleUpload, UpperBoundSizeOfDir, UpperBoundFileNumberOfDir
    global listenPort, hostname, downloadPath
    global app
    tornado.options.parse_command_line()
    preHostname = hostname
    hostname = options.hostname
    listenPort = options.port
    UpperBoundSizeOfSingleUpload = options.singlesize
    UpperBoundSizeOfDir = options.dirsize
    UpperBoundFileNumberOfDir = options.dirnum
    downloadPath = os.path.join(baseFolder, options.folder)
    app = generateFileApp()

def status():
    print 'file: %s' % __file__
    print 'fileFolder: %s' % fileFolder
    print 'dir: %s' % baseFolder
    print 'jsPath: %s' % jsPath
    print 'cssPath: %s' % cssPath
    print 'folder: %s' % downloadPath
    print 'listen on: %d' % listenPort
    print 'hostname: %s' % hostname
    print 'single upload: %d' % UpperBoundSizeOfSingleUpload
    print 'dir size: %d' % UpperBoundSizeOfDir
    print 'dir num: %d' % UpperBoundFileNumberOfDir

def main(folderPath = fileFolder):
    global fileFolder, cssPath, jsPath, templatePath, settings
    fileFolder = folderPath
    cssPath = os.path.join(fileFolder, "css")
    jsPath = os.path.join(fileFolder, "js")
    templatePath = os.path.join(fileFolder, 'templates')
    settings = {
        'template_path': templatePath,
    }
    load()
    status()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(listenPort)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main(fileFolder)
