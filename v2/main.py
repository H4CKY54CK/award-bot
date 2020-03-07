import os
import re
import json
import praw
import time
import datetime
from multiprocessing import Process


PRIMARY = ''
SECONDARY = ''
BOOK = 'queue.json'
KEYWORD = '!award'
COOLDOWN = 86400

FLAIR_LEVELS={
    1: 'Level 1',
    2: 'Level 2',
    3: 'Level 3',
    4: 'Level 4',
    5: 'Level 5',
    6: 'Max Level',
}

REVERSE_FLAIRS = {a:b for b, a in FLAIR_LEVELS.items()}
FLAIR_VALUES = FLAIR_LEVELS.values()
MAX_LEVEL = FLAIR_LEVELS[len(FLAIR_LEVELS)]

TIMEFRAME = 604800.0
KARMA = 100

class Denied:
    cooldown = f"Your !award has been added to the queue because you are still on cooldown. (Time remaining: "
    duplicate = "You have already !awarded this comment."
    post = "Only other comments can be !awarded."
    self_award = "You can't !award yourself."
    bot = "You can't !award the bot."
    award = "You can't !award other !awards."

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
                    continue
                else:
                    self.process_comment(comment)

    def check(self, comment):

        data = json.load(open(BOOK))
        recent = data['recent']
        user = str(comment.author)
        if user in recent.keys():
            last = recent[user].get('created', 0)
            awarded = recent[user].get('awarded', [])
        else:
            last = 0
            awarded = []
        parent = comment.parent_id
        if parent in awarded:
            return Denied.duplicate
        if parent.startswith('t3'):
            return Denied.post
        parent = comment.parent()
        parent_user = str(parent.author)
        if user == parent_user:
            return Denied.self_award
        if parent_user == self.THEBOT:
            return Denied.bot
        if parent.body == KEYWORD:
            return Denied.award
        if last + COOLDOWN > comment.created_utc:
            remaining = (last + COOLDOWN) - comment.created_utc
            queue = data['queue']
            if user not in queue.keys():
                queue.update({user:{}})
            queue[user].update({comment.id: {'created': comment.created_utc}})
            json.dump(data, open(BOOK, 'w'), indent=4)
            return Denied.cooldown + f"{datetime.timedelta(seconds=remaining)})"

        return True

    def process_comment(self, comment):

        parent = comment.parent()
        author = str(parent.author)
        flair = parent.author_flair_text
        chauthor = str(comment.author)
        flair_class = ''
        if flair == MAX_LEVEL:
            comment.reply("User already max level. But they appreciate your generosity.")
        elif flair in FLAIR_VALUES:
            user_level = REVERSE_FLAIRS[flair]
            new_flair = FLAIR_LEVELS[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply("Award recorded. Thank you.")
            self.add(comment)
            if new_flair == MAX_LEVEL:
                self.reddit.redditor(author).message("Invite", "Invitation")
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply("Award recorded. Thank you.")
            self.add(comment)
        elif len(flair) > 0:
            comment.reply("User has a custom flair already. But they appreciate your generosity.")

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
                            msg.reply("You lack the required level to assign yourself a custom flair.")
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
            msg.reply("Multi-line message detected. Please try again.")
            msg.mark_read()
        elif len(content) == 1:
            if valid_body:
                new_flair = content[0].rstrip()[:64]
                if len(msg.body) > 64:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(f"Your flair text exceeded reddit's limit of 64 characters, but I assigned what I could. Old: {old_flair} | New: {new_flair}")
                    msg.mark_read()
                else:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(f"Your flair has been set. Let me know if you change your mind! Old: {old_flair} | New: {new_flair}")
                    msg.mark_read()
            else:
                msg.reply("Illegal characters detected. Please try again.")
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
            submission.reply("You've acquired enough karma on this submission to earn yourself a level up!")
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            submission.reply("You've acquired enough karma on this submission to earn yourself a level up!")
        elif len(flair) > 0:
            pass

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