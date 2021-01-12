"""
This is the file that tweets out the stats interacting with the
functions from the sql_queries file.
"""

import json
import datetime as dt
import sys
import tweepy
import sql_queries

# Twitter Credentials
with open(r"/Users/GrantCulp/Desktop/Python/credentials_python_info.txt") as f:
    data = json.loads(f.read())
    CONSUMER_KEY = data['twitter']['bulls_account']['cons_key']
    CONSUMER_SECRET = data['twitter']['bulls_account']['cons_secret']
    ACCESS_TOKEN = data['twitter']['bulls_account']['access_token']
    ACCESS_TOKEN_SECRET = data['twitter']['bulls_account']['access_token_secret']

twitter_auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
twitter_auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(twitter_auth)

# We first need to get the day of the week
# This will be used to decide what tweet to send
# And if we need to send the weekly tweet
# 0 = Monday; 6 = Sunday
CUR_WEEKDAY_NUM = dt.datetime.today().weekday()
YESTERDAY_DATE = dt.date.today() - dt.timedelta(days=1)

# If there was no game played yesterday exit
# But if it is a Sunday then do not exit
if YESTERDAY_DATE != sql_queries.game_date_yest_query() and CUR_WEEKDAY_NUM != 6:
    sys.exit("No game yesterday and not a Sunday")
else:
    pass


def send_tweet_func(tweet):
    """
    This function takes in a string and tweets it
    :param tweet: String
    :return: Success message
    """
    twitter_api.update_status(tweet)
    return "Tweet Sent"


def daily_base_stats():
    """
    This function gives us the base tweet for the daily tweets.
    For example every tweet has the bulls record and their last result
    :return: String
    """
    daily_result, daily_result_emoji = sql_queries.daily_record_query()
    season_gp, season_wins, season_loss, season_record_emoji = sql_queries.season_record_query('2020-2021')

    # Daily Point Leader
    daily_ppts_id, daily_ppts_name, daily_ppts_stat = sql_queries.daily_stat_leader_query('func_pts_daily', 2, 3, 4)
    # Creating PPG Leader Dict for Season (Used for Emoji)
    season_ppts_dict = sql_queries.dict_stat_query('func_ptspg_season', '2020-2021', 0, 3)
    # Daily Point Leader Emoji
    daily_ppts_emoji = sql_queries.emoji_standard_query(daily_ppts_id, daily_ppts_stat, season_ppts_dict)

    # Daily Ast Leader
    daily_ast_id, daily_ast_name, daily_ast_stat = sql_queries.daily_stat_leader_query('func_ast_daily', 2, 3, 4)
    # Creating ASTPG Leader Dict for Season (Used for Emoji)
    season_ast_dict = sql_queries.dict_stat_query('func_astpg_season', '2020-2021', 0, 4)
    # Daily Ast Leader Emoji
    daily_ast_emoji = sql_queries.emoji_standard_query(daily_ast_id, daily_ast_stat, season_ast_dict)

    # Daily Rebound Leaders
    daily_reb_id, daily_reb_name, daily_reb_stat = sql_queries.daily_stat_leader_query('func_reb_daily', 2, 3, 4)
    # Creating REBPG Leader Dict for Season (Used for Emoji)
    season_reb_dict = sql_queries.dict_stat_query('func_rebpg_season', '2020-2021', 0, 4)
    # Daily Reb Leader Emoji
    daily_reb_emoji = sql_queries.emoji_standard_query(daily_reb_id, daily_reb_stat, season_reb_dict)
    # Formatting and returning the base tweet
    base_tweet = f"""
The Bulls {daily_result} {daily_result_emoji} - record({season_wins}-{season_loss}) {season_record_emoji}
Daily Leaders:
Points: {daily_ppts_name} {daily_ppts_stat} {daily_ppts_emoji}
Ast: {daily_ast_name} {daily_ast_stat} {daily_ast_emoji}
Reb: {daily_reb_name} {daily_reb_stat} {daily_reb_emoji}"""
    return base_tweet


