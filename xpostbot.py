#Copyright 2017, Meggie Cook

'''

'''

#The Reddit API Wrapper
import praw
#File that contains the credentials for /u/X_Post_Bot
import config
#For pausing in between retrieving a new comment/subreddit
import time
#To retrieve files from directory
import os
#Exceptions that could occur when finding if subreddit exists
from prawcore import PrawcoreException

'''
This method will create a Reddit instance so the bot can login to reddit. For
security reasons, almost all the credentials will be stored in a Config file
which will not be uploaded onto Github.
'''
def login():
	#Create a new instance of Reddit
	reddit = praw.Reddit(username = config.username,
			password = config.password,
			client_id = config.client_id,
			client_secret = config.client_secret,
			user_agent = "X_Post_Bot")

	print("Logged in!")

	return reddit

'''
This is the main method for this bot: if a comment mentions the bot as the first word of
the comment, and the message was unread, the X_Post_Bot will interpret the rest of the
words as the name of the subreddit to repost to. If the comment does mention the bot but
doesn't follow the correct format, it would reply with a comment showing that format.
'''
def bot_submit(reddit):
	print("Enter submit bot")

	#User must mention the bot's account for the submission to be crossposted
	for comment in reddit.inbox.mentions():

		#Only unread messages will be processed
		if comment in reddit.inbox.unread():
			old_submission = comment.submission

			#Keep track of the name of the sub submitted already 
			submitted_subs = []

			#Store the Submission objects after submitting
			submissions = []

			#Split post by space to easily extract subreddit name
			body = comment.body.split(" ") 

			#Proceed if the comment is in the correct format, which is:
			#/u/X_Post_Bot subreddit1 subreddit2 subreddit3
			if len(body) > 1 and body[0] == "/u/X_Post_Bot":

				#Ignore the bot metion inn the beginning
				for i in range(1, len(body)):
					subreddit = body[i]
					
					#Only proceed if subreddit exists and the bot hasn't crossposted to the subreddit already
					if subreddit_exists(subreddit, reddit) and subreddit not in submitted_subs:

						#Alter the body of the new submission
						new_submission_body = new_submission_text(old_submission)

						#Address that the submission is a duplicate on the title
						title = "(X-post by /u/" + old_submission.author.name + ") "+ old_submission.title

						#TODO: Create different submission depending whether or not the original post was a link
						#		or a text post

						#Submit the X-Post and store it into a variable
						new_submission = reddit.subreddit(subreddit).submit(title, selftext = new_submission_body)

						#Append the Submission object 
						submissions.append(new_submission)

						#Append the subreddit name (String object) to prevent duplicate X-post on same sub
						submitted_subs.append(subreddit)

					time.sleep(5)
				
				print("Submission X-posted!")

				#Notify the commentor after all the submissions have been successfully X-posted
				post_submit_notify(comment, submissions)

				#TODO: Message the OP that the post has been crossposted to different locations 

			#If the comment that contained mention of bot isn't the format requested:
			else:

				#Ignore comments made by the bot, especially from the funtion correct_format()
				if comment.author != reddit.user.me():
					print("Comment denied")

					#Reply to comment by explaining the correct format
					correct_format(comment)

			#Mark comment as read so the bot won't redo the process again
			comment.mark_read()

		#Pause before reading the next comment
		time.sleep(10)

'''
This method will check to see if the subreddit specified in the comment exists or not.
The default boolean value is True, since if subreddit exists nothing will happen, while
if it doesn't exist an exception will be thrown.
'''
def subreddit_exists(subreddit, reddit):
	exists = True

	#Search all subreddits to check if certain sub exists
	try:
		reddit.subreddits.search_by_name(subreddit, exact = True)
	#If an exception is thrown (e.g NotFound), subreddit doesn't exist
	except PrawcoreException:
		#Change boolean value to false
		exists = False

		print("Subreddit doesn't exist!")

	print("Subreddit exists!")

	return exists

'''
This method adds several things to indicate that this post is a crosspost: it includes
the origial poster of the submission, the link to the original post, as well as 
clarification that this is the work from the bot, along with the original text of the
post.
'''
def new_submission_text(old_submission):
	text = "(Author: /u/" + old_submission.author.name + ")\n"
	text += "(Link to original thread: " + old_submission.url + ")\n" 
	text += old_submission.selftext + "\n" + "This post has been reposted by X_Post_Bot"

	#TODO: Find a way to format the text: The newlines aren't showing in the crosspost
	#		Could possibly use Markdown for the text

	print("Submission text correctly formatted!")
	
	return text

'''
If the comment mentions the bot but doesn't format the comment properly, the bot will reply by
explaining the correct format. The file "correct_format.txt", which is in the same directory as
this file, contains the 
'''
def correct_format(comment):
	# Open and read the text from the file as the body for the comment reply
	with open("correct_format.txt", "r") as f:
		reply = f.read()

	comment.reply(reply)

	print("Correct format comment replied!")

'''
If the comment is correctly processed and submitted, the bot will notify (reply to) the commentor that
the post has been succesfully reposted by linking each of the crossposts.
'''
def post_submit_notify(comment, submissions):
	notify = "Hello, I am the X_Post_Bot, and your comment has been successfully X-posted to "

	# The format if the post was crossposted to one subreddit
	if(len(submissions) == 1):
		notify += "[here](" + submissions[0].url + ")!"
	
	# The format if post was crossposted to more than one subreddit
	else:
		for i in range(0, len(submissions)):
			# The format when noting the last subreddit in list.
			if i == len(submissions)-1:
				notify += "and [here](" + submissions[i].url + ")!"
			#Otherwise, repeat the following format
			else:
				notify += "[here](" + submissions[i].url +"), "

	# Reply to the original comment with above text
	comment.reply(notify)

	print("Post submit comment replied!")

#Login and create a new Reddit instance
reddit = login()

#Continuously run the bot 
while True:
	bot_submit(reddit)