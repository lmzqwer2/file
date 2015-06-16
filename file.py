import textwrap
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import os
import filetype

from tornado.options import define, options
filepath = os.path.abspath(__file__).strip(__file__)
#filepath = '/svr/file/'
downloadpath = os.path.join(filepath, "file")
csspath = os.path.join(filepath, "css")
jspath = os.path.join(filepath, "js")
templatepath = os.path.join(filepath, 'templates')
RedirectH = tornado.web.RedirectHandler
settings = {
#    "static_path": os.path.join( os.path.dirname(__file__),"static"),
    'template_path': templatepath,
}

listenport = 8080
UpperBoundSizeOfSingleUpload = 4 * 1024 * 1024
UpperBoundSizeOfDir = 64 * 1024 * 1024
UpperBoundFileNumberOfDir = 256
hostname = 'localhost:8080'
define("port", default=listenport, help="run on the given port", type=int)
define("singlesize", default=UpperBoundSizeOfSingleUpload, help="limit of single upload", type=int)
define("dirsize", default=UpperBoundSizeOfDir, help="limit of dir size", type=int)
define("dirnum", default=UpperBoundFileNumberOfDir, help="limit of file number in dir", type=int)
define("hostname", default=hostname, help="limit of file number in dir", type=str)

class dir(object):
    @classmethod
    def chain(cls, path):
        folder = path.split('/')
        if folder[0]=='.':
            folder[0] = ''
        L = []
        link = ''
        for item in folder:
            link += item + '/'
            L.append(dict(name=item, url=link))
        return L

    @classmethod
    def exists(cls, path, file):
        if os.path.isfile(path):
            path = os.path.dirname(path)
        filename = os.path.join(path, file)
        if os.path.isfile(filename):
            return filename
        return None

    @classmethod
    def size(cls, path):
        if os.path.isfile(path):
            return os.path.getsize(path)
        if os.path.isdir(path):
            size = 0L
            for root, dirs, files in os.walk(path):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
            return size
        return -1

    @classmethod
    def num(cls, path):
        if os.path.isfile(path):
            return 1
        if os.path.isdir(path):
            return len(os.listdir(path))
        return 0

    @classmethod
    def info(cls, path):
        infoname = cls.exists(path, '.info')
        if infoname:
            with open(infoname, 'r') as f:
                return f.readlines()
        return None

    @classmethod
    def upload(cls, path):
        uploadname = cls.exists(path, '.upload')
        if uploadname is not None:
            return True
        return False

class ViewHandler(tornado.web.RequestHandler):
    def initialize(self, path):
        self.absolute_path = path;

    def translate_path(self,path):
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

    def list_directory(self,path):
        dir = os.listdir(path)
        folder = []
        file = []
        for name in dir:
            if name.startswith('.'):
                continue
            fullname = os.path.join(path,name)
            displayname = linkname = name
            filetype = 'file'
            if os.path.isdir(fullname):
                displayname = name + '/'
                linkname = name + '/'
                filetype = 'dir'
                folder.append((linkname,displayname,filetype))
                continue
            if os.path.islink(fullname):
                displayname = name + '@'
                filetype = 'link'
            file.append((linkname,displayname,filetype))
        return folder + file

    def get(self,path=''):
        path = './' + path
        path = path.strip('/')
        print path
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath) \
            or not expath.startswith(downloadpath):
            raise tornado.web.HTTPError(404)
        chainpath = dir.chain(path)
        chainpath[0]['name'] = 'LM file'
        if os.path.isdir(expath):
            if not self.request.path.endswith('/'):
                self.redirect(self.request.path+'/')
                return
            names = self.list_directory(expath)
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
            or not expath.startswith(downloadpath):
            raise tornado.web.HTTPError(404)
        contentlength = int(self.request.headers.get('Content-Length'))
        if dir.upload(expath) is not None \
            and dir.size(expath) < UpperBoundSizeOfDir \
            and dir.num(expath) < UpperBoundFileNumberOfDir \
            and contentlength is not None \
            and contentlength < UpperBoundSizeOfSingleUpload:
                file_metas=self.request.files.get('file', [])
                for meta in file_metas:
                    filename = meta['filename'].lstrip('.')
                    filepath = os.path.join(expath, filename)
                    if os.path.exists(filepath):
                        continue
                    with open(filepath,'wb') as f:
                        f.write(meta['body'])
        self.redirect(self.request.path);

class StaticFH(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        host = self.request.headers.get('host')
        if host is None \
            or host != hostname:
            return
        print absolute_path
        return super(StaticFH, self).validate_absolute_path(root, absolute_path)

class DownloadFH(StaticFH):
    def set_extra_headers(self, path):
        self.set_header('Content-Disposition', 'attachment;')

app = tornado.web.Application(
    handlers=[
        (r'/download/', ViewHandler, dict(path=downloadpath)),
        (r'/download/(.*)/', ViewHandler, dict(path=downloadpath)),
        (r'/download/(.*)', DownloadFH, dict(path=downloadpath)),
        (r'/static/', ViewHandler, dict(path=downloadpath)),
        (r'/static/(.*)/', ViewHandler, dict(path=downloadpath)),
        (r'/static/(.*)', StaticFH, dict(path=downloadpath)),
        (r'/css/(.*)', StaticFH, dict(path=csspath)),
        (r'/js/(.*)', StaticFH, dict(path=jspath)),
        #(r'/(.*)/', ViewHandler, dict(path=downloadpath)),
        (r'/', ViewHandler, dict(path=downloadpath)),
        (r'/(.*)', ViewHandler, dict(path=downloadpath)),
    ],
    **settings
)

def load():
    global listenport, UpperBoundSizeOfSingleUpload, UpperBoundSizeOfDir, UpperBoundFileNumberOfDir, hostname
    tornado.options.parse_command_line()
    listenport = options.port
    UpperBoundSizeOfSingleUpload = options.singlesize
    UpperBoundSizeOfDir = options.dirsize
    UpperBoundFileNumberOfDir = options.dirnum
    hostname = options.hostname

def status():
    print 'file: %s' % __file__
    print 'dir: %s' % filepath
    print 'folder: %s' % downloadpath
    print 'listen on: %d' % listenport
    print 'hostname: %s' % hostname
    print 'single upload: %d' % UpperBoundSizeOfSingleUpload
    print 'dir size: %d' % UpperBoundSizeOfDir
    print 'dir num: %d' % UpperBoundFileNumberOfDir

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    load()
    status()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(listenport)
    tornado.ioloop.IOLoop.instance().start()
