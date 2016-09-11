"""
Retrosheet Table Builder

"""

import os
from os import listdir
from os.path import isfile, join
import sys
import itertools

import psycopg2

from etl.RetrosheetParser import RetrosheetLineParser

class RetrosheetTableBuilder(object):


    def __init__(self):
        conn = psycopg2.connect(**db_credentials)
        cur = conn.cursor()

        GAME_INFO_TABLE = 'game_info'
        PLAY_BY_PLAY_TABLE = 'play_by_play'
        STARTERS_TABLE = 'starters'


    def build_rts_tables(self, dir_path, tmp_dir):
        """From a directory of retrosheet files, build relational tables"""
        # Create tables
        self.create_rts_tables()
        # Loop through files
        for element in listdir(dir_path):
            if isfile(join(dir_path, element)) and \
                element.lower().endswith(('.eva', '.evn')):
                
                self.file_path = join(dir_path, element)
                self.rts_line_parser(self.file_path, tmp_dir)
                self.rts_db_update(tmp_dir)
                self.clean_tmp_dir(tmp_dir)
            else:
                print('Unrecognized file: %s. Skipping' % (element))


    def rts_line_parser(self, file_path, tmp_dir=''):
        """From a retrosheet file, parse it into a relational table"""

        rsp = RetrosheetLineParser()
        tmp_f = open(join(tmp_dir, 'temp.txt'), 'wb')
        tmp_output = csv.writer(tmp_f, quoting = csv.QUOTE_ALL)
        with open(self.file_path,'r') as f:
            for line in f:
                line_parts = line.rstrip().split(',')
         		parsed_line = rsp.type_parser(line_parts, a.parser_map)
         		if parsed_line:
         			parsed_line_list = list(itertools.chain.from_iterable([[k, parsed_line[k]] for k in parsed_line]))
         			tmp_output.writerow(parsed_line_list)

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
                , player_id VARCHAR(8) NOT NULL
                , player_name VARCHAR(35)
                , player_team VARCHAR(3)
                , home_team BOOLEAN
                , batting_order INTEGER
                , field_position INTEGER
                , PRIMARY KEY (game_id, player_id)
            );
            """)
        cur.commit()

        print("Create play_by_play table")
        self.cur.execute("""
            CREATE TYPE play_type AS ENUM ('play', 'sub', 'badj', 'padj'
                , 'ladj')

            CREATE TABLE play_by_play (
               game_id VARCHAR(12) NOT NULL
               , player_id VARCHAR(8) NOT NULL
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
               , PRIMARY KEY (game_id, player_id, rts_play_sequence)
            );
        """)
        cur.commit()

        print("Create game_info table")
        self.cur.execute("""
       	
        	CREATE TABLE game_info (
        		game_id VARCHAR(12) NOT NULL
        		, vistteam VARCHAR(3)
        		, hometeam VARCHAR(3)
        		, site VARCHAR(5)
        		, number INTEGER
        		, date DATE
                , info JSON
        		, PRIMARY KEY (game_id)
        	""");
        	cur.commit()

if __name__ == "__main__":
    """Parse cmd line args and build retrosheet tables"""
    pass
