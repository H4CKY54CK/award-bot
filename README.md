#Award-Bot

  Award-Bot monitors comments in real time, leveling up users who receive an `!award` in reply to a comment they've made. All `!award`s get loaded into a personal queue, only applicable to the user who is issuing an `!award`. The oldest `!award`s are processed first, with an optional and adjustable cooldown period in between. (I.E. Issuing multiple `!award`s at once will only yield one `!award` per cooldown period. If the cooldown is 24 hours, and you have multiple items in the queue waiting to be processed, as soon as your cooldown is up, the oldest `!award` in your queue will be processed first, and so on. That means you can keep queueing up your `!award`s you'd like to issue, but keep in mind the limit for the queue is 3 by default (also adjustable), and that you will be unable to issue an `!award` in a spontaneous manner. They will just keep adding into the queue until the queue is empty, whereby allowing you to `!award` in the moment again.
  
####TODO

First order of business:

- [ ] Semantic Versioning
- [ ] Re-release the bot, after verifying the new framework is an improvement over the previous design.
- [ ] Create some sort of script that tests all functionality, eliminating the need for human testing, and optimizing production.
- [ ] Condense, cleanup, investigate data files for resiliency. (PickleDB left files corrupted when shut down unexpectedly. Pretty sure I can get around this by not using PickleDB)
- [ ] Fix data-storing solution

####Getting Started


######archiver.py

  First, we'll go over the modmail archiver, `archiver.py`. This is intended to be a very simple script, and can be used by running `python3 archiver.py` or `python archiver.py`, just like any other python file. It will search your unread modmail, and reply, mute, and then archive any modmail conversations that contain any of the usernames listed in `archiverconfig.py`. Something to keep in mind, though, is that it seems like tinkering with a modmail conversation causes a problem in the archiver. I had trouble testing it initially due to this, but I think I've taken care of it now. In any case, should you happen to run into the same issue, that's why.

######submod.py

  Next, we'll go over the comment remover, `submod.py`. It's intended to be used like a command line tool would be. This can be done several different ways...

  * `python3 submod.py <user(s)> [-c] [-s] [-R] [-L]` or if on windows, use `python` instead of `python3`
  * `./submod.py <user(s)> [-c] [-s] [-R] [-L]` if you make it an executable

#

  By default, calling `python3 submod.py user1 user2` etc. will search for their comments and submission, up to the last 1000 of each in the subreddit. It will report back to you how many it finds for each user specified.

  To limit the search to comments only, use `-c`. To only search submissions, use `-s`. To limit how far back the search will go, use `-L` followed by an integer, between 1 and 1000. 

  To actually remove the comments it finds, use `-R`. It will report back how many comments and submissions were found for each user (or just one, if only one is specified), followed by a confirmation that you really do intend to remove these items.

  It's as simple as that. For a better help menu, just use `-h` like you would a normal command.
