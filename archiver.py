#! /usr/bin/python3

import os
import sys
import praw
import time
import random
from datetime import datetime
try:
    import arconfig as arcon
except:
    import archiverconfig as arcon


class ModBot:

    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])

    def archive(self):

        users = arcon.include
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
                    conv.reply(users[user])
                    print(f"Replied to {user}")
                    conv.mute()
                    print(f"{user} muted")
                    conv.archive()
                    print(f"{conv.id} archived")
                    with open(arcon.log, "a") as f:
                        time_now = time.time()
                        f.write(f"{datetime.fromtimestamp(time_now)} ({time_now}): {user} found in modmail conversation. Replied, muted, marked read, and archived.\n")
                    break

if __name__ == '__main__':
    ModBot(arcon.AR).archive()
