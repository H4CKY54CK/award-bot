##AwardBot

Here's the quick and dirty instructions.

Your `awardbot.py` will sit somewhere. Obviously. But the first thing it does when ran, is make sure it's working from the directory that it's located in. This is to avoid mishaps in file handling. You'll need a `praw.ini` file in the same directory. If I haven't included a blank one, here's the template.

---

[site1]  
client_id =  
client_secret =  
username =  
password =  
user_agent =  
subreddit =  


[site2]  
client_id =  
client_secret =  
username =  
password =  
user_agent =  
subreddit =  

---

Legend:

site1 and site2: Arbitrary names that you will use to reference the section they are heading.  
client_id: client/app ID from `prefs -> apps` (you'll need two apps, one for each site, because we're running two instances of PRAW, but on the same account)  
client_secret: client/app secret from the same place as the ID. You'll have to click on `Edit` to actually be able to see it.  
username: Bot account. Same account in both sites.  
password: Same as above  
user_agent: Something unique and descriptive. Do something like <platform:app_name:subreddit::owner:/u/tehtrb>  
so something like `linux:awardbot1:comments:misanthropy::owner:/u/tehtrb` and `linux:awardbot2:inbox/submissions:misanthropy::owner:/u/tehtrb` or something like that)  
subreddit: Misanthropy  

Since it's an `.ini` file, you won't need quotes or anything surrounding the fields. It can be `username=myusername` or `username = myusername`, or I think it can even be `username:myusername`, but I know for sure equals signs work, so let's stick with what we know.

Take `site1` and `site2` and stick them in lines 293 & 298. It should look like `CommentsStream('sitenumberone').collect()` and `KarmaCheck('sitenumbertwo').check_subs_and_inbox()`. It doesn't matter which one, but only input the string, and don't move anything around. Everything should just work without any meddling.

To start the bot, you could call `python3 awardbot.py &` or install it as a service, as I'm sure you'll do. Keep an eye on their process IDs, in case they change. It should write to the `error_log.txt` if that happens anyway. so as long as you check occasionally for one or the other, that's good enough. I can't see it crashing that often, if at all, but I could be wrong. It's been known to happen.

Enjoy.
