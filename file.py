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
StaticFH = tornado.web.StaticFileHandler
RedirectH = tornado.web.RedirectHandler
settings = {
#    "static_path": os.path.join( os.path.dirname(__file__),"static"),
    'template_path': templatepath
}
print __file__
print filepath
print downloadpath

class DLHandler(tornado.web.RequestHandler):
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
        names = []
        for name in os.listdir(path):
            if name.startswith('.'):
                continue
            fullname = os.path.join(path,name)
            displayname = linkname = name
            filetype = 'file'
            if os.path.isdir(fullname):
                displayname = name + '/'
                linkname = name + '/'
                filetype = 'dir'
            if os.path.islink(fullname):
                displayname = name + '@'
                filetype = 'link'
            names.append((linkname,displayname,filetype))
        return names

    def dir_info(self, path):
        infoname = os.path.join(path, '.info')
        if os.path.isfile(infoname):
            with open(infoname, 'r') as f:
                return f.readlines()
        return None

    def path_chain(self, path):
        folder = path.split('/')
        folder[0] = ''
        L = []
        link = ''
        for item in folder:
            link += item + '/'
            L.append(dict(name=item, url=link))
        L[0]['name'] = 'LM file'
        L[-1]['url'] = None
        return L

    def get(self,path=''):
        path = './' + path
        path = path.strip('/')
        print path
        expath = os.path.join(self.absolute_path, path)
        if not os.path.exists(expath)\
            or not expath.startswith(downloadpath):
            raise tornado.web.HTTPError(404)
        if os.path.isdir(expath):
            if not self.request.path.endswith('/'):
                self.redirect(self.request.path+'/')
                return
            names = self.list_directory(expath)
            self.render("dir.html", names=names, path=self.path_chain(path), info=self.dir_info(expath))
            return
        else:
            with open(expath, 'r') as f:
                text = f.read();
            t = filetype.filetype(expath)
            self.render("code.html", text=text, path=self.path_chain(path), ext=t, info=None)
            return
        super(DLHandler, self).get(path, include_body)

app = tornado.web.Application(
    handlers=[
        (r'/', DLHandler, dict(path=downloadpath)),
        (r'/css/(.*)', StaticFH, dict(path=csspath)),
        (r'/js/(.*)', StaticFH, dict(path=jspath)),
        #(r'/(.*)/', DLHandler, dict(path=downloadpath)),
        (r'/(.*)', DLHandler, dict(path=downloadpath)),
        (r'/static/(.*)', StaticFH, dict(path=downloadpath)),
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
