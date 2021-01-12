"""
This is the ETL script for web scraping the NBA Stats website for the Chicago Bulls daily box scores.
"""

import json
import datetime as dt
import time
import sys
import requests
import psycopg2

# MAIN SCRIPT VARIABLES:
SEASON = "2020-2021"


def date_for_query(date_diff):
    """
    This is the function that constructs the URL for querying the function that NBA uses to get their data.
    :param date_diff: days you want to offset the query by
    :return: url to send the request to, the unix timestamp of it (used for creating key), date of the query.
    """
    date = dt.date.today() - dt.timedelta(date_diff)
    year_yesterday = date.year
    month_yesterday = date.month
    day_yesterday = date.day
    unix_time = int(time.mktime(date.timetuple()))
    request_url_nba_stats = f"https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom={month_yesterday}%2F{day_yesterday}%2F{year_yesterday}&DateTo={month_yesterday}%2F{day_yesterday}%2F{year_yesterday}&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=1610612741&TwoWay=0&VsConference=&VsDivision=&Weight="
    return request_url_nba_stats, unix_time, date


request_url, unix_timestamp, date_query = date_for_query(1)

headers = {'Accept': 'application/json, text/plain, */*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.9',
           'Connection': 'keep-alive',
           'Host': 'stats.nba.com',
           'Origin': 'https://www.nba.com',
           'Referer': 'https://www.nba.com/',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
           'x-nba-stats-origin': 'stats',
           'x-nba-stats-token': 'true'}
r = requests.get(request_url, headers=headers)
nba_stats_json = r.json()


# Data Check: Making sure there is data
def check_returned_data(json_data):
    """
    This function makes sure we received data for the date we passed into the query
    If we did not then it exits the script
    :param json_data:
    :return: system exit or do nothing
    """
    if len(json_data['resultSets'][0]['rowSet']) == 0:
        return sys.exit(f"No Game Data found for {date_query}")
    return None


check_returned_data(nba_stats_json)

headers = []
for item, value in nba_stats_json.items():
    if item == "resultSets":
        for data in value:
            header_set = data['headers']
            for header in header_set:
                headers.append(header)

full_stats_w_headers = {}
list_headers = []
list_data = []
for item, value in nba_stats_json.items():
    if item == "resultSets":
        for data in value:
            header_set = data['headers']
            stats_all = data['rowSet']
            for header in header_set:
                list_headers.append(header)
            for stat in stats_all:
                list_data.append(stat)

full_stats_w_headers = [dict(zip(list_headers, datapoint)) for datapoint in list_data]

# Have some columns we are not interested in:
columns_to_delete = ['GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
                     'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK',
                     'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK',
                     'OREB_RANK', 'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK',
                     'STL_RANK', 'BLK_RANK', 'BLKA_RANK', 'PF_RANK', 'PFD_RANK',
                     'PTS_RANK', 'PLUS_MINUS_RANK', 'NBA_FANTASY_PTS_RANK',
                     'DD2_RANK', 'TD3_RANK', 'CFID', 'CFPARAMS', 'W_PCT',
                     'FG_PCT', 'FG3_PCT', 'FT_PCT', 'DD2', 'TD3', 'NBA_FANTASY_PTS']
# Deleting these columns from this list
for column in columns_to_delete:
    for element in full_stats_w_headers:
        element.pop(column)

# Create a game id - can just use a UNIX timestamp

game_id = unix_timestamp
for element in full_stats_w_headers:
    element['GAME_ID'] = game_id

# Create a unique id for each player and game (combination of player_id and game_id)
for element in full_stats_w_headers:
    first_half = element['PLAYER_ID']
    second_half = element['GAME_ID']
    element['guid'] = str(first_half) + "-" + str(second_half)
    # add in the game date
    element['game_date'] = date_query
    # add in the season
    element['season'] = SEASON

# Sorting the Dictionary to prepare for insert into the database
sort_order = ['guid', 'GAME_ID', 'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID',
              'TEAM_ABBREVIATION', 'AGE', 'GP', 'W', 'L', 'MIN', 'FGM',
              'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB',
              'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD',
              'PTS', 'PLUS_MINUS', 'game_date', 'season']
ordered_full_stats = []
for element in full_stats_w_headers:
    reordered_dict_element = {k: element[k] for k in sort_order}
    ordered_full_stats.append(reordered_dict_element)

# Postgresql Connection
with open(r"/Users/GrantCulp/Desktop/Python/credentials_python_info.txt") as f:
    data = json.loads(f.read())
    post_host = data['aws']['rds_post']['host']
    post_port = data['aws']['rds_post']['port']
    post_user = data['aws']['rds_post']['user']
    post_password = data['aws']['rds_post']['password']
    post_database = data['aws']['rds_post']['database']

connection = psycopg2.connect(
    host=post_host,
    port=post_port,
    user=post_user,
    password=post_password,
    database=post_database,
)
cursor = connection.cursor()


# DATA CHECKS:
# Checking that the pulled game does not exist otherwise exist script
def check_new_game(list_games, new_stats):
    """
    Checking that the game pulled down from the website
    does not already exists in the database
    :param list_games: list of the games already in the database
    :param new_stats: list of the game pulled from the website
    :return: Either system exit or nothing
    """
    for data_point in new_stats:
        new_game_id = str(data_point['GAME_ID'])
    if new_game_id in list_games:
        return sys.exit("Game already in dataset")
    return None


# Getting a list of all the games we have:
list_games_dataset = []
cursor.execute("""
SELECT DISTINCT game_date, game_id
FROM bullsboxscore;""")
for item in cursor.fetchall():
    list_games_dataset.append(item[1])

check_new_game(list_games_dataset, full_stats_w_headers)


# Checking that the total mins is above or equal to 240
def check_full_game(full_stats):
    """
    Check to see that the Total Mins in the dataset is above 240
        All NBA games should have at least 240 mins played for a team
    :param full_stats: List of the pulled down stats
    :return: system exit or do nothing
    """
    total_mins_played = 0
    for row in full_stats:
        total_mins_played += row['MIN']
    if int(total_mins_played) < 239:
        return sys.exit("Not a full game played check the data")
    return None


check_full_game(full_stats_w_headers)

# If we have passed all our checks then insert in the data
# Inserting the data
cursor.executemany("""INSERT INTO bullsboxscore(custom_id,game_id,player_id,player_name,team_id,team_abbreviation,
age,gp,win,loss,mins,fgm,fga,fgthreem,fgthreea,ftm,fta,oreb,dreb,reb,ast,tov,stl,blk,blka,pf,pfdrawn,
pts,plusminus,game_date,season) 
VALUES (%(guid)s, %(GAME_ID)s, %(PLAYER_ID)s, %(PLAYER_NAME)s, %(TEAM_ID)s, %(TEAM_ABBREVIATION)s,
%(AGE)s, %(GP)s, %(W)s, %(L)s, %(MIN)s, %(FGM)s, %(FGA)s,%(FG3M)s, %(FG3A)s, %(FTM)s, %(FTA)s, %(OREB)s,
%(DREB)s, %(REB)s, %(AST)s,%(TOV)s, %(STL)s, %(BLK)s, %(BLKA)s, %(PF)s, %(PFD)s, %(PTS)s,
%(PLUS_MINUS)s, %(game_date)s, %(season)s)""", ordered_full_stats)

connection.commit()
connection.close()
