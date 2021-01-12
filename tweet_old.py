# I will need to write out a series of tweets that will be tweeted daily
# Plan of attack write out 7 different tweets one for each day of the week.
# I think writting out different tweets will keep it fresh each day.
# I could also a thread (reply to the first tweet)
# Going to create a function for each day for the tweet
# Metircs: Assist/Turnover ratio, True Shooting Percentage, 3 Point Attempt Rate, Free Throw Attempt Rate, Points per minute or Points Per Possions,
# Offensive Rating: https://www.basketball-reference.com/about/ratings.html?
# Free throw percentage
# Days:
#       Sunday Scaries - Turnovers - Assist/Turnover Ratio, Turnovers per 36 mins, Total Turnovers, Turnover%(https://www.basketball-reference.com/about/glossary.html)
#       Also Sunday week in review
#       Michael - Monday - Scoring - True Shooting Percentage, PPG, Points per 36 mins
#       Thibs - Tuesday - Defense - Steal Percentage, Block PErcentage, Defensive Reb
#       Winning - Wednesday - Winning Stats - Usage Rate (https://www.nbastuffer.com/analytics101/usage-rate/), Mins Played
#               - Thursday - Overall - PER, eFG, TShooting Percentage, Assist/Turnover Ratio, Assist Percentage, Total Reb Percentage
#              - Friday - Overall
#       Shootting - Saturday - True Shotting Percentage,eFG( effecetive field goal percentage) ,FT %, 3pt%, 3 pt attempt rate: 3PAr = (3PA / FGA), freethrow attempt rate

import json
import psycopg2
import tweepy
import datetime as dt
import sys

#Need to get current date and weekday to specify which tweet to send
#Mon = 0 - Sun = 6
cur_weekday_num =dt.datetime.today().weekday()

#Twitter Credentials
with open(r"/Users/GrantCulp/Desktop/Python/credentials_python_info.txt") as f:
    data = json.loads(f.read())
    CONSUMER_KEY = data['twitter']['bulls_account']['cons_key']
    CONSUMER_SECRET = data['twitter']['bulls_account']['cons_secret']
    ACCESS_TOKEN = data['twitter']['bulls_account']['access_token']
    ACCESS_TOKEN_SECRET = data['twitter']['bulls_account']['access_token_secret']


twitter_auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
twitter_auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(twitter_auth)


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

#Need to make sure there was a game played yesterday or it is a sunday
yesterday_date = dt.date.today()-dt.timedelta(days=1)
cursor.execute("SELECT MAX(game_date) FROM bullsboxscore")
bulls_last_game = cursor.fetchone()[0]
if yesterday_date != bulls_last_game and cur_weekday_num != 6:
    sys.exit("No Game was added to the database this morning and not a Sunday")
else:
    pass

# Win Loss Query
def daily_win_loss_query():
    cursor.callproc('public.func_win_loss_last_game')
    if cursor.fetchall()[0][0] > 0:
        return "Win", '\U0001F525'
    else:
        return "Loss", '\U0001F44E'

win_loss_result, win_loss_emoji = daily_win_loss_query()
##STILL NEED TO DO THIS
#Record last seven days
def record_last_seven_days():
    cursor.execute("""SET TIMEZONE = 'America/Chicago'""")
    cursor.callproc('public.func_record_last_seven_days')
    gp, wins, loss = cursor.fetchall()[0]
    if wins > loss:
        emoji = '\U0001F525'
    else:
        emoji = '\U0001F44E'
    return gp, wins, loss, emoji

gp_last_seven_days, win_last_seven_days, loss_last_seven_days, emoji_last_seven_days = record_last_seven_days()
#Todays date and 7 Days Ago Date:
cursor.execute("""SET TIMEZONE = 'America/Chicago'""")
cursor.execute("""SELECT DATE(current_date - INTERVAL '7 days') AS seven_days_ago, current_date""")
date_seven_days_ago,date_today = cursor.fetchall()[0]

#Total Record Query, Emoji
def total_record_query():
    cursor.callproc('public.func_total_record')
    total_wins = 0
    total_losses = 0
    for item in cursor.fetchall():
        total_wins+= item[2]
        total_losses += item[3]
    if total_losses> total_wins:
        emoji = '\U0001F92E'
    else:
        emoji = '\U0001F601'
    return total_wins, total_losses, emoji

bulls_overall_record = total_record_query()

# Top Point Scorer Daily:
def daily_top_pts_scorer_query():
    cursor.callproc('public.func_pts_daily')
    player_id = cursor.fetchall()[0][2]
    cursor.callproc('public.func_pts_daily')
    player_name = cursor.fetchall()[0][3]
    cursor.callproc('public.func_pts_daily')
    pts_scored = cursor.fetchall()[0][4]
    return player_id, player_name, pts_scored


