# Basic/General Info

# Keyword to trigger the bot
trigger = "!award"
# Path to error logfile. The first thing the bot does is change directory to it's own current location, so the path can be relative.
error_log = "error_log.txt"
# Path to regular logfile. The first thing the bot does is change directory to it's own current location, so the path can be relative.
log_file = "award_log.txt"
# How much karma is required for self posts / text posts to trigger a level up.
karma_limit = 100
# How far back to look for submissions over the karma limit. One of: "hour", "day", "week", "month", "year", but month and year aren't reliable in your case.
timeframe = "week"
# Invitation subject.
invite_subj = "You're invited!"
# Invitation message
invite_msg = "Not anywhere physically, but to a custom flair, rather. Try to maintain your excitement, please."
# Cooldown between !awards
cooldown_amount = 24400.0


# Replies.

message_codes = {
    'E00': "I've encountered an unexpected error.",
    'E01': "Your `!award` has been recorded.",
    'E02': "I've assigned your flair.",
    'E03': "I've assigned your flair. However, it was longer than Reddit's flair text limit of 64 characters and was cut short.", # TODO
    'E11': "Only comments can be `!award`ed, not submissions.",
    'E12': "You cannot `!award` yourself.",
    'E13': "You cannot `!award` other `!award`s.",
    'E14': "You cannot `!award` the AwardBot.",
    'E15': "You have already `!award`ed this comment.",
    'E16': "You cannot `!award` until your cooldown is over.",
    'E17': "This user is already at the maximum level.",
    'E21': "I could not assign your flair due to illegal characters in your message.", # TODO
    'E22': "You lack the required level to assign yourself a custom flair.",
    'E23': "A multi-line message cannot be assigned as a flair.",
}

# Flair Levels (Dynamically adjustable, although with some side effects and/or a tad bit of assembly required)

flair_levels={
    1: 'Level 1',
    2: 'Level 2',
    3: 'Level 3',
    4: 'Level 4',
    5: 'Level 5',
    6: 'Max Level',
}

##################
## DON'T MODIFY ##

rurl = 'https://reddit.com'
reverse_flair_levels = {a:b for b, a in flair_levels.items()}
flair_values = flair_levels.values()
max_lvl = flair_levels[len(flair_levels)]

## DON'T MODIFY ##
##################

import os
import re
import sys
import praw
from datetime import datetime
from multiprocessing import Process
from praw.models import Submission, Comment


