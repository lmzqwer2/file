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
    'template_path': templatepath
}
print __file__
print filepath
print downloadpath

def path_chain(path):
    folder = path.split('/')
    if folder[0]=='.':
        folder[0] = ''
    L = []
    link = ''
    for item in folder:
        link += item + '/'
        L.append(dict(name=item, url=link))
    return L

def dir_info(path):
    infoname = os.path.join(path, '.info')
    if os.path.isfile(infoname):
        with open(infoname, 'r') as f:
            return f.readlines()
    return None

def dir_upload(path):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    uploadname = os.path.join(path, '.upload')
    if os.path.isfile(uploadname):
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
        if not os.path.exists(expath)\
            or not expath.startswith(downloadpath):
            raise tornado.web.HTTPError(404)
        chainpath = path_chain(path)
        chainpath[0]['name'] = 'LM file'
        if os.path.isdir(expath):
            if not self.request.path.endswith('/'):
                self.redirect(self.request.path+'/')
                return
            names = self.list_directory(expath)
            self.render("dir.html", names=names, path=chainpath, info=dir_info(expath))
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

class StaticFH(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        if dir_upload(absolute_path):
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

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    define("port", default=8000, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
