"""
Retrosheet Table Builder

"""

import os
from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
import sys

import psycopg2

from RetrosheetParser import RetrosheetLineParser

# Previously read class RetrosheetTableBuilder()...shouldn't there be 'object' inside () and ":" at the end of the line?
class RetrosheetTableBuilder(object):

	# I am not a python expert but shouldn't this always be "__init__"?
    def __init__(self):
        conn = psycopg2.connect(**db_credentials)
        cur = conn.cursor()

        GAME_INFO_TABLE = 'game_info'
        PLAY_BY_PLAY_TABLE = 'play_by_play'
        STARTERS_TABLE = 'starters'
        
        rts_line_types = RetrosheetLineParser.parser_map.keys()

    def build_rts_tables(self, dir_path, tmp_dir):
        """From a directory of retrosheet files, build relational tables"""
        # Create tables
        self.create_rts_tables()
        # Loop through files
        for element in listdir(dir_path):
            if isfile(join(dir_path, element)) and \
                element.lower().endswith(('.eva', '.evn')):
                # file_path was not previously defined.
                file_path = join(dir_path, element)
                self.rts_line_parser(file_path, tmp_dir)
                self.rts_db_update(tmp_dir)
                self.clean_tmp_dir(tmp_dir)
            else:
                print('Unrecognized file: %s. Skipping' % (element))

    def rts_line_parser(self, file_path, tmp_dir):
        """From a retrosheet file, parse it into a relational table"""

## My line of thinking with what is below is that the code needs to create a dictionary in the python environment that will be saved (temporarily) as a .csv (probably) and ultimately moved to a remote relational table (postgres).  Therefore, I think step 1 is creating dictionaries with keys corresponding to the variable names that will ultimately be stored in the relational tables. At least that's my line of thinking.

#         temp_game_info = dict.fromkeys([
#         		'game_id' , 'vistteam', 'hometeam', 'site', 'date', 'number', 'starttime', 'day_night', 'dh', 'umphome', 'ump1b', 'ump2b', 'ump3b', 'pitches', 'temp', 'winddir', 'windspeed', 'fieldcond', 'precip', 'sky', 'time_of_game', 'attendance', 'wp', 'lp', 'save', 'gwrbi', 'prim_key'
#         		])
#         
#         temp_pbp = dict.fromkeys([
#         		'game_id', 'rts_player_id', 'rts_play_sequence', 'player_team', 'play_type', 'inning', 'bottom_inning', 'home_team', 'rts_pitch_count', 'rts_pitch_seq', 'play_meta', 'sub_batting_order', 'sub_field_position', 'prim_key'
#         		])
#                
#         temp_starters = dict.fromkeys([
#                 'game_id', 'rts_player_id', 'player_name', 'player_team', 'home_team', 'batting_order', 'field_position', 'prim_key'
#                 ])

## I am a little in doubt about precisely how to structure this.  For example, we need to know what type of instance is returned for each line in order to know what to do with it, right?

#         with open(file_path,'r') as f:
#         	for line in f:
#         		morsel = RetrosheetLineParser.type_parser(line,
#         			RetrosheetLineParser.parser_map)        
	    pass
	
    def rts_db_update(self, tmp_dir):
        """Update the database from a set of temp files in relational format"""
        pass

    
    def clean_tmp_dir(self, tmp_dir):
        """Remove files from a tmp directory"""
        pass


    def create_rts_tables(self):
        print("Create starters table")
        self.cur.execute("""
            CREATE TABLE starters (
                game_id VARCHAR(12) NOT NULL
                , rts_player_id VARCHAR(8) NOT NULL
                , player_name VARCHAR(35)
                , player_team VARCHAR(3)
                , home_team BOOLEAN
                , batting_order INTEGER
                , field_position INTEGER
                , PRIMARY KEY (game_id, rts_player_id)
            );
            """)
        cur.commit()

        print("Create play_by_play table")
        self.cur.execute("""
            CREATE TYPE play_type AS ENUM ('play', 'sub', 'badj', 'padj'
                , 'ladj')

            CREATE TABLE play_by_play (
               game_id VARCHAR(12) NOT NULL
               , rts_player_id VARCHAR(8) NOT NULL
               , rts_play_sequence INTEGER NOT NULL
               , player_team VARCHAR(3)
               , play_type play_type 
               , inning INTEGER
               , bottom_inning BOOLEAN
               , home_team BOOLEAN
               , rts_pitch_count VARCHAR(3)
               , rts_pitch_seq VARCHAR(15)
               , play_meta VARCHAR(20)
               , sub_batting_order INTEGER
               , sub_field_position INTEGER
               , PRIMARY KEY (game_id, rts_player_id, rts_play_sequence)
            );
        """)
        cur.commit()

        print("Create game_info table")
        self.cur.execute("""
        	CREATE TYPE pitches_type AS ENUM ('pitches', 'count', 'none')
        	CREATE TYPE winddir_type AS ENUM ('fromcf', 'fromlf', 'fromrf',
        		'ltor', 'rtol', 'tocf', 'tolf', 'torf', 'unknown')
        	CREATE TYPE fieldcond_type AS ENUM ('unknown', 'soaked', 'wet',
        		'damp', 'dry')
        	CREATE TYPE precip_type AS ENUM ('unknown', 'none', 'drizzle',
        		'showers', 'rain', 'snow')
        	CREATE TYPE sky_type AS ENUM ('unknown', 'sunny', 'cloudy', 'overcast', 'night', 'dome')
        	
        	CREATE TABLE game_info (
        		game_id VARCHAR(12) NOT NULL
        		, vistteam VARCHAR(3)
        		, hometeam VARCHAR(3)
        		, site VARCHAR(5)
        		, date DATE
        		, number INTEGER
        		, day_night BOOLEAN
        		, dh BOOLEAN
        		, umphome VARCHAR(8)
        		, ump1b VARCHAR(8)
        		, ump2b VARCHAR(8)
        		, ump3b VARCHAR(8)
        		, pitches pitches_type
        		, starttime time
        		, temp INTEGER
        		, winddir winddir_type
        		, windspeed INTEGER
        		, fieldcond fieldcond_type
        		, precip precip_type
        		, sky sky_type
        		, time_of_game INTEGER
        		, attendance INTEGER
        		, wp VARCHAR(8)
        		, lp VARCHAR(8)
        		, save VARCHAR(8)
        		, gwrbi VARCHAR(8)
        		, PRIMARY KEY (game_id)
        	""");
        	cur.commit()

if __name__ == "__main__":
    """Parse cmd line args and build retrosheet tables"""
    pass
