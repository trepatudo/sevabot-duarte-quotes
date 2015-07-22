#!/sevabot

# -*- coding: utf-8 -*-

"""
QuoteHandler
Handle quotes from Duarte and store them in orchestrator
"""

from __future__ import unicode_literals


import logging
import Skype4Py
import datetime
import hashlib
import random
import urllib

from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode
from porc import Client

# Load settings
import settings

# Init logger
logger = logging.getLogger('QuoteHandler')
# Init orchestrate.io
client = Client(settings.API_KEY, settings.API_URL)

# Set to debug only during dev
logger.debug('[QuoteManager] Loading class')


class QuoteHandler(StatefulSkypeHandler):

    """
    QuoteHandler
    Handle Duarte's quotes
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('[QuoteManager] Constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """

        logger.debug('[QuoteManager] Initialized')

        self.skype = sevabot.getSkype()

        self.commands = {'!add': self.quote_add, '!remove': self.quote_remove, '!list': self.quote_list}

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('QuoteHandler handler got: {}'.format(body))

        # If the separators are not specified, runs of consecutive
        # whitespace are regarded as a single separator
        args = body.split()

        # Empty msg?
        if not len(args):
            return False

        for name, cmd in self.commands.items():
            if name == args[0]:
                cmd(msg, status, args)
                return True

        return False

    def shutdown(self):
        """
        Called when the module is reloaded.
        """
        logger.debug('QuoteHandler shutdown')

    def getAll(self):
        """
        Return all the quotes in database
        """
        pages = client.list("quotes", limit=100)
        quotes = pages.all()

        return quotes
    def quote_add(self, msg, status, args):
        """

        """
        # Parse quote and hash it for key
        quote = "".join(args[1:])
        key = hashlib.md5(quote).hexdigest()

        # Save on database with key hashed
        response = client.put("quotes", key, {
          "text": quote,
          "author_id": msg.Sender.Handle,
          "author_name": msg.Sender.FullName,
          "time_created": str(datetime.datetime.now().isoformat())
        });

        # make sure the request succeeded
        response.raise_for_status()


    def quote_remove(self, msg, status, args):
        """

        """

        # Dirty workaround to start a conference call from a chat
        call_command = self.skype.Command('CALL {}'.format(chat_name))
        self.skype.SendCommand(call_command)

    def quote_random(self, msg, status, args):
        quotes = self.getAll()
    def quote_list(self, msg, status, args):
        """
        Upload a list to sprunge.us
        """

        # Get all quotes
        quotes = self.getAll()

        # Get quotes text and break line
        quotesString = []
        for s in quotes:
            quotesString.append(s['path']['key'] + ": "+ s['value']['text'])

        # Prepare upload
        url = 'http://sprunge.us'
        data = {
            'sprunge':'\n'.join(quotesString),
            'submit':'Submit'
        }
        # Upload and return url
        response = urllib.urlopen(url, urllib.urlencode(data))
        page = response.read()
        print page


# Export the instance to Sevabot
sevabot_handler = QuoteHandler()

__all__ = ['sevabot_handler']