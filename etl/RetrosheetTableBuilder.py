"""
Retrosheet Table Builder

"""

import os
import re
from os import listdir
from os.path import isfile, join
import sys
import itertools
import csv
import json
import psycopg2
from etl.RetrosheetParser import RetrosheetLineParser
from etl.RetrosheetTableSetter import RetrosheetTableSetter

class RetrosheetTableBuilder(object):

    def __init__(self):
		
		# Try to connect to db
		try:
			self.conn = psycopg2.connect("dbname='patrickfisher' user='patrickfisher' host='localhost'")
			print "Connected!"
		except:
			print "I am unable to connect to the database"
		
		# Open a cursor to the connection.
		self.cur = self.conn.cursor()
		
    def build_rts_tables(self, dir_path, tmp_dir=''):
        """From a directory of retrosheet files, build relational tables"""

        # Create tables
        self.create_rts_tables()
        
        # Loop through files
        for element in listdir(dir_path):
            
            if isfile(join(dir_path, element)) and element.lower().endswith(('.eva', '.evn')):
            	
            	self.file_path = join(dir_path, element)
                print 'Reading ' + self.file_path
                rts_output = self.rts_line_parser(self.file_path)
                self.rts_db_update(rts_output)
                print 'Finished ' + self.file_path
#                 self.clean_tmp_dir(tmp_dir)
            else:
                print('Unrecognized file: %s. Skipping' % (element))
	
    def rts_line_parser(self, file_path, tmp_dir=''):
		"""From a retrosheet file, parse it into a relational table"""
		
		# Create parsing and setting objects
		rsp = RetrosheetLineParser()
		rts_setter = RetrosheetTableSetter()
		
		with open(file_path,'r') as f:
			for line in f:
				# Split up a line
				line_parts = line.rstrip().split(',')
				
				# Parse a line from a retrosheet file
				parsed_line = rsp.type_parser(line_parts, rsp.parser_map)
				
				# Determine how to store a parsed line via rts_setter
				if parsed_line:
					rts_event_dict = rts_setter.setter_parser(parsed_line, rts_setter.setter_map)
			
 			print "Done with " + file_path + "!"
		
		return rts_event_dict
	
    def rts_db_update(self, rts_output):
		"""Update the database from a set of temp files in relational format"""
		
		# Add values to starters table
		self.cur.executemany("""
    		INSERT INTO starters (game_id, player_id, player_name, field_position, batting_order, home_team)
    		VALUES
    			(%(game_id)s, %(player_id)s, %(player_name)s, %(field_position)s, %(batting_order)s, %(home_team)s)""", [rts_output['starters'][dict] for dict in rts_output['starters'].keys()])
		self.conn.commit()
		
		# Dump 'info' types into one json to read to database.
		for key in rts_output['ginfo'].keys():
			rts_output['ginfo'][key]['info'] = json.dumps(rts_output['ginfo'][key]['info'])
		
		# Add values to game_info table
		self.cur.executemany("""
			INSERT INTO game_info
				(game_id, visteam, hometeam, date, info)
			VALUES
				(%(game_id)s, %(visteam)s, %(hometeam)s, %(date)s, %(info)s)""",
			[rts_output['ginfo'][dict] for dict in rts_output['ginfo'].keys()])
		self.conn.commit()
		
		# Add values to play_by_play table
		self.cur.executemany("""
			INSERT INTO play_by_play
				(inning, play_meta, rts_pitch_sequence, rts_play_sequence, rts_pitch_count, player_id, game_id, play_type, bottom_inning, sub_batting_order, sub_field_position, comment)
			VALUES
				(%(inning)s, %(play_meta)s, %(rts_pitch_sequence)s, %(rts_play_sequence)s, %(rts_pitch_count)s, %(player_id)s, %(game_id)s, %(play_type)s, %(bottom_inning)s, %(sub_batting_order)s, %(sub_field_position)s, %(comment)s)""",
			[rts_output['pbp'][dict] for dict in rts_output['pbp'].keys()])
		self.conn.commit()
	
    def clean_tmp_dir(self, tmp_dir):
		"""Remove files from a tmp directory"""
		pass
	
    def check_rts_exist(self, table_name):
		"""Check whether an rts table exists"""
		
		self.cur.execute("""
			SELECT EXISTS(
				SELECT 1
				FROM information_schema.tables
				WHERE table_schema = 'public'
				AND table_name = %s);
			""", (table_name,))
		ans = self.cur.fetchall()
		self.conn.commit()
		
		return ans[0][0]
	
    def check_type_exist(self, type):
		"""Check whether an rts type exists"""
		
		self.cur.execute("""
			SELECT EXISTS(
				SELECT 1
				FROM pg_type
				WHERE typname = 'play_type');
			""")
		ans = self.cur.fetchall()
		self.conn.commit()
		
		return ans[0][0]
	
    def create_rts_tables(self):
		"""Create rts tables"""
		
		# If a starters table cannot be found, make it.
		if self.check_rts_exist('starters') is False:
			print('Create starters table')
			self.cur.execute("""
				CREATE TABLE starters (
					game_id VARCHAR(12) NOT NULL
					, player_id VARCHAR(8) NOT NULL
					, player_name VARCHAR(35)
					, home_team BOOLEAN
					, batting_order INTEGER
					, field_position INTEGER
					, PRIMARY KEY (game_id, player_id)
					);
				""")
			self.conn.commit()
		else:
			
			print('starters table already exists!')
					
		# If play_type type cannot be found, make it.
		if self.check_type_exist('play_type') is False:
			print("Create play_type TYPE")
			self.cur.execute("""
				CREATE TYPE play_type AS ENUM ('play', 'sub', 'badj', 'padj'
					, 'ladj');
				""")
			self.conn.commit()
		else:
			
			print("play_type type already exists!")
		
		# If play_by_play table cannot be found, make it.
		if self.check_rts_exist('play_by_play') is False:
			print("Create play_by_play table")
			self.cur.execute("""
				CREATE TABLE play_by_play (
				   game_id VARCHAR(12) NOT NULL
				   , player_id VARCHAR(8) NOT NULL
				   , rts_play_sequence INTEGER NOT NULL
				   , play_type play_type 
				   , inning INTEGER
				   , bottom_inning BOOLEAN
				   , rts_pitch_count VARCHAR(3)
				   , rts_pitch_sequence VARCHAR(30)
				   , play_meta VARCHAR(50)
				   , sub_batting_order INTEGER
				   , sub_field_position INTEGER
				   , comment VARCHAR(500)
				   , PRIMARY KEY (game_id, player_id, rts_play_sequence)
				   );
			""")
			self.conn.commit()
		else:
			
			print('play_by_play table already exists!')
		
		# If a game_info table cannot be found, make it.
		if self.check_rts_exist('game_info') is False:
			print("Create game_info table")
			self.cur.execute("""
				CREATE TABLE game_info (
					game_id VARCHAR(12) NOT NULL
					, visteam VARCHAR(3)
					, hometeam VARCHAR(3)
					, date DATE
					, info JSON
					, PRIMARY KEY (game_id)
					)
				""");
			self.conn.commit()
		else:
			print('game_info table already exists!')


if __name__ == "__main__":
    """Parse cmd line args and build retrosheet tables"""
    pass
