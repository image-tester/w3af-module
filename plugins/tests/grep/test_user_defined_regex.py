'''
test_user_defined_regex.py

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
from plugins.grep.user_defined_regex import user_defined_regex


class test_user_defined_regex(unittest.TestCase):
    
    def setUp(self):
        self.plugin = user_defined_regex()
        
    def test_user_defined_regex(self):
        body = '<html><head><script>xhr = new XMLHttpRequest(); xhr.open(GET, "data.txt",  true);'
        url = url_object('http://www.w3af.com/')
        headers = {'content-type': 'text/html'}
        response = httpResponse(200, body , headers, url, url)
        request = fuzzable_request(url, method='GET')
        
        options = self.plugin.get_options()
        options['single_regex'].setValue('".*?"')
        self.plugin.set_options( options )
        
        self.plugin.grep(request, response)
        self.assertEquals( len(kb.kb.get('user_defined_regex', 'user_defined_regex')) , 1 )
        
        info_obj = kb.kb.get('user_defined_regex', 'user_defined_regex')[0]
        self.assertTrue( info_obj.getDesc().startswith('The response matches the user defined regular expression') )
        
    def tearDown(self):
        self.plugin.end()        