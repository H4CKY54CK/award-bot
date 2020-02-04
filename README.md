#Award-Bot

## NEWS/ANNOUNCEMENTS

 Rename your `constants.py` to `config.py`, or don't, I don't care. Either way, it will pick it up. This just makes it more convenient for me.

## Description

 A bot for handling a custom award system for a subreddit. When ran, spawns two children. Child 1 monitors a subreddit's comments, live, and levels users up based on `!awards` they get from other users in reply. Child 2 does two things: 1) parses messages from users who are at the highest level and assigns them custom flair (once you reach top level, you can change your flair as often as you wish). 2) check the subreddit for submissions with 100 karma or more, and awards them a level up, same as an `!award` would do.

 This *does* mean it's using the multiprocessing module. However, don't be alarmed. The parent has only one job: Restart the children if/when they die. There's no fancy loop, or queue, or pool... Just a while loop that checks on the state of the two childrenwith a short nap on every iteration. Raising children is tough.

###### Contents

 Award-Bot
 CommentRemover (on the command line, `submod -h`)
 ModMailArchiver (you'll need to run this one like a script with `python archiver.py file`, the file being a .txt file with a list of user names)
    -Rest of this feature coming soon
