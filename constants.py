# Basic/General Info

# Keyword to trigger the bot
TRIGGER = "!award"
# Path to error logfile. The first thing the bot does is change directory to where it's located, although an absolute path is still required.
ERROR_LOG = "/home/hacky/error_log.txt"
# Path to regular logfile. The first thing the bot does is change directory to where it's located, although an absolute path is still required.
LOG_FILE = "/home/hacky/award_log.txt"
# How much karma is required for self posts / text posts to trigger a level up.
KARMA_LIMIT = 100
# How far back to look for submissions over the karma limit. One of: "hour", "day", "week", "month", "year", but month and year aren't reliable in your case.
TIMEFRAME = "week"
# Invitation subject.
INVITE_SUBJ = "You're invited!"
# Invitation message
INVITE_MSG = "Not anywhere physically, but to a custom flair, rather. Try to maintain your excitement, please."
# Cooldown between !awards, in seconds, as a float. (Some common ones: 8h = 28800, 24h = 86400, 2d = 172800, 3d = 259200, 5d = 432000)
COOLDOWN_AMOUNT = 28800.0
# Also, I don't think this will be relevant in any way, but there is about a 5 minute difference between reddit's time server and 



# Replies. (I need to verify the illegal characters thing, if there even are any, and I'll quick-edit the other one in soon.)

MESSAGE_CODES = {
    'E00': "I've encountered an unexpected error.",
    'E01': "Your `!award` has been recorded.",
    'E02': "I've assigned your flair.",
    'E03': "I've assigned your flair. However, it was longer than Reddit's flair text limit of 64 characters and was cut short.",
    'E11': "Only comments can be `!award`ed, not submissions.",
    'E12': "You cannot `!award` yourself.",
    'E13': "You cannot `!award` other `!award`s.",
    'E14': "You cannot `!award` the AwardBot.",
    'E15': "You have already `!award`ed this comment.",
    'E16': "You cannot `!award` until your cooldown is over.",
    'E17': "This user is already at the maximum level.",
    'E21': "I could not assign your flair due to illegal characters in your message. (If it's not on a generic 104 key keyboard, you can't use it.",
    'E22': "You lack the required level to assign yourself a custom flair.",
    'E23': "A multi-line message cannot be assigned as a flair.",
}

# Flair Levels (Dynamically adjustable, although with some side effects and/or a tad bit of assembly required)

FLAIR_LEVELS={
    1: 'Level 1',
    2: 'Level 2',
    3: 'Level 3',
    4: 'Level 4',
    5: 'Level 5',
    6: 'Max Level',
}

URL = 'https://reddit.com'
REVERSE_FLAIRS = {a:b for b, a in FLAIR_LEVELS.items()}
FLAIR_VALUES = FLAIR_LEVELS.values()
MAX_LEVEL = FLAIR_LEVELS[len(FLAIR_LEVELS)]
