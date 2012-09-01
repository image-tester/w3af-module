'''
test_strange_headers.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest

import core.data.kb.knowledgeBase as kb

from core.data.url.httpResponse import httpResponse
from core.data.request.fuzzable_request import fuzzable_request
from core.data.parsers.urlParser import url_object
from core.controllers.misc.temp_dir import create_temp_dir
from core.controllers.core_helpers.fingerprint_404 import fingerprint_404_singleton
from plugins.grep.strange_headers import strange_headers


class test_strange_headers(unittest.TestCase):
    
    def setUp(self):
        create_temp_dir()
        self.plugin = strange_headers()
        fingerprint_404_singleton( [False, False, False] )

    def tearDown(self):
        self.plugin.end()
    
    def test_strange_headers_positive(self):
        body = 'Hello world'
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html', 'hello-world': 'yes!'}
        request = fuzzable_request(url, method='GET')
        
        resp_positive = httpResponse(200, body , headers, url, url)
        self.plugin.grep(request, resp_positive)
        
        infos = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEquals( len(infos), 1)
        
        info = infos[0]
        self.assertEqual( info.getName(), 'Strange header')
        self.assertEqual( info.getURL(), url)
    
    def test_strange_headers_negative(self):
        body = 'Hello world'
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html', 'x-pad': 'yes!'}
        request = fuzzable_request(url, method='GET')
        
        resp_positive = httpResponse(200, body , headers, url, url)
        self.plugin.grep(request, resp_positive)
        
        infos = kb.kb.get('strange_headers', 'strange_headers')
        self.assertEquals( len(infos), 0)
