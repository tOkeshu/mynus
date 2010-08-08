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
from os import makedirs
from os.path import join, exists
from re import compile, search
from string import Template
from sys import argv
from urlparse import parse_qs
from wsgiref.simple_server import make_server
from wsgiref.util import request_uri

# Import from utils
from utils import get_template, build_file_list, redirect, error


DB_URI = 'db'
ROUTE = compile('^/pages/?([^/]*)$')
PATTERN = compile('(.*).md$')

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

        matches = search(ROUTE, path_info)
        if path_info is '/':
            status, headers, body = redirect(301, '/pages/index')
        elif path_info.endswith('/'):
            status, headers, body = redirect(301, path_info[:-1])
        elif not matches:
            status, headers, body = error(404)
        elif not hasattr(self, request_method):
            status, headers, body = error(501)
        else:
            method = getattr(self, request_method)
            status, headers, body = method(*matches.groups())

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
            body = self.pages.safe_substitute(title='Pages', files=files)

        return '200 OK', [("Content-Type", "text/html")], body


    def POST(self, name):
        document_uri = join(DB_URI, '%s.md' % name)
        length = int(self.environ['CONTENT_LENGTH'])
        input_data = self.environ['wsgi.input'].read(length)
        input_data = parse_qs(input_data)

        data = ''.join(input_data['data'])
        with open(document_uri, 'w') as document:
            document.write(data)

        status, headers, body = redirect(303, '/pages/%s' % name)
        return status, headers, body


def main():
    host = argv[1] if len(argv) >= 2 else 'localhost'
    port = int(argv[2]) if len(argv) >= 3 else 8000
    mynus_app = MynusWiki()

    if not exists(DB_URI):
        makedirs(DB_URI)

    # Running the WSGI server:
    httpd = make_server(host, port, mynus_app)
    print('Serving HTTP on http://%s:%d/ ...' % (host, port))
    httpd.serve_forever()


if __name__ == '__main__':
    main()

