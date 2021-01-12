*/
This is the SQL code I used to implement the Chicago Bulls Daily Twitter Account.
The setup is very basic as it currently only consists of one table.
I created SQL functions that I can call from my python code for the stats I am looking to tweet.
I sometimes created views to simplify some of the code in the functions.
Some of the sql code functions can be seen below.
I have considered expanding the database to include a Player Table, Game Table (Opponents Stats), and Team Table.
I created an index on game_date as that gets filtered on all the daily functions
The functions are in three main buckets: Daily, Weekly, Season.
Daily functions are used for the daily stats.
Weekly functions are used for the weekly roundup stats.
Season functions are used for the Emojis (Decide if that stat is getting better or worse)
/*

*/
Create Table
/*
CREATE TABLE public.bullsboxscore
(
    sql_uuid uuid NOT NULL DEFAULT uuid_generate_v1(),
    custom_id text COLLATE pg_catalog."default" NOT NULL,
    game_id character varying(30) COLLATE pg_catalog."default" NOT NULL,
    player_id bigint NOT NULL,
    player_name character varying(35) COLLATE pg_catalog."default" NOT NULL,
    team_id character varying(11) COLLATE pg_catalog."default" NOT NULL,
    team_abbreviation character varying(4) COLLATE pg_catalog."default" NOT NULL,
    age smallint NOT NULL,
    gp smallint NOT NULL,
    win smallint NOT NULL,
    loss smallint NOT NULL,
    mins real,
    fgm smallint,
    fga smallint,
    fgthreem smallint,
    fgthreea smallint,
    ftm smallint,
    fta smallint,
    oreb smallint,
    dreb smallint,
    reb smallint,
    ast smallint,
    tov smallint,
    stl smallint,
    blk smallint,
    blka smallint,
    pf smallint,
    pfdrawn smallint,
    pts smallint,
    plusminus smallint,
    game_date date NOT NULL,
    season character varying(20) COLLATE pg_catalog."default" NOT NULL,
    date_time_inserted timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT bullsboxscore_pkey PRIMARY KEY (sql_uuid)
)

*/
Create Functions: (I had 30+ functions so I have included a couple in this repositor.)
/*

-- FUNCTION: public.func_ast_percent_daily()

-- DROP FUNCTION public.func_ast_percent_daily();

CREATE OR REPLACE FUNCTION public.func_ast_percent_daily(
	)
    RETURNS TABLE(sql_uuid uuid, game_id character varying, game_date date, player_id bigint, player_name character varying, ast smallint, mins real, fgm smallint, game_fgm bigint, game_mins integer, ast_percent numeric)
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$

-------------------------------------------------------------------------------
-- Author       Grant Culp
-- Created      1/11/2020
-- Purpose      For the Daily Ast Percentage Query
-------------------------------------------------------------------------------
-- Modification History
--
-- 01/01/0000  Name
-- DESCRIPTION
-------------------------------------------------------------------------------

BEGIN
RETURN QUERY
	WITH ast_per_sub_query AS (
	SELECT bullsboxscore.sql_uuid, bullsboxscore.game_id,
		bullsboxscore.game_date, bullsboxscore.player_id,
		bullsboxscore.player_name, bullsboxscore.ast,
		bullsboxscore.mins, bullsboxscore.fgm,
		SUM(bullsboxscore.fgm) OVER(PARTITION BY bullsboxscore.game_id) AS game_fgm,
		SUM(bullsboxscore.mins) OVER(PARTITION BY bullsboxscore.game_id)::INTEGER AS game_mins
	FROM bullsboxscore
	WHERE bullsboxscore.game_date = (SELECT MAX(bullsboxscore.game_date)
					  FROM bullsboxscore))
	SELECT *, ROUND(100*ast_per_sub_query.ast/(((ast_per_sub_query.mins/(ast_per_sub_query.game_mins::FLOAT/5))*ast_per_sub_query.game_fgm)-ast_per_sub_query.fgm)::DECIMAL,2) AS ast_percent
	FROM ast_per_sub_query
	ORDER BY ast_percent DESC;
END;$$

-- FUNCTION: public.func_ast_percent_season(character varying)

-- DROP FUNCTION public.func_ast_percent_season(character varying);

CREATE OR REPLACE FUNCTION public.func_ast_percent_season(
	p_season character varying)
    RETURNS TABLE(player_id bigint, player_name character varying, season character varying, ast bigint, mins integer, fgm bigint, ast_team_total numeric, mins_team_total integer, fgm_team_total numeric, ast_percent numeric)
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
-------------------------------------------------------------------------------
-- Author       Grant Culp
-- Created      1/11/2020
-- Purpose      For the Season Ast Percentage Query
-------------------------------------------------------------------------------
-- Modification History
--
-- 01/01/0000  Name
-- DESCRIPTION
-------------------------------------------------------------------------------

BEGIN
	RETURN QUERY
		WITH RECURSIVE
		player_total_sub AS
		(
					SELECT bullsboxscore.player_id, bullsboxscore.player_name,bullsboxscore.season,
							SUM(bullsboxscore.ast) as ast,
							SUM(bullsboxscore.mins)::INTEGER as mins,
							SUM(bullsboxscore.fgm) as fgm
					FROM bullsboxscore
					WHERE bullsboxscore.season = p_season
					GROUP BY 1,2,3
		),
		player_season_total AS
		(
						SELECT *,
							SUM(player_total_sub.ast) OVER (PARTITION BY player_total_sub.season) AS ast_team_total,
							SUM(player_total_sub.mins) OVER (PARTITION BY player_total_sub.season)::INTEGER AS mins_team_total,
							SUM(player_total_sub.fgm) OVER (PARTITION BY player_total_sub.season) AS fgm_team_total
						FROM player_total_sub
		)
		SELECT *, ROUND(100*player_season_total.ast/(((player_season_total.mins/(player_season_total.mins_team_total::FLOAT/5))*player_season_total.fgm_team_total)-player_season_total.fgm)::DECIMAL,2) AS ast_percent
		FROM player_season_total
		ORDER BY ast_percent DESC;
END;$$

*/
Create Index
/*
-- Index: idx_game_date

-- DROP INDEX public.idx_game_date;

CREATE INDEX idx_game_date
    ON public.bullsboxscore USING btree
    (game_date ASC NULLS LAST)
    TABLESPACE pg_default;
