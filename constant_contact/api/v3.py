#!/usr/bin/env python

from constant_contact.config.find_dir import FindDir
from configparser import ConfigParser

import fcntl, requests, sys, time

class ConstantContact(object):

    base_url  = 'https://api.cc.email/v3/'

    # replace {} with refresh_token
    token_url = ( "https://idfed.constantcontact.com/as/token.oauth2"
                  "?refresh_token={}&grant_type=refresh_token" )
    conf_file = 'constant_contact.ini'

    app_id = None
    conf = None # becomes a ConfigParser object

    def __init__( self, app_id=None, conf_file=None ):

        if app_id is None:
            raise AttributeError(
              "app_id must match section heading in conf file"
            )

        self.app_id = app_id

        if conf_file is not None:
            self.conf_file = conf_file

        self._populate_config()

    def _populate_config(self, write=False):

        base_dirs = FindDir()
        cp = ConfigParser()

        conf_filename = base_dirs.conf_dir + self.conf_file

        if write:
            with open(conf_filename, 'w') as configfile:
                locked = False

                for x in range(30):
                    try:
                        fcntl.flock(configfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        locked = True
                        break
                    except OSError as e:
                        if sys.stdout.isatty(): # interactive
                            print("File Lock: {} - retrying...".format(e))

                    time.sleep(1)

                if locked:
                    self.conf.write(configfile)
                    fcntl.flock(configfile, fcntl.LOCK_UN)
                else:
                    raise OSError("Unable to establish lock on config file")
        else:
            cp.read(conf_filename)
            self.conf = cp

    def refresh_token(self):

        token_url = self.token_url.format(
          self.conf[self.app_id]['refresh_token']
        )
        res = requests.post(token_url,
          auth=(
            self.conf[self.app_id]['api_key'],
            self.conf[self.app_id]['app_secret']
          )
        )

        if res.status_code == 200:
            tokens = res.json()
            self.conf[self.app_id]["access_token"] = tokens['access_token']
            self.conf[self.app_id]["refresh_token"] = tokens['refresh_token']
            self._populate_config(True)
        else:
            if sys.stdout.isatty(): # interactive
                print("error trying to refresh token...")
            res.raise_for_status()

    def request(self, url=None, params=None, method="get", retry=True):

        if url is None:
            raise AttributeError("URL is empty when calling request()")

        headers = {
          'Accept': "application/json",
          'Content-Type': "application/json",
          'Authorization': "Bearer " + self.conf[self.app_id]['access_token']
        }

        if method == "post":
            res = requests.post(self.base_url + url, data=params, headers=headers)
        else:
            res = requests.request(method, self.base_url + url, params=params, headers=headers)

        if res.status_code == 401:
            if sys.stdout.isatty():
                print("401 response = refreshing token")
            self.refresh_token()
            if retry: # we'll retry once
                self.request(url, params, method, False)

        return res.json()

    def get_contacts(self):

        return self.request(
          '/contacts',
          { "status": "all", "include_count": "true" }
        )



if __name__ ==  "__main__":

    app_id = 'my_ctct_app'

    cc = ConstantContact(app_id)
    import pprint
    pprint.pprint(cc.get_contacts())