top_pts_score_player_id, top_pts_score_name, top_pts_scored = daily_top_pts_scorer_query()
top_pts_score_last_name = top_pts_score_name.split()[1]

# Create Dictionary of PPG:
def ppg_query():
    ppg_dictionary = {}
    cursor.callproc('public.func_ptspg_season', ['2020-2021'])
    for item in cursor.fetchall():
        ppg_dictionary[item[0]] = item[3]
    return ppg_dictionary
ppg_dictionary = ppg_query()

# Daily Ppg Emoji:
def daily_ppg_emoji_query(daily_player_id,daily_ppts, ppg_dictionary):
    overall_ppg_daily_leader = ppg_dictionary[daily_player_id]
    if daily_ppts>= overall_ppg_daily_leader:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_ppg_emoji = daily_ppg_emoji_query(top_pts_score_player_id,top_pts_scored,ppg_dictionary)


# Top Assist Leader Daily:
def daily_top_ast_query():
    cursor.callproc('public.func_ast_rank_last_game')
    player_id = cursor.fetchall()[0][2]
    cursor.callproc('public.func_ast_rank_last_game')
    player_name = cursor.fetchall()[0][3]
    cursor.callproc('public.func_ast_rank_last_game')
    ast_recorded = cursor.fetchall()[0][4]
    return player_id, player_name, ast_recorded

daily_top_ast_id, daily_top_ast_name, daily_top_ast_recorded = daily_top_ast_query()
daily_top_ast_last_name = daily_top_ast_name.split()[1]

#Create assist Dictionary pg:
def astpg_dictionary_query():
    ast_dictionary = {}
    cursor.callproc('public.func_astpg_player')
    for item in cursor.fetchall():
        ast_dictionary[item[0]] = float(item[4])
    return ast_dictionary

astpg_dictionary = astpg_dictionary_query()


#Daily Ast Emoji
def daily_ast_emoji_query(daily_leader_id, daily_ast_amount, ast_dictionary):
    overall_astpg_leader = ast_dictionary[daily_leader_id]
    if daily_ast_amount > overall_astpg_leader:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_ast_emoji = daily_ast_emoji_query(daily_top_ast_id,daily_top_ast_recorded,astpg_dictionary)


# Top Rebound Leader Daily
def daily_top_reb_query():
    cursor.callproc('public.func_reb_rank_last_game')
    top_reb_player_id = cursor.fetchone()[2]
    cursor.callproc('public.func_reb_rank_last_game')
    top_reb_name = cursor.fetchone()[3]
    cursor.callproc('public.func_reb_rank_last_game')
    top_reb_recorded = cursor.fetchone()[4]
    return top_reb_player_id,top_reb_name, top_reb_recorded

top_reb_player_id,top_reb_name, top_reb_recorded = daily_top_reb_query()
top_reb_last_name = top_reb_name.split()[1]

#Dictionary of Rebound
def rebound_dict_query():
    rebpg_dict = {}
    cursor.callproc('public.func_rebpg_player')
    for item in cursor.fetchall():
        rebpg_dict[item[0]] = float(item[4])
    return rebpg_dict
rebpg_dict_all = rebound_dict_query()

#Daily Rebound Total Emoji
def daily_rebpg_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_rebpg = total_dict[daily_player_id]
    if daily_stat >= overall_rebpg:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji
daily_total_reb_emoji = daily_rebpg_emoji_query(top_reb_player_id,top_reb_recorded,rebpg_dict_all )

# Top eFG Leader Daily
def daily_top_efg_query():
    cursor.callproc('public.func_efg_rank_last_game')
    top_efg_id = cursor.fetchone()[3]
    cursor.callproc('public.func_efg_rank_last_game')
    top_efg_name = cursor.fetchone()[4]
    cursor.callproc('public.func_efg_rank_last_game')
    top_efg_recorded = cursor.fetchone()[5]
    return top_efg_id,top_efg_name, top_efg_recorded

daily_efg_id,daily_efg_name, daily_efg_recorded = daily_top_efg_query()
daily_efg_last_name = daily_efg_name.split()[1]

#Dictionary Top Effective Field Goal:
def efg_dictionary_query():
    efg_dict = {}
    cursor.callproc('public.func_efg_player')
    for item in cursor.fetchall():
        efg_dict[item[0]] = float(item[5])
    return efg_dict
efg_dict_all = efg_dictionary_query()

