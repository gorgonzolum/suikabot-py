import time
import humanize

from modules import util
from collections import defaultdict

class Laters (defaultdict):
    def add (self, target, user, msg):
        self.get(target).append((user, msg, time.time()))
   
    def has (self, target):
        return target.lower() in self
     
    def get (self, target):
        return self[target.lower()]

    def remove (self, target):
        del self[target.lower()]

    def limitcheck (self, target, user):
        return len([l for l in self.get(target) if l[0].lower() == user.lower()]) < 3

    def load (self):
        self.clear()
        self.update(data_writer.get('laters.db'))

    def commit (self):
        data_writer.add('laters.db', dict(self))
        
laters = Laters(list)

def client_connected (client):
    laters.load()

def irc_public (client, hostmask, channel, message):
    nick, user, host = util.ircmask_split(hostmask)

    # check for saved laters first
    if laters.has(nick):
        lats = laters.get(nick)
        for l in lats:
            sender, msg, t = l
       
            t = time.time() - t

            client.say(channel, "{0}: Sent {1}: <{2}> {3}".format(
                nick, humanize.naturaltime(t), sender, msg
            ))

        laters.remove(nick)
        laters.commit()
    
    # process commands
    if message.startswith('!later'):
        _, cmd, target, msg = message.split(' ', 3)
        
        if cmd in ['tell', 'remind']:
            t = target.lower()
            if t in ['xpc', 'xpcybic', 'xpcynic', 'xpcyphone', 'xpcdroid']:
                client.say(channel, "Shhh!!! You know xpc doesn't like that!")
            else:
                if laters.limitcheck(target, nick):
                    laters.add(target, nick, msg)
                    client.say(channel, "Okay, I'll remind {0} later!".format(target))
                    laters.commit()
                else:
                    client.say(channel, "You already left {0} too many reminders!".format(target))
