#!/usr/bin/env python

from constant_contact.api.v3 import ConstantContact

import datetime

APP_ID = 'my_ctct_app'

cc = ConstantContact(APP_ID)
contacts = cc.get_contacts()

import pprint
pprint.pprint(contacts)
