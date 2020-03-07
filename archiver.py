#! /usr/bin/python3

"""
Functioning as intended. Don't modify. (Future self note.)
... immediately followed by me modifying it... super
"""

import os
import sys
import praw
import time
import random
from datetime import datetime
# Rename your archiverconfig.py to arconfig.py so we can import yours.
try:
    import arconfig as arcon
# That way, the config can be freely edited by the developer, and won't wipe the user's current settings.
except:
    import archiverconfig as arcon


class ModBot:

    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])

    def archive(self):

        users = arcon.INCLUDE
        msgs = {value:key for key, value in users.items()}
        for k,v in users.items():
            if v is None:
                users.update({k:random.choice(arcon.RANMSG)})
            
        conversations = self.subreddit.modmail.conversations()
        for conv in conversations:
            usernames = []
            for author in conv.authors:
                if author not in usernames:
                    usernames.append(author)
            for user in users:
                if user in usernames and conv.unread:
                    conv = self.subreddit.modmail(conv.id)

                    r = False
                    m = False
                    a = False

                    # Had issues with these if modmail conversation isn't brand new and untouched.
                    # So, try each action, and just carry on if something happens. Not very elegant, but hey

                    try:
                        conv.reply(users[user])
                        r = True
                    except:
                        pass

                    try:
                        conv.mute()
                        m = True
                    except:
                        pass

                    try:
                        conv.archive()
                        a = True
                    except:
                        pass

                    # Had issues with replying, muting and archiving a modmail conversation that has been opened/something/idk
                    # Therefore, rather than print 3 messages per action like before, just deliver a report based on what went through
                    report = f"Found: {user.lower()} | Replied to? {r} | Muted? {m} | Archived? {a}"
                    print(report)

                    with open(arcon.LOG, "a") as f:
                        time_now = time.time()
                        f.write(f"{datetime.fromtimestamp(time_now)} / ({time_now}): {report}\n")
                    break

if __name__ == '__main__':
    ModBot(arcon.AR).archive()
