import BaseHTTPServer
import os
import posixpath
import urllib
import re
import shutil
import mimetypes
import cgi
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class GPGUploadHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    INDEX = "index.html"
    LIST_HEAD = "list-head.htmlpart"
    LIST_FOOT = "list-foot.htmlpart"
    UPLOAD_DIRECTORY = "file-upload"

    # if servers handles a GET request, it executes this method
    def do_GET(self):
        """Serve a GET request."""
        print("GET " + self.path)
        root = self.path.split('/')[1]
        # if requesting anything outside the uploading file directory, serve as html
        print(root)
        if(root != self.UPLOAD_DIRECTORY):
            self.serve_html()
        else:
            # listing requested upload directory
            if(os.path.isdir(self.translate_path(self.path))):
                self.serve_upload_directory()
            else:
                # try to download file
                self.serve_stored_file()


    # if servers handles a POST request, it executes this method
    def do_POST(self):
        """Serve a POST request."""
        print("POST " + self.path)
        # if upload directory
        if(os.path.isdir(self.UPLOAD_DIRECTORY + "/" + self.path)):
            self.path = self.UPLOAD_DIRECTORY + "/" + self.path
            self.upload_file()
        else:
            print("wrong upload destination")
            self.path = "/"
            self.serve_html()



    # serve html files, like any http server
    def serve_html(self):
        print("Serving html")
        if(self.path == '/'):
            self.path = self.INDEX
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(self.translate_path(self.path), 'rb')
        except IOError:
            # self.send_error(404, "File not found" + self.path)
            self.serve_404()
            return None
        self.send_response(200)
        self.send_header("Content-type", self.guess_type(self.translate_path(self.path)))
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        f.close()

    # list selected upload directory content
    def serve_upload_directory(self):
        print("upload dir")
        path = self.translate_path(self.path)
        dirlist = os.listdir(self.translate_path(self.path))
        dirlist.sort(key=lambda a: a.lower())
        try:
            hd = open(self.LIST_HEAD, 'rb')
        except IOError:
            self.send_error(404, "File not found" + self.path)
            return None
        head = hd.read()
        hd.close()
        try:
            ft = open(self.LIST_FOOT, 'rb')
        except IOError:
            self.send_error(404, "File not found" + self.path)
            return None
        foot = ft.read()
        ft.close()
        f = StringIO()
        f.write(head)
        displaypath = cgi.escape(urllib.unquote(self.path))
        # link to parent directory
        f.write('<li class="parent-dir"><a href="%s"><i class="fa fa-folder-open"></i>Parent directory: %s</a></li>\n' % (urllib.quote(os.path.dirname(os.path.dirname(self.path))), cgi.escape(os.path.dirname(os.path.dirname(self.path)))))
        for name in dirlist:
            print(path)
            fullname = os.path.join(path, name)
            displayname = name
            if(self.path[-1] != "/"):
                self.path = self.path + "/"
            linkname = self.path + name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                css_class="dir"
                icon="folder"
                displayname = displayname + "/"
                linkname = linkname + "/"
            else:
                css_class="file"
                icon="file"
            if os.path.islink(fullname):
                displayname = displayname + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li class="%s"><a href="%s"><i class="fa fa-%s"></i>%s</a></li>\n' % (css_class, urllib.quote(linkname), icon, cgi.escape(displayname)))
        f.write(foot)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()

        shutil.copyfileobj(f, self.wfile)
        f.close()

    # download stored file to client
    def serve_stored_file(self):
        #TODO download file or 404
        print("Serving file")
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(self.translate_path(self.path), 'rb')
        except IOError:
            # self.send_error(404, "File not found" + self.path)
            self.serve_404()
            return None
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Cache-Control", "no-cache")
        #self.send_header("Content-Disposition", "attachment")
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        f.close()

    # serve 404.html instead of ugly 404 response
    def serve_404(self):
        print("Serving 404")

        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            print(self.translate_path("404.html"))
            print(self.path)
            f = open(self.translate_path("404.html"), 'rb')
        except IOError:
            self.send_error(404, "File not found" + self.path)
            return None
        self.send_response(404)
        self.send_header("Content-type", 'text/html')
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        shutil.copyfileobj(f, self.wfile)
        f.close()

    # upload file to server
    def upload_file(self):
        print("uploading file")
        boundary = self.headers.plisttext.split("=")[1]
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        print(fn)
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")


    ################
    # tool methods #
    ################
    # tool method to translate path
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    # tool method to guess mime type depending of file
    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """
        if not mimetypes.inited:
            mimetypes.init() # try to read system mime.types
        extensions_map = mimetypes.types_map.copy()
        base, ext = posixpath.splitext(path)
        if ext in extensions_map:
            return extensions_map[ext]
        else:
            return 'text/plain'


#############
# class end #
#############

##################
# running server #
##################
def run(server_class=BaseHTTPServer.HTTPServer, handler_class=GPGUploadHandler):
    print(handler_class)
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    add = server_address[0] if len(server_address[0])>0 else "localhost"
    print("Serving http on " + add + " on port " + str(server_address[1]))
    httpd.serve_forever()

run()
