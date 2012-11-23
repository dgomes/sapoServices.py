#!/usr/bin/env python
#
# Copyright (c) 2012 Diogo Gomes <diogogomes@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
from suds.client import Client
from suds import WebFault
from suds.sax.element import Element
import logging


class sapoService(object):
    def __init__(self, wsdl, sapoAccessKey, loglevel = logging.ERROR):
        logging.basicConfig(level=loglevel)
        self.log = logging.getLogger('sapo.Service')

        self.api = Client(wsdl, autoblend=True)
        self.accessKey = sapoAccessKey

    def authenticate(self, ESBToken = None, ESBUsername = None, ESBPassword = None):
        # Create namespaces
        def_ns = ('def', 'http://services.sapo.pt/definitions')
        market_ns = ('market', 'http://services.sapo.pt/Metadata/Market')

        # Create ESBAccessKey
        accesskey = Element('ESBAccessKey', ns=market_ns).setText(self.accessKey)

        # Create ESBCredentials
        if ESBToken != None:
            token = Element('ESBToken', ns=def_ns).setText(ESBToken)
            credentials = Element('ESBCredentials', ns=def_ns).insert(token)
            self.log.debug("authenticate with ESBToken")
        elif ESBUsername != None and ESBPassword != None:
            username = Element('ESBUsername', ns=def_ns).setText(ESBUsername)
            password = Element('ESBPassword', ns=def_ns).setText(ESBPassword)
            credentials = Element('ESBCredentials', ns=def_ns).insert(password).insert(username)
            self.log.debug("authenticate with ESBUsername and ESBPassword")
        else:
            self.log.error("authenticate requires ESBCredentials")
            return False

        # Setup SOAP Headers
        self.api.set_options(soapheaders=[credentials, accesskey])
        return True

class STS(sapoService):
    # This shoul be the only SAPO service without the need for a ESBToken arg
    # obs: chicken and egg <> get token without the token
    def __init__(self, accessKey, loglevel = logging.ERROR):
        # Call Parent Constructor
        super(STS, self).__init__(wsdl = 'http://services.sapo.pt/Metadata/Contract/STS', sapoAccessKey = accessKey, loglevel =loglevel)

        # Initialize Logging
        self.log = logging.getLogger('sapo.STS')
        self.log.setLevel(loglevel)

    # This method wraps STS's API GetToken() by assuring we have either ESBToken or ESBUsername + ESBPassword
    def getESBToken(self, token = None, username = None, password = None):
        # If we have an existing token, request new token with that one
        if token != None:
            sapoService.authenticate(self, ESBToken = token)
        elif username != None and password != None:
            sapoService.authenticate(self, ESBUsername = username, ESBPassword = password)

        # Issue the SOAP Request
        try:
            tok = self.api.service.GetToken()
        except WebFault as wf:
            self.log.error(wf)
            return None
        return tok

class MeoEPG(sapoService):
    def __init__(self, accessKey, ESBToken = None, loglevel = logging.ERROR):
        # Call Parent Constructor
        super(MeoEPG, self).__init__(wsdl = 'http://services.sapo.pt/Metadata/Contract/EPG', sapoAccessKey = accessKey, loglevel =loglevel)

        # If token is provided automatically call authenticate
        sapoService.authenticate(self, ESBToken)

# TODO extend this package with further classes representing all other SAPO services
