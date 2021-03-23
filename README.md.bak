Quick Notes:
    It will create it's own data file. Don't worry about it.
    It will maintain it's own data file. Don't worry about that either.
    It _might_ populate it's own history based on what your current award bot has collected. I dunno yet. Gotta think that one out.
    Look at how lean it is! ermagerd

# What's new?

- This is version 2 of the award bot. It's leaner and faster. It's also a rough draft, so it will need it's data files populated with everything from the launch of the first one, to now. I realize this is not ideal, but that's something I can do by hand. I don't mind. Just give this one a chance to show you what it's capable of, and I'm sure you'll love it.

## Things to note.

- Not only is there less code overall, there's also only 1 bot class. The rejection messages get their own class as well, rather than a massive dictionary labeled with numbers. This way is less confusing, and slightly more maintainable. There are also only 2 files! 3 if you count the log. How many did the first one need? `>_>` Everything is packed into one datafile, and yes it's a JSON. That made it far easier to manage the actual data while writing this. You don't actually have to concern yourself with the JSON file, as it's self-maintaining. It cleans up it's queue as it processes it. It does, however, keep a hard copy of all the comment IDs, usernames, the parent comment IDs that each individual comment ID was directed at, and the time the !awards were made. It also keeps a copy of all the submissions that pass the karma threshold. This is how it knows what's what.

#### Final Tasks

- I just remembered the thing about deleting a comment to bypass the !award checking. I don't _think_ that's possible in this version, but I can't say for sure until I test it. Or you test it.
- Move messages to variables.
- Add logging.
- That's it, really. I rebuilt the comments stream half, and c/p the submission/inbox half (which already ran fast). So, it got the makeover it needed in the areas it needed it most. I'm sure there's still some room for improvement, but this is orders of magnitude better than before, so maybe that'll be V3.

Another important note, is that it doesn't use regular IDs to track who's been awarded. It uses the 'fullname', with the 'kind' prefix. This also keeps us lean, as submissions can be identified by their prefix with a simple string operation, rather than importing "Submission" and comparing the parent of the comment against that, which is slow. But the !award comments are regular IDs.

My leisurely tests showed an average response time of about 5 seconds. If it seems much longer, it is most likely due to reddit not updating the page data fast enough. To get an unbiased resposne reading, either fetch the `created_utc` attribute from comment and comment.parent(), or turn on notifications on your phone, and time it that way. You should immediately notice the difference.