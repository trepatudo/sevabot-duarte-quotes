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
import pickle
import os
import sqlite3 as lite
import sys

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

    #contains the string dump, of speech lines from the skype db
    dump_arr = []
    #TODO: change this to the path of your skype main.db
    db = 'main.db'
    #creates the lexicon
    follow={}

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
                         '!meke': self.quote_random, '!lsd': self.quote_lsd}

        """
        let's create the lexicon with the latest skype db quotes
        this would work better if we just added new quotes since:
        1 - it's faster
        2 - skype logs only save a period of time, older quotes will be lost
        3 - ayy
        upload new is commented but the function works, orchestrate seems unhappy with big
        text dumps though
        """
        readSkypeDB(db)
        #uploadNew()
        updateStructures()

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
        quote = " ".join(args[1:])
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

    def quote_lsd(self, msg, status, args):
        """
        Use self learning algo to reply ()
        """
        #TODO: Shouldn't crash if structures aren't build, just an empty response
        #not sure needs to be tested
        speech = " ".join(args[1:])
        response = lsdQuote(speech)
        msg.Chat.SendMessage("%s" % response)

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

    #region lsd methods, not organized for now

    def readSkypeDB(skype):
        lastTime = None
        previous = None
        #Read skype db
        con = None
        try:
            con = lite.connect(skype)
            #name ='duarteLines.txt'  # Name of text file coerced with +.txt
            #ump = open(name,'w')   # Trying to create a new file or open one
            cur = con.cursor()
            #chats having both Duarte and his clone are the relevant ones
            for row in cur.execute("SELECT name  FROM Chats WHERE posters LIKE '%duarte.m.godinho%' AND posters LIKE '%bot.duarte%';"):
                #select only Duarte's (the flesh version) quotes
                for row2 in cur.execute("SELECT timestamp, author, from_dispname, chatmsg_type, identities, body_xml FROM Messages WHERE chatname = '" + str(row[0]) + "' AND author like '%duarte.m.godinho%';"):
                    if row2[5] is not None:
                        if lastTime is not None and previous is not None:
                            #Duarte does not use punctuation as that is a waste of energy
                            #we have to do it for him, if we want to extract a lexicon from this mess
                            if row2[0] is not None and row2[0] - lastTime < 50:
                                dump_arr.append(((previous[5])+',').encode('utf-8').strip()+'\n')
                            else:
                                dump_arr.append(((previous[5])+'.').encode('utf-8').strip()+'\n')
                        lastTime = row2[0]
                        previous = row2
                        #else
                        #    dump.write(((row2[5])+'.').encode('utf-8').strip()+'\n')                
        except lite.Error, e:
            #TODO: No idea how errors are being handled
            print "Error %s:" % e.args[0]
            sys.exit(1)
            
        finally:
            if con:
                con.close()

    def updateStructures():
        text=[]
        for line in dump_arr:
            for word in line.split():
                text.append (word)
            text[-1] = word + '.'
        #print 'Finished reading file'
        textset=list(set(text))
        for l in range(len(textset)):
            working=[]
            check=textset[l]
            for w in range(len(text)-1):
                if check==text[w] and text[w][-1] not in '(),.?!':
                    working.append(str(text[w+1]).replace(',', '\n'))
            follow[check]=working
        #print 'Finished creating structures'

    def nextword(a):
    extra = ['jss', 'oh', 'tao', 'tao e', 'o']
    if a in follow:
        return random.choice(follow[a])
    else:
        try:
            k = extra.index(last)
            return random.choice(l[:k] + l[(k + 1):])
        except Exception:
            return random.choice(extra)
            pass

    def lsdQuote(text):
        s=random.choice(text.split())
        last = s
        response=''
        while True:
            neword=nextword(s)
            response+=' '+neword
            s=neword
            if neword[-1] in ',?!.':
                break
        return response.replace('.', '')

    def uploadNew():
        #client = Client(settings.API_KEY, 'https://dashboard.orchestrate.io/apps/7499')
        dump_s = pickle.dumps(follow,2)
        #TODO: latin1 because my machine is dumb, isn't the same for OSX
        dump_s = dump_s.decode('latin1')
        #dump_s = dump_s.decode('utf-8')
        #print 'Finished dumping to: string'
        key = 'dump'
        now_time = str(datetime.datetime.now().isoformat())
        #Save on database with key 'dump'
        response = client.put("lexicon", key, {
            "dump": dump_s,
            "time_inserted": now_time
        })

        # make sure the request succeeded
        try:
            response.raise_for_status()
            print response
            msg.Chat.SendMessage('tive ai a ler sobre umas gemas')
        except:
            print 'error ' + response
            msg.Chat.SendMessage('muito mortal')
            pass

   #endregion lsd methods, not organized for now

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
sevabot_handler = QuoteHandler()

__all__ = ['sevabot_handler']
