import praw
import random
import socket
import sys
import json
import datetime
import re
import os
from operator import itemgetter

user_agent_var = '<Your user_agent here>'
client_id_var = '<Your client_id here>'
client_secret_var = '<Your client_secret here>'

reddit = praw.Reddit(user_agent=user_agent_var, client_id=client_id_var, client_secret=client_secret_var)


#get the timestamp here: https://www.unixtimestamp.com/
#Sep. 1st, 2017: 1504224000
#Oct. 1st, 2017: 1506816000
#Oct. 8th, 2017: 1507420800
start_utc = 1504224000
end_utc = 1506816000
data_dir = 'utc timespan - ' + str(start_utc) + '-' + str(end_utc) +'/'

subreddit_list = ['AskComputerScience','amazonecho','Android','androiddev','apple','CSEducation','CS_Questions','C_Programming','CodingContests','Compilers','CompressiveSensing','Cplusplus','Database','devops','IPython','Julia','LanguageTechnology','php','ProgrammerHumor','ProgrammingLanguages','Python','algorithms','artificial','aws','bigdata','codeprojects','codes','coding','commandline','compsci','computervision','cpp','crypto','csbooks','cscareerquestions','datamining','datascience','datasets','django','flask','functional','functionallang','gadgets','git','golang','google','hacking','hadoop','hardware','haskell','howtohack','internetisbeautiful','iOSProgramming','ios','java','javascript','learnprogramming','learnpython','linux','lisp','machinelearning','netsec','networking','nosql','opendata','opensource','programming','pystats','readablecode','robotics','scheme','semanticweb','simpleios','software','softwaredevelopment','statistics','systems','sysadmin','tech','technology','tinycode','Ubuntu','vim','visualization','webdev']


cumulative_data = {'domain_occurrences':{},'num_text_posts':0,'subbredit_submission_total':[],'subreddit_list':[]}



def combine_domain_occurrence(domaindict):
	for key in domaindict:
		if key in cumulative_data['domain_occurrences']:
			cumulative_data['domain_occurrences'][key] += domaindict[key]
		else:
			cumulative_data['domain_occurrences'][key] = domaindict[key]
	return


def combine_general_stats(datadict):
	cumulative_data['subbredit_submission_total'].append({datadict['display_name']:datadict['total_submissions']})

def compile_word_occurrence(wordcountdict, words, title):
	#version 1: add all words
	"""
	for split_str in words:
		extracted_word = re.sub('[^A-Za-z0-9]+', '', split_str).lower().replace(" ", "+")
		if extracted_word in wordcountdict:
			wordcountdict[extracted_word] += 1
		elif extracted_word == "" or extracted_word.isdigit():
			continue
		else:
			wordcountdict[extracted_word] = 1
	
	"""
	#version 2: look for key terms in title
	
	programming_langues = [' c ', ' r ','.net','c++','c#','css','flask','golang','html','haskell','java','javascript','julia','lisp','nosql','objective-c','perl','php','prolog','python','ruby','rdf','scala','sparql','swift','sql','tex']
	programs = ['apache','atom','aws','docker','emacs','gcc','github','gitlab','graphdb','gnu','hadoop','matlab','mongodb','neo4j','sublime','vim']
	operating_systems = ['ios','windows','linux']
	technologies = ['alexa','android','gps','hdmi','iphone','mp3','mp4','shell','siri','watson']
	concepts = ['big data','dbpedia','data science','data mining','deep learning','machine learning','software engineer']
	companies = ['adobe','airbnb','alphabet','amazon','apple','cisco','comcast','dell','disney','facebook','google','ibm','intel','linkedin','lyft','microsoft','mozilla','netflix','oracle','qualcomm','salesforce','tesla','time warner','twitter','uber','vmware']

	important_words = programming_langues + programs + technologies + concepts + companies + operating_systems

	#title_clean = re.sub('[^A-Za-z0-9]+', '', title).lower()
	title_clean = title.lower()
	#print(title_clean)
	for word_var in important_words:
		if word_var in title_clean:
			if word_var in wordcountdict:
				wordcountdict[word_var] += 1
			else:
				wordcountdict[word_var] = 1
	
	#IMPORVEMENTS: one version that splits up the string, 
	#		one that looks for individual strings(smaller items like c and java)

	#sorted(wordcountdict, key=wordcountdict.get)
	return wordcountdict