#Daily Emoji Top Effective Field Goal:
def daily_efg_emoji_query(daily_player_id, daily_stat, efg_dictionary):
    overall_efg = efg_dictionary[daily_player_id]
    if daily_stat >= overall_efg:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji
daily_efg_emoji = daily_efg_emoji_query(daily_efg_id,daily_efg_recorded,efg_dict_all)


# Top True Shooting Leader Daily
def daily_top_trsp_query():
    cursor.callproc('public.func_trsp_rank_last_game')
    top_trsp_id = cursor.fetchone()[2]
    cursor.callproc('public.func_trsp_rank_last_game')
    top_trsp_name = cursor.fetchone()[3]
    cursor.callproc('public.func_trsp_rank_last_game')
    top_trsp_recorded = cursor.fetchone()[6]
    return top_trsp_id, top_trsp_name, top_trsp_recorded

daily_trsp_id, daily_trsp_name, daily_trsp_recorded = daily_top_trsp_query()
daily_trsp_last_name = daily_trsp_name.split()[1]

#Dictionary True Shooting Leader
def trsp_dictionary_query():
    trsp_dict = {}
    cursor.callproc('public.func_ts_per_player')
    for item in cursor.fetchall():
        trsp_dict[item[0]] = float(item[5])
    return trsp_dict

trsp_dict_all = trsp_dictionary_query()

#Daily Emoji True Shooting Percentage
def daily_trsp_emoji_query(daily_player_id, daily_stat, trsp_dictionary):
    overall_trsp = trsp_dictionary[daily_player_id]
    if daily_stat >= overall_trsp:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_trsp_emoji = daily_trsp_emoji_query(daily_trsp_id,daily_trsp_recorded,trsp_dict_all)

#Daily Top Ast/Tov Ratio Query:
def daily_ast_tov_query():
    cursor.callproc('public.func_ast_tov_ratio_daily')
    top_ast_tov_ratio_id = cursor.fetchone()[2]
    cursor.callproc('public.func_ast_tov_ratio_daily')
    top_ast_tov_ratio_name = cursor.fetchone()[3]
    cursor.callproc('public.func_ast_tov_ratio_daily')
    top_ast_tov_ratio_num= float(cursor.fetchone()[6])
    return top_ast_tov_ratio_id, top_ast_tov_ratio_name, top_ast_tov_ratio_num

daily_top_ast_tov_id, daily_top_ast_tov_name, daily_top_ast_tov_num = daily_ast_tov_query()
daily_top_ast_tov_last_name = daily_top_ast_tov_name.split()[1]

#Dicitonary of total Ast/Tov Ratio:
def ast_tov_dictionary_query():
    ast_tov_dictionary = {}
    cursor.callproc('public.func_ast_tov_ratio_all')
    for item in cursor.fetchall():
        ast_tov_dictionary[item[0]] = float(item[4])
    return ast_tov_dictionary

ast_tov_dict_all = ast_tov_dictionary_query()

#Daily Ast/Tov Emoji Query:
def daily_ast_tov_emoji_query(daily_player_id, daily_stat, ast_tov_dictionary):
    overall_ast_tov = ast_tov_dictionary[daily_player_id]
    if daily_stat >= overall_ast_tov:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_ast_tov_emoji = daily_ast_tov_emoji_query(daily_top_ast_tov_id, daily_top_ast_tov_num, ast_tov_dict_all)

#Daily Usage Rate Query:
def daily_usage_rate_query():
    cursor.callproc('public.func_usage_rate_daily')
    daily_usage_rate_id = cursor.fetchone()[1]
    cursor.callproc('public.func_usage_rate_daily')
    daily_usage_rate_name = cursor.fetchone()[2]
    cursor.callproc('public.func_usage_rate_daily')
    daily_usage_rate_stat = cursor.fetchone()[3]
    return daily_usage_rate_id,daily_usage_rate_name,daily_usage_rate_stat

daily_usage_rate_id, daily_usage_rate_name, daily_usage_rate_stat = daily_usage_rate_query()
daily_usage_rate_last_name = daily_usage_rate_name.split()[1]

#Dictionary Usage Rate Query:
def usage_rate_dict_query():
    usage_rate_dict = {}
    cursor.callproc('public.func_usage_rate_all')
    for item in cursor.fetchall():
        usage_rate_dict[item[0]] = float(item[10])
    return usage_rate_dict
usage_rate_dict_all = usage_rate_dict_query()

