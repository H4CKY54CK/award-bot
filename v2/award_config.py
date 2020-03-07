PRIMARY = 'mhcp1'
SECONDARY = 'mhcp2'
BOOK = 'queue.json'
KEYWORD = '!award'
COOLDOWN = 86400

LOGS = 'logs.txt'

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

RECORDED = "Award recorded. Thank you."

QUEUEDOWN = "Your !award has been added to the queue because you are still on cooldown. (Time remaining: "
DUPLICATE = "You have already !awarded this comment."
POST = "Only other comments can be !awarded."
SELF_AWARD = "You can't !award yourself."
BOT_AWARD = "You can't !award the bot."
AWARD_AWARD = "You can't !award other !awards."
ALREADY_MAX = "User already max level. But they appreciate your generosity."
CUSTOM_FLAIR = "User has a custom flair already. But they appreciate your generosity."
LACK_LEVEL = "You lack the required level to assign yourself a custom flair."
MULTI_LINE = "Multi-line message detected. Please try again."
EXCEEDED = "Your flair text exceeded reddit's limit of 64 characters, but I assigned what I could."
FLAIR_CHANGED = "Your flair has been set. Let me know if you change your mind! Old:"
ILEGAL = "Illegal characters detected. Please try again."
SUBMISSION_KARMA = "You've acquired enough karma on this submission to earn yourself a level up!"
INVITE_SUBJECT = "You're invited!"
INVITE_BODY = "Explanation of invitation... Sorry, I got lazy."