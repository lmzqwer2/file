#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'lmzqwer2'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import textwrap
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os, re, json
import filetype
import chardet
import dir
import config

class ViewHandler(tornado.web.RequestHandler):
    def initialize(self, path = config.folder):
        self.absolute_path = path;

    def get(self,path=''):
        path = './' + path
        path = path.strip('/')
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath) \
            or not expath.startswith(self.absolute_path):
            raise tornado.web.HTTPError(403)
        if os.path.isdir(expath):
            # a valid folder's url should always end with '/'
            # or the relative link would miss its place.
            if not self.request.path.endswith('/'):
                self.redirect(self.request.path+'/')
                return
        d = dir.get(expath, path)
        self.render('index.html', d=d)
        return

    def post(self, path=''):
        path = './' + path
        path = path.strip('/')
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath)\
            or not expath.startswith(self.absolute_path):
            raise tornado.web.HTTPError(403)
        contentlength = int(self.request.headers.get('Content-Length'))
        if dir.upload(expath) is not None \
            and dir.size(expath) < config.UpperBoundSizeOfDir \
            and dir.num(expath) < config.UpperBoundFileNumberOfDir \
            and contentlength is not None \
            and contentlength < config.UpperBoundSizeOfSingleUpload:
                file_metas = self.request.files.get('file', [])
                for meta in file_metas:
                    filename = meta['filename']
                    fileLocation = os.path.join(expath, filename)
                    if os.path.exists(fileLocation)\
                        or config.validUploadFileName.match(filename) is None:
                        continue
                    with open(fileLocation,'wb') as f:
                        f.write(meta['body'])
        self.redirect(self.request.path);

class TextHandler(tornado.web.RequestHandler):
    def initialize(self, path = config.folder):
        self.absolute_path = path;

    def get(self, path):
        path = './' + path
        path = path.strip('/')
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath) \
            or not expath.startswith(self.absolute_path):
            raise tornado.web.HTTPError(403)
        d = dir.status(expath)
        info = filetype.filetype(expath)
        if info.get('readable', False):
            with open(expath, 'r') as f:
                text = f.read();
            t = chardet.detect(text)
            if t['confidence'] > 0.9 and t['encoding'] != 'utf-8':
                text = text.decode(t['encoding']).encode('utf-8')
            self.write(text)
        else:
            self.write(json.dumps(dict(
                readable = False
            )))
        self.finish()
        return

class APIhandler(tornado.web.RequestHandler):

    def initialize(self, path = config.folder):
        self.absolute_path = path;

    def get(self,path=''):
        path = './' + path
        path = path.strip('/')
        expath = os.path.join(self.absolute_path, path)
        d = dir.get(expath, path)
        self.write(d)
        self.finish()


class StaticFH(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        host = self.request.headers.get('host')
        if config.hostname is not None \
            and host != config.hostname:
            return
        return super(StaticFH, self).validate_absolute_path(root, absolute_path)

class DownloadFH(StaticFH):
    def set_extra_headers(self, path):
        self.set_header('Content-Disposition', 'attachment;')

def generateFileApp():
    settings = {
        'template_path': config.templatePath,
    }
    return tornado.web.Application(
        handlers=[
            (r'/download/', ViewHandler),
            (r'/download/(.*)/', ViewHandler),
            (r'/download/(.*)', DownloadFH, dict(path=config.folder)),
            (r'/static/', ViewHandler),
            (r'/static/(.*)/', ViewHandler),
            (r'/static/(.*)', StaticFH, dict(path=config.folder)),
            (r'/text/', TextHandler),
            (r'/text/(.*)', TextHandler),
            (r'/css/(.*)', StaticFH, dict(path=config.cssPath)),
            (r'/js/(.*)', StaticFH, dict(path=config.jsPath)),
            (r'/api', APIhandler),
            (r'/api/(.*)', APIhandler),
            #(r'/(.*)/', ViewHandler),
            (r'/', ViewHandler),
            (r'/(.*)', ViewHandler),
        ],
        **settings
    )

def start(path):
    config.changeFileFolder(path)
    config.show()
    app = generateFileApp()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(config.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start(os.path.dirname(os.path.abspath(__file__)))