#Daily Usage Rate Emoji Query:
def daily_usage_rate_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_usage_rate = total_dict[daily_player_id]
    if daily_stat >= overall_usage_rate:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_usage_rate_emoji = daily_usage_rate_emoji_query(daily_usage_rate_id, daily_usage_rate_stat, usage_rate_dict_all)

#Daily Three Point Attempt Rate Query:
def daily_threepar_query():
    cursor.callproc('public.func_threepar_daily')
    daily_threepar_id = cursor.fetchone()[2]
    cursor.callproc('public.func_threepar_daily')
    daily_threepar_name = cursor.fetchone()[3]
    cursor.callproc('public.func_threepar_daily')
    daily_threepar_stat = cursor.fetchone()[6]
    return daily_threepar_id,daily_threepar_name,daily_threepar_stat

daily_threepar_id, daily_threepar_name, daily_threepar_stat = daily_threepar_query()
daily_threepar_last_name = daily_threepar_name.split()[1]

#Dictionary Three Point Attempt Rate:
def threepar_dictionary_query():
    threepar_dict = {}
    cursor.callproc('public.func_threepar_all')
    for item in cursor.fetchall():
        threepar_dict[item[0]] = float(item[4])
    return threepar_dict

threepar_dict_all = threepar_dictionary_query()

#Daily Three Point Attempt Rate Emoji Query:
def daily_threepar_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_threepar = total_dict[daily_player_id]
    if daily_stat >= overall_threepar:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_threepar_emoji = daily_threepar_emoji_query(daily_threepar_id, daily_threepar_stat, threepar_dict_all)

#Daily Mins Query:
def daily_mins_query():
    cursor.callproc('public.func_mins_daily')
    daily_mins_id = cursor.fetchone()[3]
    cursor.callproc('public.func_mins_daily')
    daily_mins_name = cursor.fetchone()[4]
    cursor.callproc('public.func_mins_daily')
    daily_mins_stat = cursor.fetchone()[5]
    return daily_mins_id,daily_mins_name,daily_mins_stat

daily_mins_id, daily_mins_name, daily_mins_stat = daily_mins_query()
daily_mins_last_name = daily_mins_name.split()[1]

#Dictionary Mins:
def mins_dictionary_query():
    mins_dict = {}
    cursor.callproc('public.func_mins_all')
    for item in cursor.fetchall():
        mins_dict[item[0]] = float(item[4])
    return mins_dict

mins_dict_all = mins_dictionary_query()

#Daily Mins Emoji Query:
def daily_mins_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_mins = total_dict[daily_player_id]
    if daily_stat >= overall_mins:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji

daily_mins_emoji = daily_mins_emoji_query(daily_mins_id, daily_mins_stat, mins_dict_all)

#Daily Assist Percentage Query:
def daily_ast_percent_query():
    cursor.callproc('public.func_ast_percent_daily')
    daily_ast_percent_id = cursor.fetchone()[3]
    cursor.callproc('public.func_ast_percent_daily')
    daily_ast_percent_name = cursor.fetchone()[4]
    cursor.callproc('public.func_ast_percent_daily')
    daily_ast_percent_stat = float(cursor.fetchone()[10])
    return daily_ast_percent_id,daily_ast_percent_name,daily_ast_percent_stat
daily_ast_percent_id,daily_ast_percent_name,daily_ast_percent_stat = daily_ast_percent_query()
daily_ast_percent_last_name = daily_ast_percent_name.split()[1]

#Dictionary Ast Percentage Query
def ast_percent_dictionary_query():
    ast_percent_dict = {}
    cursor.callproc('public.func_ast_percent_season')
    for item in cursor.fetchall():
        ast_percent_dict[item[0]] = float(item[9])
    return ast_percent_dict

ast_perc_dict_all = ast_percent_dictionary_query()

#Daily Assist Percentage Emoji Query:
def daily_ast_percent_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ast_percent = total_dict[daily_player_id]
    if daily_stat >= overall_ast_percent:
        emoji = "\U0001F4C8"
    else:
        emoji = "\U0001F4C9"
    return emoji
daily_ast_percent_emoji = daily_ast_percent_emoji_query(daily_ast_percent_id,daily_ast_percent_stat,ast_perc_dict_all)

#Daily TOV Percent Query:
def daily_tov_percent_query():
    cursor.callproc('public.func_tov_percent_daily')
    daily_tov_percent_id = cursor.fetchone()[3]
    cursor.callproc('public.func_tov_percent_daily')
    daily_tov_percent_name = cursor.fetchone()[4]
    cursor.callproc('public.func_tov_percent_daily')
    daily_tov_percent_stat = float(cursor.fetchone()[8])
    return daily_tov_percent_id,daily_tov_percent_name,daily_tov_percent_stat
