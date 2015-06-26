import os
import logging

if os.environ.get('ORCHESTRATE_DEBUG', None) != None:
    logging.basicConfig(level=logging.DEBUG)

API_KEY = os.environ.get('ORCHESTRATE_API_KEY', None)
API_URL = os.environ.get('ORCHESTRATE_API_URL', None)

logging.debug('API_URL: %s\tAPI_KEY: %s\n' % (API_URL, API_KEY))

