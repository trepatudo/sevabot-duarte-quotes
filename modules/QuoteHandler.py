#!/sevabot

# -*- coding: utf-8 -*-

"""
QuoteHandler
Handle quotes from Duarte and store them in orchestrator
"""

from __future__ import unicode_literals

# Import shitloads of needed stuff
import logging
import datetime
import hashlib
import urllib
import random
import requests

# Sevabot & Orchestratre
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

        self.commands = {'!add': self.quote_add, '!rem': self.quote_rem, '!list': self.quote_list, '!meke': self.quote_random }

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('[QuoteManager] got: {}'.format(body))

        # If the separators are not specified, runs of consecutive
        # whitespace are regarded as a single separator
        args = body.split()

        # Empty msg?
        if not len(args):
            return False

        # Find command
        for name, cmd in self.commands.items():
            if name == args[0]:
                cmd(msg, status, args)
                return True

        return False

    def shutdown(self):
        """
        Called when the module is reloaded.
        """
        logger.debug('[QuoteManager]  shutdown')

    def getAll(self):
        """
        Return all the quotes in database
        """
        pages = client.list("quotes", limit=100)
        quotes = pages.all()

        return quotes

    def quote_add(self, msg, status, args):
        """
        Add a quote, use md5 hashed text as key
        """

        # Parse quote and hash it for key
        quote = "".join(args[1:])
        m = hashlib.md5()
        m.update(quote)
        key = m.hexdigest()

        # Save on database with key hashed
        response = client.put("quotes", key, {
            "text": quote,
            "author_id": '- pre-python list -',
            "author_name": '- pre-python list -',
            "time_created": str(datetime.datetime.now().isoformat())
        })

        # make sure the request succeeded
        try:
            response.raise_for_status()
            msg.Chat.SendMessage(settings.MESSAGES['add_success'])
        except:
            msg.Chat.SendMessage(settings.MESSAGES['add_fail'])
            pass

    def quote_rem(self, msg, status, args):
        """
        Remove a quote based on it's hash
        """

        # Parse key
        key = "".join(args[1:])

        # @TODO: Maybe check if the quote really exists? For now I don't think its necessary.

        # Save on database with key hashed
        response = client.delete("quotes", key)

        # make sure the request succeeded
        msg.Chat.SendMessage("test")
        print response.status_code
        try:
            response.raise_for_status()
            msg.Chat.SendMessage(settings.MESSAGES['rem_success'])
        except:
            msg.Chat.SendMessage(settings.MESSAGES['rem_fail'])
            pass


    def quote_random(self, msg, status, args):
        """
        Pick a random quote and send it
        """
        quotes = self.getAll()

        # Send it
        msg.Chat.SendMessage("%s" % (random.choice(quotes)['value']['text']))

    def quote_list(self, msg, status, args):
        """
        Upload a list to sprunge.us
        """

        # Get all quotes
        quotes = self.getAll()

        # Get quotes text and break line (utf8 !)
        quotesString = []
        for s in quotes:
            string = s['path']['key'] + ": " + s['value']['text']
            quotesString.append(string)

        # Prepare upload
        url = 'http://sprunge.us'
        # Hardcoded POST string due to UTF-8 crap
        data = 'sprunge='+ '\n'.join(quotesString) + '&submit=Submit'

        # Upload and return url
        response = urllib.urlopen(url, data.encode('utf-8'))
        page = response.read()

        # Send it
        msg.Chat.SendMessage("%s" % (page))


# Export the instance to Sevabot
sevabot_handler = QuoteHandler()

__all__ = ['sevabot_handler']
