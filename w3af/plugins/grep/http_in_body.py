''''
http_in_body.py

Copyright 2008 Andres Riancho

This file is part of w3af, http://w3af.org/ .

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
import core.controllers.output_manager as om
import core.data.kb.knowledge_base as kb

from core.controllers.plugins.grep_plugin import GrepPlugin
from core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from core.data.esmre.multi_re import multi_re
from core.data.kb.info import Info


class http_in_body (GrepPlugin):
    """
    Search for HTTP request/response string in response body.
    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    HTTP = (
        # GET / HTTP/1.0
        ('[a-zA-Z]{3,6} .*? HTTP/1.[01]', 'REQUEST'),
        # HTTP/1.1 200 OK
        ('HTTP/1.[01] [0-9][0-9][0-9] [a-zA-Z]*', 'RESPONSE')
    )
    _multi_re = multi_re(HTTP)

    def __init__(self):
        GrepPlugin.__init__(self)

        self._already_inspected = ScalableBloomFilter()

    def grep(self, request, response):
        '''
        Plugin entry point.

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None, all results are saved in the kb.
        '''
        uri = response.get_uri()
        
        # 501 Code is "Not Implemented" which in some cases responds with
        # this in the body:
        # <body><h2>HTTP/1.1 501 Not Implemented</h2></body>
        # Which creates a false positive.
        
        if response.get_code() != 501\
        and response.is_text_or_html()\
        and uri not in self._already_inspected:
            
            # Don't repeat URLs
            self._already_inspected.add(uri)

            body_without_tags = response.get_clear_text_body()
            if body_without_tags is None:
                return

            for match, _, _, reqres in self._multi_re.query(body_without_tags):

                if reqres == 'REQUEST':
                    desc = 'An HTTP request was found in the HTTP body of'\
                           ' a response.'
                    i = Info('HTTP Request in HTTP body', desc, response.id,
                             self.get_name())
                    i.set_uri(uri)
                    i.add_to_highlight(match.group(0))
                    kb.kb.append(self, 'request', i)

                if reqres == 'RESPONSE':
                    desc = 'An HTTP response was found in the HTTP body of'\
                           ' a response.'
                    i = Info('HTTP Response in HTTP body', desc, response.id,
                             self.get_name())
                    i.set_uri(uri)
                    i.add_to_highlight(match.group(0))
                    kb.kb.append(self, 'response', i)

    def end(self):
        '''
        This method is called when the plugin wont be used anymore.
        '''
        for info_type in ['request', 'response']:

            if kb.kb.get('http_in_body', info_type):
                msg = 'The following URLs have an HTTP ' + \
                    info_type + ' in the HTTP response body:'
                om.out.information(msg)
                for i in kb.kb.get('http_in_body', info_type):
                    om.out.information(
                        '- ' + i.get_uri() + '  (id:' + str(i.get_id()) + ')')

    def get_long_desc(self):
        '''
        :return: A DETAILED description of the plugin functions and features.
        '''
        return '''\
        This plugin searches for HTTP responses that contain other HTTP
        request/responses in their response body. This situation is mostly seen
        when programmers enable some kind of debugging for the web application,
        and print the original request in the response HTML as a comment.
        '''
