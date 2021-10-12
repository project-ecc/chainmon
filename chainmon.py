#!/usr/bin/env python3
# coding: UTF-8

import datetime
import settings
import argparse
import pathlib
import logging
import signal
import time
import sys

from util_email import sendEmail

from slickrpc import Proxy
from slickrpc import exc

proxy = Proxy('http://%s:%s@%s' % (settings.rpc_user, settings.rpc_pass, settings.rpc_address))

################################################################################
## ChainMonApp class ###########################################################
################################################################################

class ChainMonApp:

	def __init__(self):

		pass

	############################################################################

	def get_blocks(self):

		info = proxy.getinfo()

		return info['blocks']

	############################################################################

	def run(self):

		blocks = self.get_blocks()

		logging.info('Blockchain monitoring starting at block {}'.format(blocks))

		while True:

			time.sleep(settings.stall_sec)

			new_blocks  = self.get_blocks()

			if new_blocks == blocks:

				logging.info('Blockchain stalled at block {}'.format(blocks))

				sendEmail('henry@home-young.me.uk', 'Blockchain stalled at block {}'.format(blocks))

			blocks = new_blocks

################################################################################

def terminate(signalNumber, frame):

	sys.exit()

################################################################################
### Main program ###############################################################
################################################################################

def main():

	if sys.version_info[0] < 3:

		raise 'Use Python 3'

	pathlib.Path(settings.coin_symbol).mkdir(parents=True, exist_ok=True)

	logging.basicConfig(filename = settings.coin_symbol + '/{:%Y-%m-%d}.log'.format(datetime.datetime.now()),
						filemode = 'a',
						level    = logging.INFO,
						format   = '%(asctime)s - %(levelname)s : %(message)s',
						datefmt  = '%d/%m/%Y %H:%M:%S')

	logging.info('STARTUP')

	signal.signal(signal.SIGINT,  terminate)  # keyboard interrupt ^C
	signal.signal(signal.SIGTERM, terminate)  # kill [default -15]

	argparser = argparse.ArgumentParser(description='Blockchain stall monitor')

	command_line_args = argparser.parse_args()

	logging.info('Arguments %s', vars(command_line_args))

	app = ChainMonApp()

	app.run()

	logging.info('SHUTDOWN')

################################################################################

if __name__ == '__main__':

	main()

################################################################################
