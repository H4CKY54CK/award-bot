#! /usr/bin/python3

import os
import sys
import praw
import time
import argparse
# Rename your archiverconfig.py to arconfig.py so we can import yours.
try:
    import arconfig as arcon
# That way, the config can be freely edited by the developer, and won't wipe the user's current settings.
except:
    import archiverconfig as arcon
from collections import defaultdict
from praw.models import Comment, Submission

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
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])

    def verify(self, coll, args=None, kind=None):

        confirm = ['y', 'ye', 'yes']
        deny = ['n', 'no']

        if kind == 'comments':
            msg = f"Are you sure you want to remove these comments? [Y/N]: "
        elif kind == 'submissions':
            msg = f"Are you sure you want to remove these submissions? [Y/N]: "

        amount = len(coll)
        for key in coll.keys():
            print(f"Amount of {kind} found for {key}: {len(coll[key])}")
        if args.remove and coll:
            check = input(f"{msg}")
            if check.lower() in confirm:
                for key in coll.keys():
                    user = coll[key]
                    count = 0
                    for item in user:
                        count += 1
                        print(f"Removing {count} of {len(user)}...", end='\r')
                        item.mod.remove()
                    print('')
            else:
                pass

    def modsearch(self, args=None):

        users = NameList(args.user)
        comments = defaultdict(list)
        submissions = defaultdict(list)

        if args.limit:
            com = self.subreddit.comments()
            sub = self.subreddit.new()
        else:
            com = self.subreddit.comments(limit=None)
            sub = self.subreddit.new(limit=None)

        if args.comments:
            for item in com:
                if item is None or item.removed:
                    continue
                if str(item.author).lower() in users:
                    comments[str(item.author)].append(item)
        if args.submissions:
            for item in self.subreddit.new(limit=None):
                if item is None:
                    continue
                if str(item.author).lower() in users:
                    submissions[str(item.author)].append(item)
        if comments:
            self.verify(comments, args, kind='comments')
        if submissions:
            self.verify(submissions, args, kind='submissions')

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    bot = ModBot(arcon.AR)
    parser.add_argument('user', type=str, nargs='*', help="user(s) for whom you wish to identify comments/submission (can take multiple users)")
    parser.add_argument('-c', '--comments', dest='submissions', action='store_false', help="limit the search to comments (by default, searches for both comments and submissions)")
    parser.add_argument('-s', '--submissions', dest='comments', action='store_false', help="limit the search to submissions (by default, searches for both comments and submissions)")
    parser.add_argument('-R', '--remove', dest='remove', action='store_true', help='remove any comments/submissions by given user(s) in the subreddit')
    parser.add_argument('-L', '--limit', dest='limit', action='store_true', help="for quicker searches, limit the amount of comments/submission to the last 100 (default is the last 1000)")
    parser.set_defaults(func=bot.modsearch)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())