daily_tov_percent_id,daily_tov_percent_name,daily_tov_percent_stat = daily_tov_percent_query()
daily_tov_percent_last_name = daily_tov_percent_name.split()[1]

#Dictionary TOV Percentage Query
def tov_percent_dictionary_query():
    tov_percent_dict = {}
    cursor.callproc('public.func_tov_percent_all')
    for item in cursor.fetchall():
        tov_percent_dict[item[0]] = float(item[6])
    return tov_percent_dict

tov_perc_dict_all = tov_percent_dictionary_query()

#Daily Tov Percentage Emoji Query:
def daily_tov_percent_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_tov_percent = total_dict[daily_player_id]
    if daily_stat >= overall_tov_percent:
        emoji = "\U0001F4C9"
    else:
        emoji = "\U0001F4C8"
    return emoji
daily_tov_percent_emoji = daily_tov_percent_emoji_query(daily_tov_percent_id,daily_tov_percent_stat,tov_perc_dict_all)

#Weekly Points Per Game Query:
def weekly_ptsg_query():
    cursor.callproc('public.func_pts_game_last_seven_days')
    weekly_ptsg_id = cursor.fetchone()[0]
    cursor.callproc('public.func_pts_game_last_seven_days')
    weekly_ptsg_name = cursor.fetchone()[1]
    cursor.callproc('public.func_pts_game_last_seven_days')
    weekly_ptsg_stat = float(cursor.fetchone()[3])
    return weekly_ptsg_id,weekly_ptsg_name,weekly_ptsg_stat
#weekly_ptsg_id, weekly_ptsg_name, weekly_ptsg_stat = weekly_ptsg_query()
#weekly_ptsg_last_name = weekly_ptsg_name.split()[1]

#Weekly Points Per Game Emoji Query:
def weekly_ptsg_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ptsg = total_dict[daily_player_id]
    if daily_stat >= overall_ptsg:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_ptsg_emoji = weekly_ptsg_emoji_query(weekly_ptsg_id,weekly_ptsg_stat,ppg_dictionary)

#Weekly Points Per 36 Mins Query:
def weekly_pts_per_full_game_query():
    cursor.callproc('public.func_pts_per_full_game_last_seven_days')
    weekly_pts_per_full_game_id = cursor.fetchone()[0]
    cursor.callproc('public.func_pts_per_full_game_last_seven_days')
    weekly_pts_per_full_game_name = cursor.fetchone()[1]
    cursor.callproc('public.func_pts_per_full_game_last_seven_days')
    weekly_pts_per_full_game_stat = float(cursor.fetchone()[5])
    return weekly_pts_per_full_game_id,weekly_pts_per_full_game_name,weekly_pts_per_full_game_stat

#weekly_pts_per_full_game_id, weekly_pts_per_full_game_name, weekly_pts_per_full_game_stat = weekly_pts_per_full_game_query()
#weekly_pts_per_full_game_last_name = weekly_pts_per_full_game_name.split()[1]

#All Points Per 36 Mins Query:
def all_pts_per_full_game_query():
    pts_per_full_game_dict = {}
    cursor.callproc('public.func_pts_per_full_game_all')
    for item in cursor.fetchall():
        pts_per_full_game_dict[item[0]] = float(item[5])
    return pts_per_full_game_dict

#all_pts_per_full_game_dict = all_pts_per_full_game_query()

#Weekly Points Per 36 Mins Emoji Query:
def weekly_pts_per_full_game_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ptsg = total_dict[daily_player_id]
    if daily_stat >= overall_ptsg:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_pts_per_full_game_emoji = weekly_pts_per_full_game_emoji_query(weekly_pts_per_full_game_id,weekly_pts_per_full_game_stat,all_pts_per_full_game_dict)

#Weekly Rebounds Per Game Last 7 Days Query:
def weekly_reb_per_game_query():
    cursor.callproc('public.func_reb_per_game_last_seven_days')
    weekly_reb_per_game_id = cursor.fetchone()[0]
    cursor.callproc('public.func_reb_per_game_last_seven_days')
    weekly_reb_per_game_name = cursor.fetchone()[1]
    cursor.callproc('public.func_reb_per_game_last_seven_days')
    weekly_reb_per_game_stat = float(cursor.fetchone()[4])
    return weekly_reb_per_game_id,weekly_reb_per_game_name,weekly_reb_per_game_stat

#weekly_reb_per_game_id, weekly_reb_per_game_name, weekly_reb_per_game_stat = weekly_reb_per_game_query()
#weekly_reb_per_game_last_name = weekly_reb_per_game_name.split()[1]

