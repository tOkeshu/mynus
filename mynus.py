# Copyright (C) 2010 Romain Gauthier <romain.gauthier@masteri2l.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the standard library
from os import listdir
from os.path import join, exists, splitext
from re import compile, findall
from string import Template
from urlparse import parse_qs
from wsgiref.simple_server import make_server
from wsgiref.util import request_uri


DB_URI = 'db'
ROUTE = compile('^/pages/([^/]*)$')
TEMPLATE_DIR = 'templates'
PATTERN = compile('(.*).md$')

def get_template(name):
    template_uri = join(TEMPLATE_DIR, name)
    return open(template_uri).read()


def build_file_list(directory):
    filenames = listdir(directory)
    items = []
    for filename in filenames:
        name, extension = splitext(filename)
        item = '<li><a href="/pages/%s">%s</li>' % (name, name)
        items.append(item)
    return '<ul>\n%s</ul>' % '\n'.join(items)

class MynusWiki(object):

    page = Template(get_template('page.html'))
    pages = Template(get_template('pages.html'))
    new_page = Template(get_template('new.html'))

    def __init__(self, directory=DB_URI):
        self.directory = directory
        self.environ = None


    def __call__(self, environ, start_response):
        self.environ = environ
        request_method = self.environ['REQUEST_METHOD']
        path_info = self.environ['PATH_INFO']

        matches = findall(ROUTE, path_info)
        if path_info is '/':
            body = '301 Moved Permanently'
            status = '301 %s' % body
            headers = [("Location", "/pages/index")]
        elif not matches:
            body = 'Not Found'
            status = '404 %s' % body
            headers = [("Content-Type", "text/plain")]
        elif not hasattr(self, request_method):
            body = 'Unsupported method (%s)' % request_method
            status = '501 %s' % body
            headers = [("Content-Type", "text/plain")]
        else:
            method = getattr(self, request_method)
            status, headers, body = method(*matches)

        start_response(status, headers)
        return body


    def GET(self, name):
        if name:
            document_uri = join(DB_URI, '%s.md' % name)
            if exists(document_uri):
                data =open(document_uri).read()
                vars = { 'data': data
                       , 'title': name
                       , 'html_data': data.replace('\n', '<br/>\n')
                       }
                body = self.page.safe_substitute(**vars)
            else:
                body = self.new_page.safe_substitute(title=name)
        else:
            files = build_file_list(self.directory)
            print files
            body = self.pages.safe_substitute(title='Pages', files=files)

        status = '200 OK'
        headers = [("Content-Type", "text/html")]
        return status, headers, body


    def POST(self, name):
        document_uri = join(DB_URI, '%s.md' % name)
        length = int(self.environ['CONTENT_LENGTH'])
        input_data = self.environ['wsgi.input'].read(length)
        input_data = parse_qs(input_data)

        data = ''.join(input_data['data'])
        with open(document_uri, 'w') as document:
            document.write(data)

        body = '301 Moved Permanently'
        status = '301 %s' % body
        headers = [("Location", "/pages/%s" % name)]
        return status, headers, body


mynus_app = MynusWiki()

# Running the WSGI server:
httpd = make_server("", 8000, mynus_app)
httpd.serve_forever()

