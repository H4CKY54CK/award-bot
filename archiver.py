#! /usr/bin/python3

import os
import sys
import praw
import time
from datetime import datetime
import archiverconfig as arcon


class ModBot:

    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])

    def archive(self):

        users = arcon.include
        msgs = {value:key for key, value in users.items()}
            
        conversations = self.subreddit.modmail.conversations()
        for conv in conversations:
            for author in conv.authors:
                user_name = str(author).lower()
                if user_name in users and conv.unread:
                    conv = self.subreddit.modmail(conv.id)
                    conv.reply(users[user_name])
                    conv.mute()
                    conv.archive()
                    with open(arcon.log, "a") as f:
                        time_now = time.time()
                        f.write(f"{datetime.fromtimestamp(time_now)} ({time_now}): {user_name} found in modmail conversation. Replied, muted, marked read, and archived.\n")
                    break

if __name__ == '__main__':
    ModBot(arcon.AR).archive()
