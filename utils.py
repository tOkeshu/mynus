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
from os.path import join, splitext


RESPONSES = { 200: 'OK'
            , 301: 'Moved Permanently'
            , 303: 'See Other'
            , 404: 'Not Found'
            , 501: 'Not Implemented'
            }
TEMPLATE_DIR = 'templates'

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


def redirect(code, path):
    body = RESPONSES[code]
    status = '%d %s' % (code, body)
    headers = [("Location", path)]
    return status, headers, body


def error(code):
    body = RESPONSES[code]
    status = '%d %s' % (code, body)
    headers = [("Content-Type", "text/plain")]
    return status, headers, body