daily_base_tweet = daily_base_stats()


def daily_monday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Ast Tov Ratio Leader
    daily_ast_tov_id, daily_ast_tov_name, daily_ast_tov_stat = \
        sql_queries.daily_stat_leader_query('func_ast_tov_ratio_daily', 2, 3, 6)
    # Creating Ast/Tov Dict for Season (Used for Emoji)
    season_ast_tov_dict = sql_queries.dict_stat_query('func_ast_tov_ratio_season', '2020-2021', 0, 4)
    # Daily Ast/Tov Emoji
    daily_ast_tov_emoji = sql_queries.emoji_standard_query(daily_ast_tov_id, daily_ast_tov_stat, season_ast_tov_dict)

    # 2. Daily Turnover Percentage Leader (High Bad)
    daily_tov_perc_id, daily_tov_perc_name, daily_tov_perc_stat = \
        sql_queries.daily_stat_leader_query('func_tov_perc_daily', 3, 4, 8)
    # Creating Tov Perc Dict for Season (Used for Emoji)
    season_tov_perc_dict = sql_queries.dict_stat_query('func_tov_perc_season', '2020-2021', 0, 6)
    # Daily Tov Percent Emoji
    daily_tov_perc_emoji = sql_queries.emoji_reversed_query(daily_tov_perc_id, daily_tov_perc_stat, season_tov_perc_dict)

    # 3. Daily Free Throw Attempt Rate Leader
    daily_ftar_id, daily_ftar_name, daily_ftar_stat = sql_queries.daily_stat_leader_query('func_ftar_daily', 3, 4, 7)
    # Creating FTAR Dict for Season (Used for Emoji)
    season_ftar_dict = sql_queries.dict_stat_query('func_ftar_season', '2020-2021', 0, 4)
    # Daily FTAR Emoji
    daily_ftar_emoji = sql_queries.emoji_standard_query(daily_ftar_id, daily_ftar_stat, season_ftar_dict)

    # 4. Daily Effective Field Goal Percent Leader
    daily_efg_id, daily_efg_name, daily_efg_stat = sql_queries.daily_stat_leader_query('func_efg_daily', 3, 4, 5)
    # Creating EFG Dict for Season (Used for Emoji)
    season_efg_dict = sql_queries.dict_stat_query('func_efg_season', '2020-2021', 0, 5)
    # Daily EFG Emoji
    daily_efg_emoji = sql_queries.emoji_standard_query(daily_efg_id, daily_efg_stat, season_efg_dict)

    formatted_tweet = f"""
{base_tweet}
Ast/Tov: {daily_ast_tov_name} {daily_ast_tov_stat} {daily_ast_tov_emoji}
TOV%: {daily_tov_perc_name} {daily_tov_perc_stat} {daily_tov_perc_emoji}
FTr: {daily_ftar_name} {daily_ftar_stat} {daily_ftar_emoji}
eFG%: {daily_efg_name} {daily_efg_stat} {daily_efg_emoji}"""
    return formatted_tweet


