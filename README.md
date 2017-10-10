# RedditDataCollection
Collection of reddit submissions from various computer science subreddits to find trends in the computer science domain

## File Directory Structure
Contains python file data collection, general metadata file, and sample generated datasets

## Run Instructions
1. Install the following programs/plugins
  * Any text editor
  * A bash interface
  * Install git (sudo apt-get install git)
  * The latest version of python: https://www.python.org/ (pip install python 2.7)
  * PRAW: https://praw.readthedocs.io (pip install praw)
2. Clone this repository (git clone https://github.com/IanGross/RedditDataCollection/)
3. Create a reddit account and setup and Script App with OAuth2
  * Instructions here: https://github.com/reddit/reddit/wiki/OAuth2
4. Copy the values for user_agent, client_id and client_secret of your application
5. Open the Reddit_Data_Collection.py file and insert the values in the appropriate fields of "reddit = praw.Reddit()" (located right after import statements.
6. *Optional*
  * Go to the website: https://www.unixtimestamp.com/ and get a utc start and end value. Insert those values under start_utc and end_utc
  * Add and/or remove subreddit names in the subreddit_list list
7. Run the file with: python Reddit_Data_Collection.py