class Login:


    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])


    def process_object(self, comment):
        """Process this comment, to determine how to level up the parent user."""

        # Reload comment, so that we have the most recent info.
        child = comment.author
        comment = self.reddit.comment(comment)
        parent = self.reddit.comment(comment.parent())
        author = str(comment.parent().author)
        flair = comment.parent().author_flair_text
        chauthor = str(comment.author)

        flair_class = ''

        if flair == max_level:
            comment.reply(message_codes['E17'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{rurl}{comment.permalink}`\n")

        elif flair in flair_values:
            user_level = reverse_flair_levels[flair]
            new_flair = flair_levels[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(message_codes['E01'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{rurl}{comment.permalink}`.\n")
            if new_flair == max_lvl:
                self.reddit.redditor(author).message(invite_subj, invite_msg)
                with open(log_file, 'a') as f:
                    f.write(f"{datetime.now()}: Sent invite/invitation to `{author}`. `{rurl}{comment.permalink}`.\n")

        elif flair == None or flair == '':
            new_flair = flair_levels[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(message_codes['E01'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{rurl}{comment.permalink}`.\n")

        elif len(flair) > 0:
            comment.reply(message_codes['E17'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{rurl}{comment.permalink}`\n")


class CommentsStream(Login):


    def collect(self):
        """Fetch the comments, per submission."""

        try:
            for comment in self.subreddit.stream.comments(skip_existing=True):
                if comment is None:
                    continue
                if comment.body == trigger:
                    if not self.on_cooldown(comment) and self.check_comment(comment):
                        self.process_object(comment)
                    elif self.on_cooldown(comment):
                        comment.reply(message_codes['E16'])
        except Exception as e:
            with open(error_log, 'a') as f:
                f.write(f"{e}\n\n")
                time.sleep(5)
            self.collect()


    def on_cooldown(self, comment):

        if not os.path.exists(log_file):
            with open(log_file, 'a') as f:
                pass

        chauthor = str(comment.author)
        msg = f"grep '{chauthor}' {log_file} | grep 'successfully processed' | tail -1 | cut -d '.' -f1"
        last_award = os.popen(msg)
        last_award = last_award.read().rstrip('\n')
        try:
            if last_award < 0:
                last_award = 0
        except:
            last_award = 0
        if comment.created_utc < float(last_award) + cooldown_amount:
            return True
        return False


    def check_comment(self, comment):
        """Check the comment for conditions."""

        thebot = str(self.reddit.user.me())
        author = str(comment.author)
        parent = comment.parent()
        pauthor = str(parent.author)

        if isinstance(parent, Submission):
            comment.reply(message_codes['E11'])
            return False

        if pauthor == author:
            comment.reply(message_codes['E12'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{author}` denied. Reason: self award. `{rurl}{comment.permalink}.`\n")
            return False

        if pauthor == thebot:
            comment.reply(message_codes['E14'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{author}` denied. Reason: bot award. `{rurl}{comment.permalink}.`\n")
            return False

        if parent.body == trigger:
            comment.reply(message_codes['E13'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Award `{comment.id}` by `{author}` denied. Reason: award award. `{rurl}{comment.permalink}`.\n")
            return False

        parent.refresh()
        if len(parent.replies) > 0:
            for reply in parent.replies:
                if reply.body == trigger and str(reply.author) == author and reply.id != comment.id:
                    comment.reply(message_codes['E15'])
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: Award `{comment.id}` by `{author}` denied. Reason: already awarded. `{rurl}{comment.permalink}`.\n")
                    return False
        else:
            return True
        ####
        # May possibly need this
        #
        #
        # old_id = parent.id
        # parent.refresh()
        # if parent.id != old_id:
        #     try:
        #         time.sleep(10)
        #         parent.refresh()
        #     except praw.exceptions.ClientException:
        #         print('SKIPPING due to ClientException:', comment, comment.body)
        #         pass
        ####
        return True


class KarmaCheck(Login):


    def check_subs_and_inbox(self):

        valid = r'[a-zA-Z0-9_-]+'
        self.flairs = {}
        flair_class = '' or None

        for submission in self.subreddit.top(timeframe):
            if submission.score >= karma_limit and submission.is_self:
                author = str(submission.author)
                valid_user = re.match(valid, author)
                if not self.already_replied(submission) and valid_user:
                    self.process_object(submission)

        for item in self.subreddit.flair(limit=None):
            self.flairs.update({str(item['user']):item['flair_text']})

        for msg in self.reddit.inbox.all():
            if msg.new:
                author = str(msg.author)
                valid_user = re.match(valid, author)
                if author in self.flairs and valid_user and not msg.was_comment:
                    user_flair = self.flairs[author]
                    if len(user_flair) > 0 and user_flair not in flair_values:
                        self.process_message(msg)
                    elif user_flair == max_lvl:
                        self.process_message(msg)
                    else:
                        msg.reply(message_codes['E22'])
                        with open(log_file, 'a') as f:
                            f.write(f"{datetime.now()}: Private message from `{author}` denied. Reason: not-top-lvl.\n")
                        msg.mark_read()



    def already_replied(self, submission):

        for comment in submission.comments:
            if comment.author == self.reddit.user.me():
                return True
        return False


    def process_message(self, msg):

        flair_class = '' or None
        author = str(msg.author)
        content = msg.body.split('\n')
        if len(content) > 1:
            msg.reply(message_codes['E23'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Private message from `{author}` denied. Reason: multi-line.\n")
            msg.mark_read()
        elif len(content) == 1:
            new_flair = content[0].rstrip()[:64]
            self.subreddit.flair.set(author, new_flair, flair_class)
            msg.reply(message_codes['E02'])
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now()}: Private message from `{author}` processed. Flair changed from `{self.flairs[author]}` to `{new_flair}`.\n")
            msg.mark_read()


def one():

    while True:
        KarmaCheck('aufb-one').check_subs_and_inbox()

def two():

    while True:
        CommentsStream('aufb-two').collect()

def monitor(h1, h2):

    while True:
        if not h1.is_alive():
            h1 = Process(target=one)
            h1.daemon = True
            h1.start()
        if not h2.is_alive():
            h2 = Process(target=two)
            h2.daemon = True
            h2.start()

def main():

    h1 = Process(target=one)
    h1.daemon = True
    h1.start()
    h2 = Process(target=two)
    h2.daemon = True
    h2.start()

    try:
        monitor(h1, h2)
    except:
        monitor(h1, h2)


if __name__ == '__main__':
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()