def daily_tuesday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in Mins
    daily_mins_id, daily_mins_name, daily_mins_stat = sql_queries.daily_stat_leader_query('public.func_mins_daily', 3, 4, 5)
    # Creating Season Dict for Mins (Used for Emoji)
    season_mins_dict = sql_queries.dict_stat_query('func_minspg_season', '2020-2021', 0, 4)
    # Daily Mins Emoji
    daily_mins_emoji = sql_queries.emoji_standard_query(daily_mins_id, daily_mins_stat, season_mins_dict)

    # 2. Daily Leader in Ast Percentage
    daily_ast_perc_id, daily_ast_perc_name, daily_ast_perc_stat = sql_queries.daily_stat_leader_query('func_ast_percent_daily', 3, 4, 10)
    # Creating Season Dict for Mins (Used for Emoji)
    season_ast_perc_dict = sql_queries.dict_stat_query('func_ast_percent_season', '2020-2021', 0, 9)
    # Daily Ast Percent Dict
    dail_ast_perc_emoji = sql_queries.emoji_standard_query(daily_ast_perc_id, daily_ast_perc_stat, season_ast_perc_dict)

    # 3. Daily Leader in 3 Point Attempt Rate
    daily_threepar_id, daily_threepar_name, daily_threepar_stat = sql_queries.daily_stat_leader_query('func_threepar_daily', 2, 3, 6)
    # Creating Season Dict for 3 Point Attempt Rate
    season_threepar_dict = sql_queries.dict_stat_query('func_threepar_season', '2020-2021', 0, 4)
    # Daily 3 Point Attempt Rate Query
    daily_threepar_emoji = sql_queries.emoji_standard_query(daily_threepar_id, daily_threepar_stat, season_threepar_dict)

    # 4. Daily Leader in True Shooting Percentage
    daily_tsp_id, daily_tsp_name, daily_tsp_stat = sql_queries.daily_stat_leader_query('func_tsp_daily', 2, 3, 7)
    # Creating Season Dict for True Shooting Percentage
    season_tsp_dict = sql_queries.dict_stat_query('func_tsp_season', '2020-2021', 0, 5)
    # Daily True Shooting Percentage Emoji
    daily_tsp_emoji = sql_queries.emoji_standard_query(daily_tsp_id, daily_tsp_stat, season_tsp_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
Mins: {daily_mins_name} {daily_mins_stat} {daily_mins_emoji}
AST%: {daily_ast_perc_name} {daily_ast_perc_stat} {dail_ast_perc_emoji}
3PAr: {daily_threepar_name} {daily_threepar_stat} {daily_threepar_emoji}
TS%: {daily_tsp_name} {daily_tsp_stat} {daily_tsp_emoji}"""
    return formatted_tweet


def daily_wednesday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in Steals
    daily_stl_id, daily_stl_name, daily_stl_stat = sql_queries.daily_stat_leader_query('func_stl_daily', 3, 4, 5)
    # Creating Season Dict for Steals
    season_stl_dict = sql_queries.dict_stat_query('func_stlpg_season', '2020-2021', 0, 4)
    # Daily STL Emoji
    daily_stl_emoji = sql_queries.emoji_standard_query(daily_stl_id, daily_stl_stat, season_stl_dict)

    # 2. Daily Leader in Blks
    daily_blk_id, daily_blk_name, daily_blk_stat = sql_queries.daily_stat_leader_query('func_blk_daily', 3, 4, 5)
    # Creating Season Dict for Blocks
    season_blk_dict = sql_queries.dict_stat_query('func_blkpg_season', '2020-2021', 0, 4)
    # Daily BLK Emoji
    daily_blk_emoji = sql_queries.emoji_standard_query(daily_blk_id, daily_blk_stat, season_blk_dict)

    # 3. Daily Leader in 3P%
    daily_threeperc_id, daily_threeperc_name, daily_threeperc_stat = sql_queries.daily_stat_leader_query('func_threepercent_daily', 3, 4, 7)
    # Creating Season Dict for 3P%
    season_threeperc_dict = sql_queries.dict_stat_query('func_threepercent_season', '2020-2021', 0, 4)
    # Daily 3P% Emoji
    daily_threeperc_emoji = sql_queries.emoji_standard_query(daily_threeperc_id, daily_threeperc_stat, season_threeperc_dict)

    # 4. Daily Leader in Ast Percentage
    daily_ast_perc_id, daily_ast_perc_name, daily_ast_perc_stat = sql_queries.daily_stat_leader_query('func_ast_percent_daily', 3, 4, 10)
    # Creating Season Dict for Mins (Used for Emoji)
    season_ast_perc_dict = sql_queries.dict_stat_query('func_ast_percent_season', '2020-2021', 0, 9)
    # Daily Ast Percent Dict
    dail_ast_perc_emoji = sql_queries.emoji_standard_query(daily_ast_perc_id, daily_ast_perc_stat, season_ast_perc_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
Steals: {daily_stl_name} {daily_stl_stat} {daily_stl_emoji}
BLK: {daily_blk_name} {daily_blk_stat} {daily_blk_emoji}
3P%: {daily_threeperc_name} {daily_threeperc_stat} {daily_threeperc_emoji}
AST%: {daily_ast_perc_name} {daily_ast_perc_stat} {dail_ast_perc_emoji}"""
    return formatted_tweet


def daily_thursday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in 3 Point Attempt Rate
    daily_threepar_id, daily_threepar_name, daily_threepar_stat = sql_queries.daily_stat_leader_query(
        'func_threepar_daily', 2, 3, 6)
    # Creating Season Dict for 3 Point Attempt Rate
    season_threepar_dict = sql_queries.dict_stat_query('func_threepar_season', '2020-2021', 0, 4)
    # Daily 3 Point Attempt Rate Query
    daily_threepar_emoji = sql_queries.emoji_standard_query(daily_threepar_id, daily_threepar_stat,
                                                            season_threepar_dict)
    # 2. Daily Leader in 3P%
    daily_threeperc_id, daily_threeperc_name, daily_threeperc_stat = \
        sql_queries.daily_stat_leader_query('func_threepercent_daily', 3, 4, 7)
    # Creating Season Dict for 3P%
    season_threeperc_dict = sql_queries.dict_stat_query('func_threepercent_season', '2020-2021', 0, 4)
    # Daily 3P% Emoji
    daily_threeperc_emoji = sql_queries.emoji_standard_query(daily_threeperc_id, daily_threeperc_stat,
                                                             season_threeperc_dict)

    # 3. Daily Leader in True Shooting Percentage
    daily_tsp_id, daily_tsp_name, daily_tsp_stat = sql_queries.daily_stat_leader_query('func_tsp_daily', 2, 3, 7)
    # Creating Season Dict for True Shooting Percentage
    season_tsp_dict = sql_queries.dict_stat_query('func_tsp_season', '2020-2021', 0, 5)
    # Daily True Shooting Percentage Emoji
    daily_tsp_emoji = sql_queries.emoji_standard_query(daily_tsp_id, daily_tsp_stat, season_tsp_dict)

    # 4. Daily Effective Field Goal Percent Leader
    daily_efg_id, daily_efg_name, daily_efg_stat = sql_queries.daily_stat_leader_query('func_efg_daily', 3, 4, 5)
    # Creating EFG Dict for Season (Used for Emoji)
    season_efg_dict = sql_queries.dict_stat_query('func_efg_season', '2020-2021', 0, 5)
    # Daily EFG Emoji
    daily_efg_emoji = sql_queries.emoji_standard_query(daily_efg_id, daily_efg_stat, season_efg_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
3PAr: {daily_threepar_name} {daily_threepar_stat} {daily_threepar_emoji}
3P%: {daily_threeperc_name} {daily_threeperc_stat} {daily_threeperc_emoji}
TS%: {daily_tsp_name} {daily_tsp_stat} {daily_tsp_emoji}
eFG%: {daily_efg_name} {daily_efg_stat} {daily_efg_emoji}"""
    return formatted_tweet


def daily_friday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in Mins
    daily_mins_id, daily_mins_name, daily_mins_stat = sql_queries.daily_stat_leader_query('public.func_mins_daily', 3, 4, 5)
    # Creating Season Dict for Mins (Used for Emoji)
    season_mins_dict = sql_queries.dict_stat_query('func_minspg_season', '2020-2021', 0, 4)
    # Daily Mins Emoji
    daily_mins_emoji = sql_queries.emoji_standard_query(daily_mins_id, daily_mins_stat, season_mins_dict)

    # 2. Daily Turnover Percentage Leader (High Bad)
    daily_tov_perc_id, daily_tov_perc_name, daily_tov_perc_stat = sql_queries.daily_stat_leader_query('func_tov_perc_daily', 3, 4, 8)
    # Creating Tov Perc Dict for Season (Used for Emoji)
    season_tov_perc_dict = sql_queries.dict_stat_query('func_tov_perc_season', '2020-2021', 0, 6)
    # Daily Tov Percent Emoji
    daily_tov_perc_emoji = sql_queries.emoji_reversed_query(daily_tov_perc_id, daily_tov_perc_stat, season_tov_perc_dict)

    # 3. Daily Ast Tov Ratio Leader
    daily_ast_tov_id, daily_ast_tov_name, daily_ast_tov_stat = sql_queries.daily_stat_leader_query('func_ast_tov_ratio_daily', 2, 3, 6)
    # Creating Ast/Tov Dict for Season (Used for Emoji)
    season_ast_tov_dict = sql_queries.dict_stat_query('func_ast_tov_ratio_season', '2020-2021', 0, 4)
    # Daily Ast/Tov Emoji
    daily_ast_tov_emoji = sql_queries.emoji_standard_query(daily_ast_tov_id, daily_ast_tov_stat, season_ast_tov_dict)

    # 4. Daily Leader in Steals
    daily_stl_id, daily_stl_name, daily_stl_stat = sql_queries.daily_stat_leader_query('func_stl_daily', 3, 4, 5)
    # Creating Season Dict for Steals
    season_stl_dict = sql_queries.dict_stat_query('func_stlpg_season', '2020-2021', 0, 4)
    # Daily STL Emoji
    daily_stl_emoji = sql_queries.emoji_standard_query(daily_stl_id, daily_stl_stat, season_stl_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
Mins: {daily_mins_name} {daily_mins_stat} {daily_mins_emoji}
TOV%: {daily_tov_perc_name} {daily_tov_perc_stat} {daily_tov_perc_emoji}
Ast/Tov: {daily_ast_tov_name} {daily_ast_tov_stat} {daily_ast_tov_emoji}
STL%: {daily_stl_name} {daily_stl_stat} {daily_stl_emoji}"""
    return formatted_tweet


def daily_saturday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in Blks
    daily_blk_id, daily_blk_name, daily_blk_stat = sql_queries.daily_stat_leader_query('func_blk_daily', 3, 4, 5)
    # Creating Season Dict for Blocks
    season_blk_dict = sql_queries.dict_stat_query('func_blkpg_season', '2020-2021', 0, 4)
    # Daily BLK Emoji
    daily_blk_emoji = sql_queries.emoji_standard_query(daily_blk_id, daily_blk_stat, season_blk_dict)

    # 2. Daily Leader in Ast Percentage
    daily_ast_perc_id, daily_ast_perc_name, daily_ast_perc_stat = sql_queries.daily_stat_leader_query('func_ast_percent_daily', 3, 4, 10)
    # Creating Season Dict for Mins (Used for Emoji)
    season_ast_perc_dict = sql_queries.dict_stat_query('func_ast_percent_season', '2020-2021', 0, 9)
    # Daily Ast Percent Dict
    dail_ast_perc_emoji = sql_queries.emoji_standard_query(daily_ast_perc_id, daily_ast_perc_stat, season_ast_perc_dict)

    # 3. Daily Free Throw Attempt Rate Leader
    daily_ftar_id, daily_ftar_name, daily_ftar_stat = sql_queries.daily_stat_leader_query('func_ftar_daily', 3, 4, 7)
    # Creating FTAR Dict for Season (Used for Emoji)
    season_ftar_dict = sql_queries.dict_stat_query('func_ftar_season', '2020-2021', 0, 4)
    # Daily FTAR Emoji
    daily_ftar_emoji = sql_queries.emoji_standard_query(daily_ftar_id, daily_ftar_stat, season_ftar_dict)

    # 4. Daily Leader in 3 Point Attempt Rate
    daily_threepar_id, daily_threepar_name, daily_threepar_stat = sql_queries.daily_stat_leader_query('func_threepar_daily', 2, 3, 6)
    # Creating Season Dict for 3 Point Attempt Rate
    season_threepar_dict = sql_queries.dict_stat_query('func_threepar_season', '2020-2021', 0, 4)
    # Daily 3 Point Attempt Rate Query
    daily_threepar_emoji = sql_queries.emoji_standard_query(daily_threepar_id, daily_threepar_stat, season_threepar_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
BLK: {daily_blk_name} {daily_blk_stat} {daily_blk_emoji}
AST%: {daily_ast_perc_name} {daily_ast_perc_stat} {dail_ast_perc_emoji}
FTr: {daily_ftar_name} {daily_ftar_stat} {daily_ftar_emoji}
3PAr: {daily_threepar_name} {daily_threepar_stat} {daily_threepar_emoji}"""
    return formatted_tweet


def daily_sunday_tweet(base_tweet):
    """
    There are going to be 7 of these functions to create and format the tweets
    for each day.
    :param base_tweet: string from base_tweet function
    :return: string
    """
    # 1. Daily Leader in True Shooting Percentage
    daily_tsp_id, daily_tsp_name, daily_tsp_stat = sql_queries.daily_stat_leader_query('func_tsp_daily', 2, 3, 7)
    # Creating Season Dict for True Shooting Percentage
    season_tsp_dict = sql_queries.dict_stat_query('func_tsp_season', '2020-2021', 0, 5)
    # Daily True Shooting Percentage Emoji
    daily_tsp_emoji = sql_queries.emoji_standard_query(daily_tsp_id, daily_tsp_stat, season_tsp_dict)

    # 2. Daily Effective Field Goal Percent Leader
    daily_efg_id, daily_efg_name, daily_efg_stat = sql_queries.daily_stat_leader_query('func_efg_daily', 3, 4, 5)
    # Creating EFG Dict for Season (Used for Emoji)
    season_efg_dict = sql_queries.dict_stat_query('func_efg_season', '2020-2021', 0, 5)
    # Daily EFG Emoji
    daily_efg_emoji = sql_queries.emoji_standard_query(daily_efg_id, daily_efg_stat, season_efg_dict)

    # 3. Daily Leader in Blks
    daily_blk_id, daily_blk_name, daily_blk_stat = sql_queries.daily_stat_leader_query('func_blk_daily', 3, 4, 5)
    # Creating Season Dict for Blocks
    season_blk_dict = sql_queries.dict_stat_query('func_blkpg_season', '2020-2021', 0, 4)
    # Daily BLK Emoji
    daily_blk_emoji = sql_queries.emoji_standard_query(daily_blk_id, daily_blk_stat, season_blk_dict)

    # 4. Daily Free Throw Attempt Rate Leader
    daily_ftar_id, daily_ftar_name, daily_ftar_stat = sql_queries.daily_stat_leader_query('func_ftar_daily', 3, 4, 7)
    # Creating FTAR Dict for Season (Used for Emoji)
    season_ftar_dict = sql_queries.dict_stat_query('func_ftar_season', '2020-2021', 0, 4)
    # Daily FTAR Emoji
    daily_ftar_emoji = sql_queries.emoji_standard_query(daily_ftar_id, daily_ftar_stat, season_ftar_dict)

    # Creating the Tweet:
    formatted_tweet = f"""
{base_tweet}
TS%: {daily_tsp_name} {daily_tsp_stat} {daily_tsp_emoji}
eFG%: {daily_efg_name} {daily_efg_stat} {daily_efg_emoji}
BLK: {daily_blk_name} {daily_blk_stat} {daily_blk_emoji}
FTr: {daily_ftar_name} {daily_ftar_stat} {daily_ftar_emoji}"""
    return formatted_tweet

# TODO: Still need to do the weekly stat roundup

# Deciding which tweet to send based on the Day of the Week
if CUR_WEEKDAY_NUM == 0:
    tweet_to_send = daily_monday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 1:
    tweet_to_send = daily_tuesday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 2:
    tweet_to_send = daily_wednesday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 3:
    tweet_to_send = daily_thursday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 4:
    tweet_to_send = daily_friday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 5:
    tweet_to_send = daily_saturday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
elif CUR_WEEKDAY_NUM == 6:
    tweet_to_send = daily_sunday_tweet(daily_base_tweet)
    print(tweet_to_send)
    # send_tweet_func(tweet_to_send)