#Weekly Rebounds Per Game Emoji Query:
def weekly_reb_per_game_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_reb_per_game= total_dict[daily_player_id]
    if daily_stat >= overall_reb_per_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_reb_per_game_emoji = weekly_reb_per_game_emoji_query(weekly_reb_per_game_id,weekly_reb_per_game_stat,rebpg_dict_all)

#Weekly Assist Per Game Last 7 Days Query:
def weekly_ast_per_game_query():
    cursor.callproc('public.func_astpg_last_seven_days')
    weekly_ast_per_game_id = cursor.fetchone()[0]
    cursor.callproc('public.func_astpg_last_seven_days')
    weekly_ast_per_game_name = cursor.fetchone()[1]
    cursor.callproc('public.func_astpg_last_seven_days')
    weekly_ast_per_game_stat = float(cursor.fetchone()[4])
    return weekly_ast_per_game_id,weekly_ast_per_game_name,weekly_ast_per_game_stat

#weekly_ast_per_game_id, weekly_ast_per_game_name, weekly_ast_per_game_stat = weekly_ast_per_game_query()
#weekly_ast_per_game_last_name = weekly_ast_per_game_name.split()[1]

#Weekly Ast Per Game Emoji Query:
def weekly_ast_per_game_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ast_per_game= total_dict[daily_player_id]
    if daily_stat >= overall_ast_per_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_ast_per_game_emoji = weekly_ast_per_game_emoji_query(weekly_ast_per_game_id,weekly_ast_per_game_stat,astpg_dictionary)

#Weekly Mins Per Game Last 7 Days Query:
def weekly_mins_per_game_query():
    cursor.callproc('public.func_mins_last_seven_days')
    weekly_mins_per_game_id = cursor.fetchone()[0]
    cursor.callproc('public.func_mins_last_seven_days')
    weekly_mins_per_game_name = cursor.fetchone()[1]
    cursor.callproc('public.func_mins_last_seven_days')
    weekly_mins_per_game_stat = float(cursor.fetchone()[4])
    return weekly_mins_per_game_id,weekly_mins_per_game_name,weekly_mins_per_game_stat

#weekly_mins_per_game_id, weekly_mins_per_game_name, weekly_mins_per_game_stat = weekly_mins_per_game_query()
#weekly_mins_per_game_last_name = weekly_mins_per_game_name.split()[1]

#Weekly Mins Per Game Emoji Query:
def weekly_mins_per_game_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_mins_per_game= total_dict[daily_player_id]
    if daily_stat >= overall_mins_per_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_mins_per_game_emoji = weekly_mins_per_game_emoji_query(weekly_mins_per_game_id,weekly_mins_per_game_stat,mins_dict_all)

#Weekly Ast/Tov Last 7 Days Query:
def weekly_ast_tov_ratio_game_query():
    cursor.callproc('public.func_ast_tov_ratio_last_seven_days')
    weekly_ast_tov_ratio_id = cursor.fetchone()[0]
    cursor.callproc('public.func_ast_tov_ratio_last_seven_days')
    weekly_ast_tov_ratio_name = cursor.fetchone()[1]
    cursor.callproc('public.func_ast_tov_ratio_last_seven_days')
    weekly_ast_tov_ratio_stat = float(cursor.fetchone()[4])
    return weekly_ast_tov_ratio_id,weekly_ast_tov_ratio_name,weekly_ast_tov_ratio_stat

#weekly_ast_tov_ratio_id, weekly_ast_tov_ratio_name, weekly_ast_tov_ratio_stat = weekly_ast_tov_ratio_game_query()
#weekly_ast_tov_ratio_last_name = weekly_ast_tov_ratio_name.split()[1]

#Weekly Ast/Tov Last 7 Days Emoji Query:
def weekly_ast_tov_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ast_tov_game= total_dict[daily_player_id]
    if daily_stat >= overall_ast_tov_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_ast_tov_emoji = weekly_ast_tov_emoji_query(weekly_ast_tov_ratio_id,weekly_ast_tov_ratio_stat,ast_tov_dict_all)

#Weekly eFG Last 7 Days Query:
def weekly_efg_game_query():
    cursor.callproc('public.func_efg_last_seven_days')
    weekly_efg_id = cursor.fetchone()[0]
    cursor.callproc('public.func_efg_last_seven_days')
    weekly_efg_name = cursor.fetchone()[1]
    cursor.callproc('public.func_efg_last_seven_days')
    weekly_efg_stat = float(cursor.fetchone()[5])
    return weekly_efg_id,weekly_efg_name,weekly_efg_stat

