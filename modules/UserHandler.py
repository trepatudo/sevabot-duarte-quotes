#!/sevabot

# -*- coding: utf-8 -*-

"""
UserHandler
Manage people allowed to add/remove quotes
"""

from __future__ import unicode_literals

# Import shitloads of needed stuff
import logging
import datetime

# Sevabot & Orchestratre
from sevabot.bot.stateful import StatefulSkypeHandler
from sevabot.utils import ensure_unicode
from porc import Client, Patch

# Load settings
import settings

# Init logger
logger = logging.getLogger('UserHandler')
# Init orchestrate.io
client = Client(settings.API_KEY, settings.API_URL)

# Set to debug only during dev
logger.debug('[UserHandler] Loading class')


class UserHandler(StatefulSkypeHandler):
    """
    UserHandler
    Handle Duarte's bans
    """

    def __init__(self):
        """
        Use `init` method to initialize a handler.
        """

        logger.debug('[UserHandler] Constructed')

    def init(self, sevabot):
        """
        Set-up our state. This is called every time module is (re)loaded.
        :param skype: Handle to Skype4Py instance
        """
        logger.debug('[UserHandler] Initialized')

        self.commands = {'!ban': self.ban_add, '!unban': self.ban_rem, '!bans': self.ban_list}

    def handle_message(self, msg, status):
        """
        Override this method to customize a handler.
        """

        # Parse body into utf8
        body = ensure_unicode(msg.Body)

        # Debug
        logger.debug('[UserHandler] got: {}'.format(body))

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
        logger.debug('[UserHandler]  shutdown')

    def getAll(self):
        """
        Return all the users in database
        """
        pages = client.list("users", limit=100)
        users = pages.all()

        return users

    def ban_add(self, msg, status, args):
        """
        Add a user to ban list
        """

        # Parse author and check if it's moderator
        authorUsername = msg.Sender.Handle
        author = self.getUser(authorUsername)
        if not self.isMod(author):
            msg.Chat.SendMessage(settings.MESSAGES['no_perms'] % (msg.Sender.FullName))
            return False


        # Parse username
        user = args[1]

        # Is there a quote?
        reason = ""
        if (len(args) > 1):
            reason = " ".join(args[2:])

        # Save on database with key hashed
        response = client.put("users", user, {
            "banned": True,
            "ban_reason": reason,
            "ban_author_id": msg.Sender.Handle,
            "ban_author_name": msg.Sender.FullName,
            "ban_time": str(datetime.datetime.now().isoformat())
        })

        # make sure the request succeeded
        try:
            response.raise_for_status()
            msg.Chat.SendMessage(settings.MESSAGES['ban_success'] % (user))
        except:
            msg.Chat.SendMessage(settings.MESSAGES['ban_fail'])
            pass

    def ban_rem(self, msg, status, args):
        """
        Remove a username from banlist
        """

        # Parse author and check if it's moderator
        authorUsername = msg.Sender.Handle
        author = self.getUser(authorUsername)
        if not self.isMod(author):
            msg.Chat.SendMessage(settings.MESSAGES['no_perms'] % (msg.Sender.FullName))
            return False

        # Parse key
        user = args[1]

        # @TODO: Maybe check if the user really exists? For now I don't think its necessary.

        # Save on database as a patch to "banned" value
        patch = Patch()
        patch.add("banned", False)
        response = client.patch('users', user, patch)

        # make sure the request succeeded
        try:
            response.raise_for_status()
            msg.Chat.SendMessage(settings.MESSAGES['unban_success'] % (user))
        except:
            msg.Chat.SendMessage(settings.MESSAGES['unban_fail'])
            pass

    def ban_list(self, msg, status, args):
        """
        Show the list of banned users
        """

        # Get all quotes
        users = self.getAll()

        # Get quotes text and break line (utf8 !)
        usersString = []
        for s in users:
            if 'banned' in s['value']:
                if s['value']['banned'] == True:
                    string = s['path']['key'] + " - " + s['value']['ban_reason'] + " > banned by: " + s['value']['ban_author_name'] + "(" + s['value']['ban_author_id'] + ")"
                    usersString.append(string)

        # Send it
        msg.Chat.SendMessage("%s" % ('\n'.join(usersString)))

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
        if user == False:
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
        if user == False:
            return False
        if not user['banned']:
            return False
        return True
        # EO copy paste :)


# Export the instance to Sevabot
sevabot_handler = UserHandler()

__all__ = ['sevabot_handler']
