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
logger.debug('[QuoteHandler] Loading class')


class QuoteHandler(StatefulSkypeHandler):
    """
    QuoteHandler
    Handle Duarte's quotes
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('[QuoteHandler] Constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """
        logger.debug('[QuoteHandler] Initialized')

        self.commands = {'!add': self.quote_add, '!rem': self.quote_rem, '!list': self.quote_list,
                         '!meke': self.quote_random}

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('[QuoteHandler] got: {}'.format(body))

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
        logger.debug('[QuoteHandler]  shutdown')

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

        # Parse author and check if it's not banned
        authorUsername = msg.Sender.Handle
        author = self.getUser(authorUsername)
        if self.isBanned(author):
            if not author['ban_reason']:
                msg.Chat.SendMessage(settings.MESSAGES['no_perms'] % (msg.Sender.FullName))
            else:
                msg.Chat.SendMessage(author['ban_reason'])

            return False

        # Parse quote and hash it for key
        quote = "".join(args[1:])
        m = hashlib.md5()
        m.update(quote)
        key = m.hexdigest()

        # Save on database with key hashed
        response = client.put("quotes", key, {
            "text": quote,
            "author_id": msg.Sender.Handle,
            "author_name": msg.Sender.FullName,
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
        data = 'sprunge=' + '\n'.join(quotesString) + '&submit=Submit'

        # Upload and return url
        response = urllib.urlopen(url, data.encode('utf-8'))
        page = response.read()

        # Send it
        msg.Chat.SendMessage("%s" % (page))

    # copy paste
    # @TODO: This methods are copied into both handlers, should be put into a single class (repository)
    @staticmethod
    def getUser(user):
        """
        Check if user exists
        """
        userSearch = client.get("users", user)

        # make sure the request succeeded
        try:
            userSearch.raise_for_status()
            return userSearch
        except:
            return False

    @staticmethod
    def isMod(user):
        """
        Detect if a user is moderator
         :param user: Handle to Result instance from getUser
        """
        if not user:
            return False
        if not user['moderator']:
            return False
        return True

    @staticmethod
    def isBanned(user):
        """
        Detect if a user is banned
         :param user: Handle to Result instance from getUser
        """
        if not user:
            return False
        if not user['banned']:
            return False
        return True

    # EO copy paste :)


# Export the instance to Sevabot
sevabot_handler = QuoteHandler()

__all__ = ['sevabot_handler']