#weekly_efg_id, weekly_efg_name, weekly_efg_stat = weekly_efg_game_query()
#weekly_efg_last_name = weekly_efg_name.split()[1]

#Weekly eFG Last 7 Days Emoji Query:
def weekly_efg_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_efg_game= total_dict[daily_player_id]
    if daily_stat >= overall_efg_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_efg_emoji = weekly_efg_emoji_query(weekly_efg_id,weekly_efg_stat,efg_dict_all)

#Weekly True Shooting Last 7 Days Query:
def weekly_ts_game_query():
    cursor.callproc('public.func_ts_last_seven_days')
    weekly_ts_id = cursor.fetchone()[0]
    cursor.callproc('public.func_ts_last_seven_days')
    weekly_ts_name = cursor.fetchone()[1]
    cursor.callproc('public.func_ts_last_seven_days')
    weekly_ts_stat = float(cursor.fetchone()[5])
    return weekly_ts_id,weekly_ts_name,weekly_ts_stat

#ekly_ts_id, weekly_ts_name, weekly_ts_stat = weekly_ts_game_query()
#weekly_ts_last_name = weekly_ts_name.split()[1]

#Weekly True Shooting Last 7 Days Emoji Query:
def weekly_ts_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_ts_game= total_dict[daily_player_id]
    if daily_stat >= overall_ts_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_ts_emoji = weekly_ts_emoji_query(weekly_efg_id,weekly_efg_stat,trsp_dict_all)

#Weekly Three Point Attempt Rate Last 7 Days Query:
def weekly_threepar_query():
    cursor.callproc('public.func_threepar_last_seven_days')
    weekly_threepar_id = cursor.fetchone()[0]
    cursor.callproc('public.func_threepar_last_seven_days')
    weekly_threepar_name = cursor.fetchone()[1]
    cursor.callproc('public.func_threepar_last_seven_days')
    weekly_threepar_stat = float(cursor.fetchone()[4])
    return weekly_threepar_id,weekly_threepar_name,weekly_threepar_stat

#weekly_threepar_id, weekly_threepar_name, weekly_threepar_stat = weekly_threepar_query()
#weekly_threepar_last_name = weekly_threepar_name.split()[1]

#Weekly Three Point Attempt Rate Last 7 Days Emoji Query:
def weekly_threepar_emoji_query(daily_player_id, daily_stat, total_dict):
    overall_threepar_game= total_dict[daily_player_id]
    if daily_stat >= overall_threepar_game:
        emoji = "\U0001F4C8" #upward emoji
    else:
        emoji = "\U0001F4C9" #downward emoji
    return emoji
#weekly_threepar_emoji = weekly_threepar_emoji_query(weekly_threepar_id,weekly_threepar_stat,threepar_dict_all)


#Daily Tweets:

