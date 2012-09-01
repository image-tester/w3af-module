'''
test_code_disclosure.py

Copyright 2011 Andres Riancho

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

from nose.plugins.skip import SkipTest
from plugins.grep.code_disclosure import code_disclosure
from core.data.url.httpResponse import httpResponse
from core.data.request.fuzzable_request import fuzzable_request
from core.data.parsers.urlParser import url_object


class test_code_disclosure(unittest.TestCase):
    
    def setUp(self):
        self.plugin = code_disclosure()

        from core.controllers.core_helpers.fingerprint_404 import fingerprint_404_singleton
        from core.data.url.xUrllib import xUrllib
        f = fingerprint_404_singleton( [False, False, False] )
        f.set_url_opener( xUrllib() )
        kb.kb.save('code_disclosure', 'code_disclosure', [])
    
    def tearDown(self):
        self.plugin.end()
        
    def test_ASP_code_disclosure(self):
        body = 'header <% Response.Write("Hello World!") %> footer'
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, url, url)
        request = fuzzable_request(url, method='GET')
        self.plugin.grep(request, response)
        self.assertTrue( len(kb.kb.get('code_disclosure', 'code_disclosure')) == 1 )
            
    def test_PHP_code_disclosure(self):
        body = 'header <? echo $a; ?> footer'
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, url, url)
        request = fuzzable_request(url, method='GET')
        self.plugin.grep(request, response)
        self.assertTrue( len(kb.kb.get('code_disclosure', 'code_disclosure')) == 1 )


    def test_no_code_disclosure_blank(self):
        body = ''
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, url, url)
        request = fuzzable_request(url, method='GET')
        self.plugin.grep(request, response)
        self.assertTrue( len(kb.kb.get('code_disclosure', 'code_disclosure')) == 0 )

    def test_no_code_disclosure(self):
        raise SkipTest('Add this test')
    
    def test_no_code_disclosure_xml(self):
        raise SkipTest('Add this test')

