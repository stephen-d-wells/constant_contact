#!/usr/bin/env python

from constant_contact.config.find_dir import FindDir
import configparser, fcntl, requests, sys

# if you changed your app id in the configuration file, update here too
APP_ID = 'my_ctct_app'

# change this to point your ini file (absolute path required)
#CONF_FILE="/home/me/.access/constant_contact.ini"
# otherwise we'll find it by looking under `conf/` in this package.
CONF_FILE="constant_contact.ini"

CODE_REQUEST=( "https://api.cc.email/v3/idfed?response_type=code&client_id={}"
               "&scope=contact_data&redirect_uri=https%3A%2F%2Flocalhost" )

TOKEN_REQUEST=( "https://idfed.constantcontact.com/as/token.oauth2?code={}"
                "&redirect_uri=https%3A%2F%2Flocalhost&"
                "grant_type=authorization_code" )


base_dirs = FindDir()
conf_filename = base_dirs.conf_dir + CONF_FILE

parser = configparser.ConfigParser()
parser.read(conf_filename)

conf = dict(parser['my_ctct_app'])


print("""
This script will generate new access / refresh tokens.

Assumptions:

1. You have already filled in {} with

  * api_key: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
  * app_secret: XXXXXXXXXXXXXXXXXXXXXX
""".format(conf_filename))

res = input("Have you filled these in? [Y/n] ")

if res.lower().startswith("n"):
    print("""
  You can obtain these from:

  https://app.constantcontact.com/pages/dma/portal/

  It's not abvious at the onset but the app_secret is generated
  after you select the app you're going to use. Find the button
  labeled "Generate Secret". A warning will pop up that you may
  be overwriting your current secret. After passing that you
  will get one shot to copy and paste it here or generate a new
  one and try again.

  When you are done, re-run this script.
    """)
    sys.exit()

print("""

2. You have access to a browser you can cut-n-paste into?

  I will be generating a URL from the entries provided in your
  conf/constant_contact.ini file. You will place this URL in a
  browser and it will redirect you to a local url. That URL will
  fail because you are not running a browser locally.

  What we need from that URL is the code it provides. It will
  look like:

  https://localhost/?code=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

  You will need to cut~n~paste that code into here.

""")

res = input("Do you have access to a browser you can cut~n~paste into? [Y/n] ")

if res.lower().startswith("n"):
    print("You may need to run this at another time. The URL is too fraught\n"
          "with potential typos and it requires authentication through a\n"
          "browser to continue.\n")
    sys.exit()

url = CODE_REQUEST.format(conf['api_key'])

print("cut~n~paste the following url into your browser to retrieve the code.")
print("URL:\n  ", url + "\n")
print("just enter everything after the code= portion of the url")
print("https://localhost/?code=<code> -- Your code expires in 1 minute.")

code = input("Enter the code here: ")

req = requests.post(
  TOKEN_REQUEST.format(code), auth=(conf['api_key'], conf['app_secret'])
)

results = req.json()

import pprint
pprint.pprint(results)

print("\n  access_token: ", results['access_token'])
print("  refresh_token: ", results['refresh_token'])
print("\nThese need to be updated in your configuration "
      "file: {}".format(conf_filename))

res = input("I can attempt to do that now if you'd like or you can\n"
            "stop and do it manually. Would you like me to update your\n"
            "configuration file? [Y/n]")

if res.lower().startswith("n"):
    print("\nYou can take it from here. Good Luck.\n")
    sys.exit()

parser[APP_ID]['access_token'] = results['access_token']
parser[APP_ID]['refresh_token'] = results['refresh_token']
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
        parser.write(configfile)
        fcntl.flock(configfile, fcntl.LOCK_UN)
    else:
        raise OSError("Unable to establish lock on config file")

print("\nSuccess. Try running\n  bin/fetch_contacts.py\nto test your "
      "new configuration.")