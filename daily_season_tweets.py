"""
This is the file that tweets out the daily season stats interacting with the
functions from the sql_queries file.
"""

import sql_queries


def top_n_dict(sql_result, n_len):
    """
    Function to take a list of data from SQL and return the top 5
    :param sql_result:
    :param n_len:
    :return:
    """
    sql_result = sql_result[:n_len]
    return_dict = {}
    counter = 0
    for player in sql_result:
        counter += 1
        return_dict[counter] = [player['player_name'].split(" ")[1], player['player_stat']]
    return return_dict


# These are going to be Daily Tweets to supplement the Tweets from the main pyt

def mon_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Points Per Game
    # Getting the PPG Result from SQL
    ppg_list_data = sql_queries.season_daily_stats('func_ptspg_season', '2020-2021', 0, 1, 4)
    ppg_top_five = top_n_dict(ppg_list_data, 5)
    top_ppg = ""
    for rank, player in ppg_top_five.items():
        top_ppg += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. Points Per 36 Mins
    # Getting the Points Per 36 Mins
    pp_full_game_list_data = sql_queries.season_daily_stats('func_pts_per_full_game_season', '2020-2021', 0, 1, 5)
    pp_full_game_list_data = top_n_dict(pp_full_game_list_data, 5)
    top_ppg_full_game = ""
    for rank, player in pp_full_game_list_data.items():
        top_ppg_full_game += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 PPG Season: 
{top_ppg}
Top 5 Points Per 36 Mins Season:
{top_ppg_full_game}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet


def tues_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Ast Per Game
    # Getting the APG Result from SQL
    apg_list_data = sql_queries.season_daily_stats('func_astpg_season', '2020-2021', 0, 1, 4)
    apg_top_five = top_n_dict(apg_list_data, 5)
    top_apg = ""
    for rank, player in apg_top_five.items():
        top_apg += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. Ast Per 36 Mins
    # Getting the Ast Per 36 Results from SQL
    ap_full_game_list_data = sql_queries.season_daily_stats('func_ast_per_full_game_season', '2020-2021', 0, 1, 5)
    ap_full_game_list_data = top_n_dict(ap_full_game_list_data, 5)
    top_apg_full_game = ""
    for rank, player in ap_full_game_list_data.items():
        top_apg_full_game += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 APG Season: 
{top_apg}
Top 5 Assist Per 36 Mins Season:
{top_apg_full_game}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet


def wed_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Three Point Attempt Rate
    # Getting the Three Point Attempt Rate Result from SQL
    threepar_list_data = sql_queries.season_daily_stats('func_threepar_season', '2020-2021', 0, 1, 4)
    threepar_top_five = top_n_dict(threepar_list_data, 5)
    top_threepar = ""
    for rank, player in threepar_top_five.items():
        top_threepar += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. Three Point Percentage
    # Getting the Three Point % from SQL
    three_point_perc_list_data = sql_queries.season_daily_stats('func_threepercent_season', '2020-2021', 0, 1, 4)
    three_point_perc_list_data = top_n_dict(three_point_perc_list_data, 5)
    top_three_point_perc = ""
    for rank, player in three_point_perc_list_data.items():
        top_three_point_perc += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 - 3 Pt Attempt Rate Season: 
{top_threepar}
Top 5 - 3% Season:
{top_three_point_perc}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet


def thur_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Effective Field goal Rate
    # Getting the EFG Result from SQL
    efg_list_data = sql_queries.season_daily_stats('func_efg_season', '2020-2021', 0, 1, 5)
    efg_list_data = top_n_dict(efg_list_data, 5)
    top_efg = ""
    for rank, player in efg_list_data.items():
        top_efg += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. True Shooting Percentage
    # Getting the True Shooting Perc % from SQL
    ts_perc_list_data = sql_queries.season_daily_stats('func_tsp_season', '2020-2021', 0, 1, 5)
    ts_perc_list_data = top_n_dict(ts_perc_list_data, 5)
    ts_perc = ""
    for rank, player in ts_perc_list_data.items():
        ts_perc += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 Effective FG Season: 
{top_efg}
Top 5 Three Point Percent Season:
{ts_perc}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet


def fri_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Tov per Game
    # Getting the APG Result from SQL
    tov_game_list_data = sql_queries.season_daily_stats('func_tov_per_game_season', '2020-2021', 0, 1, 4)
    tov_game_list_data = top_n_dict(tov_game_list_data, 5)
    top_tov_game = ""
    for rank, player in tov_game_list_data.items():
        top_tov_game += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. Tov Percentage
    # Getting the Three Point % from SQL
    tov_perc_list_data = sql_queries.season_daily_stats('func_tov_perc_season', '2020-2021', 0, 1, 6)
    tov_perc_list_data = top_n_dict(tov_perc_list_data, 5)
    top_tov_perc = ""
    for rank, player in tov_perc_list_data.items():
        top_tov_perc += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 Tov Per Game Season: 
{top_tov_game}
Top 5 Turnover Percent Season:
{top_tov_perc}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet


def sat_season_stats():
    """
    Function that queries the stats and returns the tweet
    :return: Tweet for the main python file
    """
    # 1. Steal per Game
    # Getting the STG Result from SQL
    stl_game_list_data = sql_queries.season_daily_stats('func_stlpg_season', '2020-2021', 0, 1, 4)
    stl_game_list_data = top_n_dict(stl_game_list_data, 5)
    stl_game = ""
    for rank, player in stl_game_list_data.items():
        stl_game += f"{rank}. {player[0]} - {player[1]}\n"

    # 2. Blks per Game
    # Getting the Blocks per Game from SQL
    blks_game_list_data = sql_queries.season_daily_stats('func_blkpg_season', '2020-2021', 0, 1, 4)
    blks_game_list_data = top_n_dict(blks_game_list_data, 5)
    top_blk_game = ""
    for rank, player in blks_game_list_data.items():
        top_blk_game += f"{rank}. {player[0]} - {player[1]}\n"

    # Formatting Tweet
    formatted_tweet = f"""
Top 5 Steals Per Game Season: 
{stl_game}
Top 5 Blocks Per Game Season:
{top_blk_game}
#BullsNation #Bulls #ChicagoBulls
"""
    return formatted_tweet
