#! /usr/bin/python3

import os
import sys
import praw
import time
import argparse
from collections import defaultdict
from praw.models import Comment, Submission
# from config import *

class NameList(object):
    def __init__(self, names):
        self.names = names

    def __contains__(self, name):
        return name.lower() in (n.lower() for n in self.names)

    def add(self, name):
        self.names.append(name)

class ModBot:

    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['test_subreddit'])

    def archive(self, args=None):

        users = NameList(args.user)

        conversations = self.subreddit.modmail.conversations()
        for conv in conversations:
            authors = []
            for author in conv.authors:
                if str(author).lower() in users and conv.unread:
                    conv.mute()
                    conv.read()
                    conv.archive()
                    print(f"{str(author)} found in {conv}. Muted, read, archived.")
                    break

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    bot = ModBot('hacky')
    parser.add_argument('user', type=str, nargs='*', help="user(s) for whom you wish to identify comments/submission (can take multiple users)")
    parser.set_defaults(func=bot.archive)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())
