# Site 3 from your `praw.ini` (AKA app number 3)
AR = ""

# Path to log
LOG = ""

# List of users to look for in modmail conversations. (dict, so use `user: msg`)
# None = random msg

INCLUDE = {
"user1": None,
"user2": "Stop harassing my mother.",
"user3": "And YOU stop harassing my grandmother!",
"user4": None,
}

# Simple list of random messages that will be used in place of any `None` values
# above. (list, so each line needs surrounded in quotes, with a trailing comma)

RANMSG = [
"Sorry to see you go. But not really.",
"Here's some reading material for you during your quiet time: `THE RULES`.",
"Bye.",
]
