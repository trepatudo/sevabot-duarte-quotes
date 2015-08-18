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
logger.debug('[DuarteTe] Loading class')


class DuarteTe(StatefulSkypeHandler):
    """
    Duarte
    Handle Duarte's bans
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('[DuarteTe] Constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """
        logger.debug('[DuarteTe] Initialized')

        self.channels = []

        self.sevabot = sevabot

        # start the trigger on keyword
        self.commands = {'!te': self.duarte_te}

        # var for last setence
        self.lastMsg = u''

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('[DuarteTe] got: {}'.format(body))

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

        # No command, save message from Duarte
        if (msg.Sender.Handle == "duarte.m.godinho"):
            msg.lastMsg = body


        return False

    def shutdown(self):
        """
        Called when the module is reloaded.
        """
        logger.debug('[DuarteTe]  shutdown')

    def getAllQuotes(self):
        """
        Return all the quotes in database
        """
        pages = client.list("quotes", limit=100)
        users = pages.all()

        return users

    def duarte_te(self, msg, status, args):
        """
        Add -te to every word and send it
        """

        msgArray = self.lastMsg.split()
        if not len (msgArray):
            return False

        msgTe = msgArray.split()

        msg.Chat.SendMessage('-te '.join(msgTe) + '-te')



# Export the instance to Sevabot
sevabot_handler = DuarteTe()

__all__ = ['sevabot_handler']
