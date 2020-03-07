import os
import re
import json
import praw
import time
import datetime
from award_config import *
from multiprocessing import Process


class Bot:

    def __init__(self, site):
        if not os.path.exists(BOOK):
            data = {'queue': {}, 'recent': {}, 'submissions': []}
            json.dump(data, open(BOOK, 'w'), indent=4)
        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(self.reddit.config.custom['subreddit'])
        self.THEBOT = str(self.reddit.user.me())

    def start_stream(self):

        print(self.subreddit.display_name)
        for comment in self.subreddit.stream.comments(skip_existing=True, pause_after=0):
            if comment is None:
                continue
            if comment.body == KEYWORD:
                state = self.check(comment)
                if type(state) == str:
                    comment.reply(state)
                else:
                    self.process_comment(comment)

    def check(self, comment):

        data = json.load(open(BOOK))
        recent = data['recent']
        user = str(comment.author)
        parent = comment.parent()
        parent_id = comment.parent_id
        parent_user = str(parent.author)
        if user in recent.keys():
            last = recent[user].get('created', 0)
            awarded = recent[user].get('awarded', [])
        else:
            last = 0
            awarded = []
        if parent_id in awarded:
            return DUPLICATE
        if parent_id.startswith('t3'):
            return POST
        if user == parent_user:
            return SELF_AWARD
        if parent_user == self.THEBOT:
            return BOT_AWARD
        if parent.body == KEYWORD:
            return AWARD_AWARD
        if last + COOLDOWN > comment.created_utc:
            remaining = (last + COOLDOWN) - comment.created_utc
            queue = data['queue']
            if user not in queue.keys():
                queue.update({user:{}})
            queue[user].update({comment.id: {'created': comment.created_utc}})
            json.dump(data, open(BOOK, 'w'), indent=4)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {comment.id} entered into queue.")
            return QUEUEDOWN + f"{datetime.timedelta(seconds=remaining)})"

        return True

    def process_comment(self, comment):

        parent = comment.parent()
        author = str(parent.author)
        flair = parent.author_flair_text
        chauthor = str(comment.author)
        flair_class = ''
        if flair == MAX_LEVEL:
            comment.reply(ALREADY_MAX)
        elif flair in FLAIR_VALUES:
            user_level = REVERSE_FLAIRS[flair]
            new_flair = FLAIR_LEVELS[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(RECORDED)
            self.add(comment)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} has been incremented one level, courtesy of {chauthor}.\n")
            if new_flair == MAX_LEVEL:
                self.reddit.redditor(author).message(INVITE_SUBJECT, INVITE_BODY)
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(RECORDED)
            self.add(comment)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} has been incremented one level, courtesy of {chauthor}.\n")
        elif len(flair) > 0:
            comment.reply(CUSTOM_FLAIR)

    def add(self, comment):

        data = json.load(open(BOOK))
        recent = data['recent']
        author = str(comment.author)
        if author not in recent.keys():
            recent.update({author:{'created': comment.created_utc, 'awarded': [comment.parent_id]}})
        else:
            recent[author].update({'created': comment.created_utc})
            recent[author]['awarded'].append(comment.parent_id)
        json.dump(data, open(BOOK, 'w'), indent=4)

    def start_checking(self):

        while True:
            data = json.load(open(BOOK))
            self.flairs = {}
            valid = r'[a-zA-Z0-9_-]+'
            for submission in self.subreddit.new(limit=None):
                if submission.created_utc > (time.time() - TIMEFRAME):
                    if submission.score >= KARMA and submission.is_self:
                        author = str(submission.author)
                        if submission.id not in data['submissions']:
                            data['submissions'].append(submission.id)
                            self.process_submission(submission)
                else:
                    continue
            for item in self.subreddit.flair(limit=None):
                self.flairs.update({str(item['user']):item['flair_text']})

            for msg in self.reddit.inbox.all():
                if msg is None or msg.distinguished:
                    continue
                if msg.new:
                    author = str(msg.author)
                    valid_user = re.match(valid, author)
                    if author in self.flairs and valid_user and not msg.was_comment:
                        user_flair = self.flairs[author]
                        if len(user_flair) > 0 and user_flair not in FLAIR_VALUES:
                            self.process_message(msg)
                        elif user_flair == MAX_LEVEL:
                            self.process_message(msg)
                        else:
                            msg.reply(LACK_LEVEL)
                            msg.mark_read()
            queue = data['queue']
            for user in queue:
                user = queue[user]
                for itemid in list(user):
                    item = user[itemid]
                    if item['created'] + COOLDOWN < time.time():
                        comment = self.reddit.comment(itemid)
                        self.process_comment(comment)
                        del user[itemid]
                        json.dump(data, open(BOOK, 'w'), indent=4)

    def process_message(self, msg):

        valid = r"[a-zA-Z0-9!#$%&'()*+,-\./:;<=>?@_{|}~]+"
        author = str(msg.author)
        flair_class = '' or None
        body = msg.body
        valid_body = re.match(valid, body)
        content = msg.body.split('\n')
        if len(content) > 1:
            msg.reply(MULTI_LINE)
            msg.mark_read()
        elif len(content) == 1:
            if valid_body:
                new_flair = content[0].rstrip()[:64]
                if len(msg.body) > 64:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(EXCEEDED + f" Old: {old_flair} | New: {new_flair}")
                    msg.mark_read()
                    with open(LOGS, 'a') as f:
                        f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} user flair has been changed. Source: inbox. Old flair: {old_flair} | New flair: {new_flair}.\n")
                else:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(FLAIR_CHANGED + f" {old_flair} | New: {new_flair}")
                    msg.mark_read()
                    with open(LOGS, 'a') as f:
                        f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} user flair has been changed. Source: inbox. Old flair: {old_flair} | New flair: {new_flair}.\n")
            else:
                msg.reply(ILLEGAL)
                msg.mark_read()

    def process_submission(self, submission):

        submission = self.reddit.submission(submission)
        author = str(submission.author)
        flair = submission.author_flair_text
        flair_class = ''
        if flair == MAX_LEVEL:
            pass
        elif flair in FLAIR_VALUES:
            user_level = REVERSE_FLAIRS[flair]
            new_flair = FLAIR_LEVELS[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            submission.reply(SUBMISSION_KARMA)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} incremented one level. Source: Submission threshold met. {submission.id}.\n")
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            submission.reply(SUBMISSION_KARMA)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} incremented one level. Source: Submission threshold met. {submission.id}.\n")
        elif len(flair) > 0:
            pass

def backup_manager(b1,b2):
    while True:
        if not b1.is_alive():
            b1 = Process(target=bot1.start_stream)
            b1.daemon = True
            b1.start()
            b1.join()
        if not b2.is_alive():
            b2 = Process(target=bot2.start_checking)
            b2.daemon = True
            b2.start()
            b2.join()
        time.sleep(.1)


if __name__ == '__main__':
    bot1 = Bot(PRIMARY)
    bot2 = Bot(SECONDARY)
    b1 = Process(target=bot1.start_stream)
    b2 = Process(target=bot2.start_checking)
    b1.daemon = True
    b2.daemon = True
    b1.start()
    b2.start()
    b1.join()
    b2.join()
    backup_manager(b1,b2)