# Bulls Daily Stats Twitter

This a repository for the code used to run the [Bulls Daily Stats Account]('https://twitter.com/stats_bulls).
The python code is used with an AWS RDS PostgreSQL to hold all the daily stats for the Chicago Bulls Boxscores.
This program includes an ETL (Extract, Transform, Load) from the NBA Stats website into an AWS PostgreSQL database.
From that point the program then tweets out a daily Stats Summary of the leaders from the game the night before.

## ETL
The code for this ETL project can be found in [bulls_boxscore_etl.py](wwe.google.com). The script checks the [NBA Stats website]('https://www.nba.com/stats/players/traditional/?sort=PTS&dir=-1')
to see if the Chicago Bulls played a game the day before and then if they did it pulls in the data.
I have created a table in my AWS RDS PostgreSQL database to hold the daily information.
This code has the ability to be triggered daily and will check to see if it should insert in the game data so it does not create duplicates.

**Extract**:
- This is the web scrapping portion of this project to gather the daily boxscores (stats)
for the Chicago Bulls.
- I was able to use some basic web scrapping skills to send a request to the NBA Stats website and get a result that I then could parse and create a list of dictionaries.

**Transform**:
- I utilized a lot of data checks within the script to make sure I am loading in full complete data and not replicating any data.
- There was a lot of extra data being returned I had to delete out
- I needed to create a couple new columns for the table to be effective.

**Load**:
- The database I decided to use for this project was an AWS RDS PostgreSQL database because of the low cost.
- I used python to load the data into the PostgreSQL table.

## Tweet
The tweets are created using a mix of SQL and Python. The stats are created by using SQL Functions to get the data and create a clean
python code when calling them.
I had to create 30+ SQL functions as I had to create 2-3 for each stat category. Each stat has a daily leader, season overall for the whole team,
and a weekly one for all the games played in the last 7 days.

I also created an Index on game_date as I used that to filter on most of the functions to speed up the results.

The python portion of this is to create the daily tweets and tweet them out.

## Current Improvements (Working on):
1/2020:
- Creating the weekly tweet
- Creating a newsletter
- Continue on cleaning up code

## Suggestions:
- Feel free to tweet at the account with any suggestions!