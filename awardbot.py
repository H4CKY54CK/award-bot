import os
import re
import sys
import praw
import time
from string import printable
from constants import *
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

        # We defined `MAX_LEVEL` at the top of the script, as the length of the dictionary. 6 levels = Level 6 is the max
        if flair == MAX_LEVEL:
            comment.reply(MESSAGE_CODES['E17'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{URL}{comment.permalink}`\n")

        # Since the flair isn't maxed out, is it even one of the levels?
        elif flair in FLAIR_VALUES:

            # I swapped the keys and values in a new dictionary, so we can use 'Level 3' as the key, to get the value of 3 (it's key in the original dict)
            user_level = REVERSE_FLAIRS[flair]

            # Because of that, and because it's an integer, we can just increment it.
            new_flair = FLAIR_LEVELS[user_level+1]

            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(MESSAGE_CODES['E01'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{URL}{comment.permalink}`.\n")

            # If the user advanced to the max level, they get the invite.
            if new_flair == MAX_LEVEL:
                self.reddit.redditor(author).message(INVITE_SUBJ, INVITE_MSG)
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{time.time()}: Sent invite/invitation to `{author}`. `{URL}{comment.permalink}`.\n")

        # If the flair isn't at max level, and isn't even one of the levels, it could be that they have a custom flair, or they may not have one at all.
        # Checking if it's None or an empty string is easy, let's do that first. (I've seen both get returned from the data, so check for both)
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(MESSAGE_CODES['E01'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` successfully processed. `{author}` increased to `{new_flair}`. `{URL}{comment.permalink}`.\n")

        # If it's not max, and not one of the levels, and they definitely have one, then logic says they must have a custom flair.
        elif len(flair) > 0:
            comment.reply(MESSAGE_CODES['E17'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{chauthor}` unprocessed. Reason: already-top-level. `{URL}{comment.permalink}`\n")


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
                if comment.body == TRIGGER:

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
                        coolmsg = f"{MESSAGE_CODES['E16']} Remaining: {readable}"
                        comment.reply(coolmsg)

        # If something happens and we get an error, send itself right back the start of this function.
        except Exception as e:
            with open(ERROR_LOG, 'a') as f:
                f.write(f"{e}\n\n")
                time.sleep(5)
            self.collect()


    def on_cooldown(self, comment):
        """Your doing."""

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'a') as f:
                pass

        chauthor = str(comment.author)
        msg = f"grep '{chauthor}' {LOG_FILE} | grep 'successfully processed' | tail -1 | cut -d '.' -f1"
        last_award = os.popen(msg)
        last_award = last_award.read().rstrip('\n')
        try:
            if float(last_award) < 0:
                last_award = 0
        except:
            last_award = 0
        if comment.created_utc < float(last_award) + COOLDOWN_AMOUNT:
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
            comment.reply(MESSAGE_CODES['E11'])
            return False

        # If they are doing this to their own comment, Fail
        if pauthor == author:
            comment.reply(MESSAGE_CODES['E12'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: self award. `{URL}{comment.permalink}.`\n")
            return False

        # If the parent comment is the bot, Fail
        if pauthor == thebot:
            comment.reply(MESSAGE_CODES['E14'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: bot award. `{URL}{comment.permalink}.`\n")
            return False

        # If the parent comment is also an !award, Fail
        if parent.body == TRIGGER:
            comment.reply(MESSAGE_CODES['E13'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: award award. `{URL}{comment.permalink}`.\n")
            return False

        # Refresh to get replies, check replies to see if they've already awarded the parent comment before. If they have, Fail
        parent.refresh()
        # If there are actually replies, let's check them. If not, we skip this.
        if len(parent.replies) > 0:
            for reply in parent.replies:
                if reply.body == TRIGGER and str(reply.author) == author and reply.id != comment.id:
                    comment.reply(MESSAGE_CODES['E15'])
                    with open(LOG_FILE, 'a') as f:
                        f.write(f"{time.time()}: Award `{comment.id}` by `{author}` denied. Reason: already awarded. `{URL}{comment.permalink}`.\n")
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

        # Check submissions, sorted by highest karma first, in the last `TIMEFRAME` (probably 'week')
        for submission in self.subreddit.top(TIMEFRAME):

            # If the score meets the requirements, and is a self post...
            if submission.score >= KARMA_LIMIT and submission.is_self:
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
                    if len(user_flair) > 0 and user_flair not in FLAIR_VALUES:
                        self.process_message(msg)

                    # If they have a max level flair, send for flair assignment
                    elif user_flair == MAX_LEVEL:
                        self.process_message(msg)

                    # Any other scenario, they don't qualify, and tell them so. Mark message as read.
                    else:
                        msg.reply(MESSAGE_CODES['E22'])
                        with open(LOG_FILE, 'a') as f:
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

        valid = r"[a-zA-Z0-9!#$%&'()*+,-\./:;<=>?@_{|}~]+"
        author = str(msg.author)
        flair_class = '' or None
        body = msg.body
        valid_body = re.match(valid, body)

        # Split by newlines, into a list
        content = msg.body.split('\n')

        # If there's more than one item in the list, it was multi-lined. Respond and mark read.
        if len(content) > 1:
            msg.reply(MESSAGE_CODES['E23'])
            with open(LOG_FILE, 'a') as f:
                f.write(f"{time.time()}: Private message from `{author}` denied. Reason: multi-line.\n")
            msg.mark_read()

        # If there's only one item in list, it's fine. Assign it. Respond, mark read.
        elif len(content) == 1:

            if valid_body:
                new_flair = content[0].rstrip()[:64]

                # If their flair is longer than the limit, assign it, but tell them about it.
                if len(msg.body) > 64:
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(MESSAGE_CODES['E03'])
                    with open(LOG_FILE, 'a') as f:
                        f.write(f"{time.time()}: Private message from `{author}` processed (however, their flair got shortened due to the length of their message). Flair changed from `{self.flairs[author]}` to `{new_flair}`.\n")
                    msg.mark_read()

                # If it's not longer than the limit, assign it, respond with an 'okie dokie'.
                else:
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(MESSAGE_CODES['E02'])
                    with open(LOG_FILE, 'a') as f:
                        f.write(f"{time.time()}: Private message from `{author}` processed. Flair changed from `{self.flairs[author]}` to `{new_flair}`.\n")
                    msg.mark_read()
            else:
                msg.reply(MESSAGE_CODES["E21"])
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{time.time()}: Private message from `{author}` denied. Reason: illegal chars.\n")
                msg.mark_read()

def one():

    # Continuously run this function, which checks submissions for karma and inbox messages for custom flair assignment.
    while True:
        KarmaCheck(KC).check_subs_and_inbox()

def two():

    # Continuously run this function, which streams the comments. If the stream breaks, it'll just start it again.
    while True:
        CommentsStream(CT).collect()

def monitor(h1, h2):

    # Continuously check the children, and if anything stops them, spawn up a new one. Set daemon to True, so
    # that they can't make their own children, just as a safety measure. Parents also try to terminate their daemonic processes, but not well enough
    while True:
        time.sleep(.1)
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

    # Without this little function, as small as it is, it would be double the size right here. (the function `monitor` I mean, not the whole thing o_o)
    try:
        monitor(h1, h2)
    except:
        monitor(h1, h2)

if __name__ == '__main__':
    # Move to a known directory.
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    # Start
    main()