def retrieve_subreddit_submissions(cur_subreddit):
		
	datadict, domaindict, title_wordcountdict = {}, {}, {}
	total_submissions, avg_score_var, avg_comment_var, self_reddit_var = 0, 0, 0, 0


	#get subreddit information example link: https://www.reddit.com/r/technology/about.json
	datadict['audience_target'] = reddit.subreddit(cur_subreddit).audience_target
	datadict['advertiser_category'] = reddit.subreddit(cur_subreddit).advertiser_category
	datadict['active_user_count'] = reddit.subreddit(cur_subreddit).active_user_count #accounts_active
	datadict['description'] = reddit.subreddit(cur_subreddit).description
	datadict['display_name'] = reddit.subreddit(cur_subreddit).display_name
	datadict['id'] = reddit.subreddit(cur_subreddit).id
	datadict['public_description'] = reddit.subreddit(cur_subreddit).public_description
	datadict['subreddit_creation_utc'] = reddit.subreddit(cur_subreddit).created
	datadict['subscribers'] = reddit.subreddit(cur_subreddit).subscribers
	datadict['title'] = reddit.subreddit(cur_subreddit).title
	
	datadict['collection_range_start_utc'] = datetime.datetime.utcfromtimestamp(int(start_utc)).strftime('%Y-%m-%d %H:%M:%S')
	datadict['collection_range_end_utc'] = datetime.datetime.utcfromtimestamp(int(end_utc)).strftime('%Y-%m-%d %H:%M:%S')
	datadict['collection_range_start_unix_timestamp'] = start_utc
	datadict['collection_range_end_unix_timestamp'] = end_utc

	#Source for strftime values: http://pubs.opengroup.org/onlinepubs/009695399/functions/strftime.html
	#https://www.cl.cam.ac.uk/~mgk25/iso-time.html
	datadict['utc_of_data_collection_start'] = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

	
	datadict['submissions'] = []

	counter = 1

	for submission in reddit.subreddit(cur_subreddit).submissions(start_utc, end_utc):

		#Minor fixes for praw formatting issues
		author_tmp = str(submission.author)
		subreddit_tmp = str(submission.subreddit)
		title_tmp = submission.title.replace(u"\u2013", "-").replace(u"\u2018", "'").replace(u"\u2019", "'")

		print(str(counter) + ": - " + title_tmp)
		counter += 1


		#ex data: https://www.reddit.com/r/technology/new.json?sort=new
		results = {"title":title_tmp, "score":submission.score, "domain":submission.domain, "id":submission.id, "link_flair_text":submission.link_flair_text, "num_comments":submission.num_comments, "created_utc":submission.created_utc, "permalink":submission.permalink, "author":author_tmp, "subreddit":subreddit_tmp, "url":submission.url, "link_flair_css_class":submission.link_flair_css_class, "selftext":submission.selftext, "is_self":submission.is_self, "media":submission.media, "is_reddit_media_domain":submission.is_reddit_media_domain, "num_crossposts":submission.num_crossposts,"is_video":submission.is_video}
		

		#Increment Variables for Statistics
		total_submissions += 1
		avg_score_var += submission.score
		avg_comment_var += submission.num_comments
		if submission.is_self == True: self_reddit_var += 1
		if submission.domain in domaindict: domaindict[submission.domain] += 1
		else: domaindict[submission.domain] = 1

		title_wordcountdict = compile_word_occurrence(title_wordcountdict, title_tmp.split(), title_tmp)
		

		datadict['submissions'].append(results)

	datadict['top_score_submissions'] = sorted(datadict['submissions'], key=itemgetter('score'), reverse=True)[:5]
		


	datadict['domain_occurrences'] = domaindict
	datadict['title_word_count_occurrences'] = title_wordcountdict
	datadict['total_submissions'] = total_submissions
	datadict['num_text_posts'] = self_reddit_var
	datadict['num_external_website_posts'] = total_submissions - self_reddit_var
	if total_submissions > 0:
		datadict['avg_submission_score'] = avg_score_var/total_submissions
		datadict['avg_comment_num_per_submission'] = avg_comment_var/total_submissions
	else:
		datadict['avg_submission_score'] = total_submissions
		datadict['avg_comment_num_per_submission'] = total_submissions

	#combine data for overall statistics
	combine_domain_occurrence(domaindict)
	combine_general_stats(datadict)

	#wrtie the completion time of data collection
	datadict['utc_of_data_collection_completion'] = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

	#write data to file
	with open(data_dir + 'subreddit_data - ' + cur_subreddit + '.json', 'w+') as outfile:
		json.dump(dict(datadict), outfile, indent=4, sort_keys=True)

	
	return




def submit_cumulative_data():
	#num of submissions, domains, important words
	cumulative_data['utc_of_data_collection_completion'] = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

	with open(data_dir + 'cumulative_data.json', 'w+') as outfile:
		json.dump(dict(cumulative_data), outfile, indent=4, sort_keys=True)




if __name__ == "__main__":

	if os.path.isdir(data_dir) == False:
		os.mkdir(data_dir)

	cumulative_data['utc_of_data_collection_start'] = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

	for cur_subreddit in subreddit_list:
		print(cur_subreddit)
		retrieve_subreddit_submissions(cur_subreddit)

	cumulative_data['subreddit_list'] = subreddit_list
	submit_cumulative_data()