#!/usr/bin/env python
import yaml
import logging
from suds import WebFault

from sapoServices import STS, MeoEPG

if __name__ == '__main__':
    conf = yaml.load(file('settings.yaml', 'r'))

    # Retrieve ESBToken from STS service
    sts = STS(conf['sapo']['STS']['ESBAccessKey'])
    token = sts.getESBToken(username = conf['sapo']['username'], password = conf['sapo']['password'])
    print token

    # GetChannelList
    meoEPG = MeoEPG(conf['sapo']['MeoEPG']['ESBAccessKey'], token)
    try:
        print meoEPG.api.service.GetChannelList()

        #Before the token expires, you must get a new one! logic on expiration is app specific
        sts.authenticate(ESBToken = token)
        print sts.api.service.GetPrimaryId()
    except WebFault as wf:
        print wf

