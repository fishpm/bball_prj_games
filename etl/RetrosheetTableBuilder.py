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


class RetrosheetTableBuilder()


    def init(self):
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
                self.rts_line_parser(file_path, tmp_dir)
                self.rts_db_update(tmp_dir)
                self.clean_tmp_dir(tmp_dir)
            else:
                print('Unrecognized file: %s. Skipping' % (element))


    def rts_line_parser(self, file_path, tmp_dir):
        """From a retrosheet file, parse it into a relational table"""
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
               , rts_player_id VARCHAR(35) NOT NULL
               , rts_play_sequence INTEGER
               , play_type play_type 
               , inning INTEGER
               , home_team BOOLEAN
               , batter_count VARCHAR(3)
               , pitch_meta VARCHAR(15)
               , play_meta VARCHAR(20)
               , sub_batting_order INTEGER
               , sub_field_position INTEGER
               , PRIMARY KEY (game_id, rts_player_id, rts_play_sequence)
            );
        """)

        print("Create game_info table")
        self.cur.execute("""
        """);




if __name__ == "__main__":
    """Parse cmd line args and build retrosheet tables"""
    pass