#Monday:
def monday_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Ast: {daily_top_ast_last_name} - {daily_top_ast_recorded} {daily_ast_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top Ast/Tov: {daily_top_ast_tov_last_name} - {daily_top_ast_tov_num} {daily_ast_tov_emoji}
Top Usage Rate: {daily_usage_rate_last_name}- {daily_usage_rate_stat}% {daily_usage_rate_emoji}
Top eFG%: {daily_efg_last_name} - {daily_efg_recorded}% {daily_efg_emoji}
#Bulls #BullsNation
"""
    return tweet

#Tuesday:
def tues_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Ast: {daily_top_ast_last_name} - {daily_top_ast_recorded} {daily_ast_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top Ast/Tov: {daily_top_ast_tov_last_name} - {daily_top_ast_tov_num} {daily_ast_tov_emoji}
Top Usage Rate: {daily_usage_rate_last_name}- {daily_usage_rate_stat}% {daily_usage_rate_emoji}
Top eFG%: {daily_efg_last_name} - {daily_efg_recorded}% {daily_efg_emoji}
#Bulls #BullsNation
"""
    return tweet

#Wednesday:
def wed_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Ast: {daily_top_ast_last_name} - {daily_top_ast_recorded} {daily_ast_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top Mins: {daily_mins_last_name} - {daily_mins_stat} {daily_mins_emoji}
Top Ast Perc: {daily_ast_percent_last_name}- {daily_ast_percent_stat}% {daily_ast_percent_emoji}
Top eFG%: {daily_efg_last_name} - {daily_efg_recorded}% {daily_efg_emoji}
#Bulls #BullsNation
"""
    return tweet

# Thursday:
def thur_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Ast: {daily_top_ast_last_name} - {daily_top_ast_recorded} {daily_ast_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top 3PAr: {daily_threepar_last_name} - {daily_threepar_stat} {daily_threepar_emoji}
Top TS%: {daily_trsp_last_name}- {daily_trsp_recorded}% {daily_trsp_emoji}
Top TOV%: {daily_tov_percent_last_name} - {daily_tov_percent_stat}% {daily_tov_percent_emoji}
#Bulls #BullsNation
"""
    return tweet

#Friday:
def fri_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Ast: {daily_top_ast_last_name} - {daily_top_ast_recorded} {daily_ast_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top Ast/Tov: {daily_top_ast_tov_last_name} - {daily_top_ast_tov_num} {daily_ast_tov_emoji}
Top Usage Rate: {daily_usage_rate_last_name}- {daily_usage_rate_stat}% {daily_usage_rate_emoji}
Top eFG%: {daily_efg_last_name} - {daily_efg_recorded}% {daily_efg_emoji}
#Bulls #BullsNation
"""
    return tweet

#Saturday:
def sat_tweet():
    tweet = f"""
The Bulls {win_loss_result}{win_loss_emoji} - record {bulls_overall_record[0:2]} {bulls_overall_record[2]}
Top Scorer: {top_pts_score_last_name} - {top_pts_scored} {daily_ppg_emoji}
Top Reb: {top_reb_last_name} - {top_reb_recorded} {daily_total_reb_emoji}
Top Mins: {daily_mins_last_name} - {daily_mins_stat} {daily_mins_emoji}
Top eFG%: {daily_efg_last_name} - {daily_efg_recorded}% {daily_efg_emoji}
Top TS%: {daily_trsp_last_name} - {daily_trsp_recorded}% {daily_trsp_emoji}
Top 3PAr: {daily_threepar_last_name} - {daily_threepar_stat}% {daily_threepar_emoji}
#Bulls #BullsNation
"""
    return tweet

#Sunday:
def sun_tweet():
    tweet = f"""


#Bulls #BullsNation
"""
    return tweet

#Sunday Weekly Tweet:
def sun_weekly_tweet():
    weekly_tweet = f"""
Dates: {date_seven_days_ago} - {date_today}
Record: {win_last_seven_days} - {loss_last_seven_days} {emoji_last_seven_days}
Top PPG: {weekly_ptsg_last_name} - {weekly_ptsg_stat} {weekly_ptsg_emoji}
Top PTS (36 Mins): {weekly_pts_per_full_game_last_name} - {weekly_pts_per_full_game_stat} {weekly_pts_per_full_game_emoji}
Top Rebpg: {weekly_reb_per_game_last_name} - {weekly_reb_per_game_stat} {weekly_reb_per_game_emoji}
Top Ast: {weekly_ast_per_game_last_name} - {weekly_ast_per_game_stat} {weekly_ast_per_game_emoji}
Top Mins: {weekly_mins_per_game_last_name} - {weekly_mins_per_game_stat} {weekly_mins_per_game_emoji}
Top Ast/Tov: {weekly_ast_tov_ratio_last_name} - {weekly_ast_tov_ratio_stat} {weekly_ast_tov_emoji}
Top eFG%: {weekly_efg_last_name} - {weekly_efg_stat} {weekly_efg_emoji}
Top TS%: {weekly_ts_last_name} - {weekly_ts_stat} {weekly_ts_emoji}
Top 3PAr: {weekly_threepar_last_name} - {weekly_threepar_stat} {weekly_threepar_emoji}
#Bulls #BullsNation
"""
    return weekly_tweet

#print(sun_weekly_tweet())
#print(len(sun_weekly_tweet()))
#NEED TO SHORTEN TWEET

def day_week_tweet(cur_weekday_num):
    if cur_weekday_num == 0:
        send_tweet_function(twitter_api, monday_tweet())
    elif cur_weekday_num == 1:
        send_tweet_function(twitter_api,tues_tweet())
    elif cur_weekday_num == 2:
        send_tweet_function(twitter_api,wed_tweet())
    elif cur_weekday_num == 3:
        send_tweet_function(twitter_api,thur_tweet())
    elif cur_weekday_num == 4:
        send_tweet_function(twitter_api, fri_tweet())
    elif cur_weekday_num == 5:
        send_tweet_function(twitter_api, sat_tweet())
    elif cur_weekday_num == 6:
        send_tweet_function(twitter_api,sun_tweet())
        send_tweet_function(twitter_api,sun_weekly_tweet())
    return cur_weekday_num

def send_tweet_function(auth, tweet):
    twitter_api = auth
    return twitter_api.update_status(tweet)

day_week_tweet(cur_weekday_num)
connection.close()
