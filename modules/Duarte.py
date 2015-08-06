#!/sevabot

# -*- coding: utf-8 -*-

"""
Duarte
Say somethign random every 5 minutes
"""

from __future__ import unicode_literals

# Import shitloads of needed stuff
import logging
import random
from threading import Timer
from datetime import datetime

# Sevabot & Orchestratre
from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode, get_chat_id
from porc import Client

# Load settings
import settings

# Init logger
logger = logging.getLogger('Duarte')
# Init orchestrate.io
client = Client(settings.API_KEY, settings.API_URL)

# Set to debug only during dev
logger.debug('[Duarte] Loading class')


class Duarte(StatefulSkypeHandler):
    """
    Duarte
    Handle Duarte's bans
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('[Duarte] Constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """
        logger.debug('[Duarte] Initialized')

        self.channels = []

        self.sevabot = sevabot

        # start the trigger on keyword
        self.commands = {settings.DUARTE_KEYWORD: self.duarte_add}

        # Init Duarte without speaking at first
        self.duarte_speak(False)

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('[Duarte] got: {}'.format(body))

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
        logger.debug('[Duarte]  shutdown')

    def getAllQuotes(self):
        """
        Return all the quotes in database
        """
        pages = client.list("quotes", limit=100)
        users = pages.all()

        return users

    def duarte_add(self, msg, status, args):
        chan = get_chat_id(msg.Chat)

        # Add if not there
        if not chan in self.channels:
            self.channels.append(chan)

        logger.info('[Duarte] Added new channel: '+ chan)

        return False

    def duarte_speak(self, speak = True):
        """
        Pick a random quote and send it
        """
        now_time = datetime.now().time()
        sleepy_time = settings.DUARTE_TIMER
        # If speak = fal
        if speak == True:
            if time(11,55) <= now_time <= time(14,05):
                # 15 minute timer
                sleepy_time*=3
            elif (time(9,35) > now_time) or (now_time > time(18,05):
                # 60 minute timer
                sleepy_time*=12
            else:
                quotes = self.getAllQuotes()

                # New quote
                logger.info('Getting new quote')

                # Get channels
                for c in self.channels:
                    # Quote
                    logger.info('Sending new quote to: %s' % (c))
                    # Send it
                    self.sevabot.sendMessage(c, "%s" % (random.choice(quotes)['value']['text']))

        # 5 minute timer
        self.notifier = Timer(sleepy_time, self.duarte_speak)
        self.notifier.daemon = True  # Make sure CTRL+C works and does not leave timer blocking it
        self.notifier.start()



# Export the instance to Sevabot
sevabot_handler = Duarte()

__all__ = ['sevabot_handler']
