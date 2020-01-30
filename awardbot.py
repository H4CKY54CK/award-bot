# Basic/General Info

# Keyword to trigger the bot
trigger = "!award"
# Path to error logfile. The first thing the bot does is change directory to where it's located, although an absolute path is still required.
error_log = "/home/hacky/error_log.txt"
# Path to regular logfile. The first thing the bot does is change directory to where it's located, although an absolute path is still required.
log_file = "/home/hacky/award_log.txt"
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


# Replies. (I need to verify the illegal characters thing, if there even are any, and I'll quick-edit the other one in soon.)

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

# These should really be constants, probably. Ah, well.
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
import time
from datetime import datetime
from multiprocessing import Process
from praw.models import Submission, Comment


class Login:
    """Base class for logging in and processing comments/submissions."""

    def __init__(self, site):

        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])


    def process_object(self, comment):
        """Process this comment, to determine how to level up the parent user."""

        child = comment.author
        # Reload comment by reinstantiating it, so that we have the most recent info.
        comment = self.reddit.comment(comment)
        # Instantiate an instance of the parent comment, so we can treat it like any other comment.
        parent = self.reddit.comment(comment.parent())
        author = str(comment.parent().author)
        flair = comment.parent().author_flair_text
        chauthor = str(comment.author)

        # Set the image flair to an empty string, because it is a required parameter to set a flair, even though we're only setting the text.
        flair_class = ''

        # We defined `max_lvl` at the top of the script, as the length of the dictionary. 6 levels = Level 6 is the max
        if flair == max_lvl:
            comment.reply(message_codes['E17'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{rurl}{comment.permalink}`\n")

        # Since the flair isn't maxed out, is it even one of the levels?
        elif flair in flair_values:

            # I swapped the keys and values in a new dictionary, so we can use 'Level 3' as the key, to get the value of 3 (it's key in the original dict)
            user_level = reverse_flair_levels[flair]

            # Because of that, and because it's an integer, we can just increment it.
            new_flair = flair_levels[user_level+1]

            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(message_codes['E01'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{rurl}{comment.permalink}`.\n")

            # If the user advanced to the max level, they get the invite.
            if new_flair == max_lvl:
                self.reddit.redditor(author).message(invite_subj, invite_msg)
                with open(log_file, 'a') as f:
                    f.write(f"{time.time()}: Sent invite/invitation to `{author}`. `{rurl}{comment.permalink}`.\n")

        # If the flair isn't at max level, and isn't even one of the levels, it could be that they have a custom flair, or they may not have one at all.
        # Checking if it's None or an empty string is easy, let's do that first. (I've seen both get returned from the data, so check for both)
        elif flair == None or flair == '':
            new_flair = flair_levels[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(message_codes['E01'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{rurl}{comment.permalink}`.\n")

        # If it's not max, and not one of the levels, and they definitely have one, then logic says they must have a custom flair.
        elif len(flair) > 0:
            comment.reply(message_codes['E17'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{rurl}{comment.permalink}`\n")


class CommentsStream(Login):
    """Subclass of Login. We inherit the __init__ login, so we don't need one."""


    def collect(self):
        """Stream the comments."""

        # Try all this...
        try:
            for comment in self.subreddit.stream.comments(skip_existing=True):

                # Comments return None when no new objects have been returned. Also when there's a hiccup somewhere. So we `continue` to the next comment.
                if comment is None:
                    continue

                # Since the comment exists, check if it's an !award.
                if comment.body == trigger:

                    # Must return False to pass.
                    if not self.on_cooldown(comment):
                        # Test against the conditions, must return True to pass.
                        if self.check_comment(comment):
                            # Send for processing.
                            self.process_object(comment)
                    # Since it returned True, do this.
                    else:
                        remaining = time.time()-comment.created_utc
                        readable = datetime.fromtimestamp(remaining)
                        coolmsg = f"{message_codes['E16']} Remaining: {readable}"
                        comment.reply(message_codes['E16'])
        # If something happens and we get an error, send itself right back the start of this function.
        except Exception as e:
            with open(error_log, 'a') as f:
                f.write(f"{e}\n\n")
                time.sleep(5)
            self.collect()


    def on_cooldown(self, comment):
        """Your doing."""

        if not os.path.exists(log_file):
            with open(log_file, 'a') as f:
                pass

        chauthor = str(comment.author)
        msg = f"grep '{chauthor}' {log_file} | grep 'successfully processed' | tail -1 | cut -d '.' -f1"
        last_award = os.popen(msg)
        last_award = float(last_award.read().rstrip('\n'))
        try:
            if last_award < 0:
                last_award = 0
        except:
            last_award = 0
        if comment.created_utc < last_award + cooldown_amount:
            return True
        return False


    def check_comment(self, comment):
        """Check the comment for conditions."""

        thebot = str(self.reddit.user.me())
        author = str(comment.author)
        parent = comment.parent()
        pauthor = str(parent.author)

        # If the parent is a submission, Fail
        if isinstance(parent, Submission):
            comment.reply(message_codes['E11'])
            return False

        # If they are doing this to their own comment, Fail
        if pauthor == author:
            comment.reply(message_codes['E12'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: self award. `{rurl}{comment.permalink}.`\n")
            return False

        # If the parent comment is the bot, Fail
        if pauthor == thebot:
            comment.reply(message_codes['E14'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: bot award. `{rurl}{comment.permalink}.`\n")
            return False

        # If the parent comment is also an !award, Fail
        if parent.body == trigger:
            comment.reply(message_codes['E13'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: award award. `{rurl}{comment.permalink}`.\n")
            return False

        # Refresh to get replies, check replies to see if they've already awarded the parent comment before. If they have, Fail
        parent.refresh()
        # If there are actually replies, let's check them. If not, we skip this.
        if len(parent.replies) > 0:
            for reply in parent.replies:
                if reply.body == trigger and str(reply.author) == author and reply.id != comment.id:
                    comment.reply(message_codes['E15'])
                    with open(log_file, 'a') as f:
                        f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: already awarded. `{rurl}{comment.permalink}`.\n")
                    return False

        ####
        # May possibly need this, in the event of missing comments (but not deleted). Only happened to me once, but it's apparently a thing.
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

        # Got passed all conditions, so return True and get on with it.
        return True


class KarmaCheck(Login):


    def check_subs_and_inbox(self):
        """Check submissions, then inbox items. No stream."""

        # Create a global dictionary that we don't have to pass around.
        self.flairs = {}
        valid = r'[a-zA-Z0-9_-]+'
        flair_class = '' or None

        # Check submissions, sorted by highest karma first, in the last `timeframe` (probably 'week')
        for submission in self.subreddit.top(timeframe):

            # If the score meets the requirements, and is a self post...
            if submission.score >= karma_limit and submission.is_self:
                author = str(submission.author)
                valid_user = re.match(valid, author)

                # and if we haven't replied to this submission before, and if the username is valid...
                if not self.already_replied(submission) and valid_user:

                    # Process it
                    self.process_object(submission)

        # If a user has a flair in the subreddit, add the user and their flair to the dict
        for item in self.subreddit.flair(limit=None):
            self.flairs.update({str(item['user']):item['flair_text']})

        # Check our inbox for new messages
        for msg in self.reddit.inbox.all():
            if msg.new:
                author = str(msg.author)
                valid_user = re.match(valid, author)

                # If the author is in our flair dict, and it's not a comment reply...
                if author in self.flairs and valid_user and not msg.was_comment:
                    user_flair = self.flairs[author]

                    # If they have a flair, but not one of the stock ones, send for flair assignment
                    if len(user_flair) > 0 and user_flair not in flair_values:
                        self.process_message(msg)

                    # If they have a max level flair, send for flair assignment
                    elif user_flair == max_lvl:
                        self.process_message(msg)

                    # Any other scenario, they don't qualify, and tell them so. Mark message as read.
                    else:
                        msg.reply(message_codes['E22'])
                        with open(log_file, 'a') as f:
                            f.write(f"{time.time()}: Private message from `{author}` denied. Reason: not-top-lvl.\n")
                        msg.mark_read()



    def already_replied(self, submission):
        """Whether we've replied to the submission once before or not."""


        for comment in submission.comments:
            if comment.author == self.reddit.user.me():
                return True
        return False


    def process_message(self, msg):
        """Flair assignment."""

        flair_class = '' or None
        author = str(msg.author)

        # Split by newlines, into a list
        content = msg.body.split('\n')

        # If there's more than one item in the list, it was multi-lined. Respond and mark read.
        if len(content) > 1:
            msg.reply(message_codes['E23'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Private message from `{author}` denied. Reason: multi-line.\n")
            msg.mark_read()

        # If there's only one item in list, it's fine. Assign it. Respond, mark read.
        elif len(content) == 1:
            new_flair = content[0].rstrip()[:64]
            self.subreddit.flair.set(author, new_flair, flair_class)
            msg.reply(message_codes['E02'])
            with open(log_file, 'a') as f:
                f.write(f"{time.time()}: Private message from `{author}` processed. Flair changed from `{self.flairs[author]}` to `{new_flair}`.\n")
            msg.mark_read()


def one():

    # Continuously run this function, which checks submissions for karma and inbox messages for custom flair assignment.
    while True:
        KarmaCheck('aufb-one').check_subs_and_inbox()

def two():

    # Continuously run this function, which streams the comments. If the stream breaks, it'll just start it again.
    while True:
        CommentsStream('aufb-two').collect()

def monitor(h1, h2):

    # Continuously check the children, and if anything stops them, spawn up a new one. Set daemon to True, so
    # that they can't make their own children, just as a safety measure. Parents also try to terminate their daemonic processes, but not well enough
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

    # Setup for multiprocessing. No arguments, since we know what we want to do already.
    h1 = Process(target=one)
    h1.daemon = True
    h1.start()
    h2 = Process(target=two)
    h2.daemon = True
    h2.start()

    # Without this little function, as small as it is, it would be double the size right here.
    try:
        monitor(h1, h2)
    except:
        monitor(h1, h2)

if __name__ == '__main__':
    # Move to a known directory.
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # Start
    main()
