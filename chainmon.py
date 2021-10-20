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

from discord_webhook import DiscordWebhook

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

	def get_block_info(self):

		blockchaininfo = proxy.getblockchaininfo()

		bestblockhash  = blockchaininfo['bestblockhash']

		bestblockinfo  = proxy.getblock(bestblockhash)

		return (blockchaininfo['blocks'], bestblockinfo['time'])

	############################################################################

	def run(self):

		stalls = 0

		(block, block_time) = self.get_block_info()

		logging.info('Blockchain monitoring starting at block {}'.format(block))

		while True:

			time.sleep(settings.stall_sec)

			(new_block, block_time) = self.get_block_info()

			if new_block == block:

				stalls += 1

				if bin(stalls).count('1') == 1:

					message = 'Blockchain stalled at block {} for {} minutes'.format(block, (int(time.time()) - block_time) // 60)

					logging.info(message)

					if settings.email_enable:

						sendEmail(settings.to_email, message)

					if settings.twitter_enable:

						pass

					if settings.discord_enable:

						webhook = DiscordWebhook(url=settings.discord_webhook, content=message)

						response = webhook.execute()

			else:

				stalls = 0

			block = new_block

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
