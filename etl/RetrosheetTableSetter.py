"""
Retrosheet Table Builder

Goal: Organize parsed rts data into dict structure that can be read into database
"""

class RetrosheetTableSetter(object):
	
	def __init__(self):
		
		# Read parsed line into appropriate dict variable based on setter_map
		self.setter_map = {
			"id": self.setter_id,
			"version": self.setter_version,
			"info": self.setter_info,
            "start": self.setter_start,
            "play": self.setter_play,
            "sub": self.setter_sub,
            "data": self.setter_data,
            "com": self.setter_com,
            "ladj": self.setter_ladj,
            "badj": self.setter_badj,
            "padj": self.setter_padj
		}
		
		# Dicts to be read into database
		self.ginfo = {}
		self.pbp = {}
		self.starters = {}
		
		# Relevant tmp variables
		self.game_id = ''
		self.play_id = ''
		self.rts_play_sequence = 0
		self.comment_before = None
		self.comment_after = None
	
	def set_play_id(self, parsed_line=None):
		"""Update play_id variable"""
		
		if parsed_line is not None:
			self.rts_play_sequence += 1
		
		# Create play-specific ID
		set_play_id = self.game_id + '_' + str(self.rts_play_sequence)
		
		return set_play_id
	
	def setter_parser(self, parsed_line, setter_map):
		"""Determine which setter should be applied to a parsed line"""
		
		setter_type = parsed_line['type']
		
		# Identify and apply appropriate setter
		if setter_map.has_key(setter_type):
			setter = self.setter_map[setter_type]
			type_setter = setter(parsed_line)
		else:
			print('Unrecognized key: %s. Skipping' % (setter_type))		
		
			return type_setter
	
	def setter_id(self, parsed_line):
		"""Set id type"""
		
		# Reading a id line necessarily means it is a new game.
		self.rts_play_sequence = 0
		
		self.game_id = parsed_line['game_id']
		self.ginfo[self.game_id] = {}
		self.ginfo[self.game_id]['game_id'] = self.game_id
		self.ginfo[self.game_id]['info'] = {}

		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_version(self):
		"""Set version type"""
		
		# Indicated on retrosheet.org that the version record is obsolete.
		pass
	
	def setter_info(self, parsed_line):
		"""Set info type"""
		
		self.info_special_keys = {'visteam', 'hometeam','date'}
		
		# Get keys from parsed line.
		self.keys = [key for key in parsed_line.keys() if key is not 'type']
		
		# Add values from identified keys
		for key in self.keys:
			self.ginfo[self.game_id]['info'][key] = parsed_line[key]
			if key in self.info_special_keys:
				self.ginfo[self.game_id][key] = parsed_line[key]
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_start(self, parsed_line):
		"""Set start type"""
		
		starter_id = self.game_id + parsed_line['player_id']
		self.starters[starter_id] = {}
		self.starters[starter_id]['game_id'] = self.game_id
		self.starters[starter_id]['player_id'] = parsed_line['player_id']
		self.starters[starter_id]['player_name'] = parsed_line['player_name']
		self.starters[starter_id]['home_team'] = parsed_line['player_team']
		self.starters[starter_id]['batting_order'] = 						parsed_line['batting_order']
		self.starters[starter_id]['field_position'] = 	parsed_line['field_position']
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_play(self, parsed_line):
		"""Set play type"""
		
		# Play-relevant comments almost always come after play is described. This updates comment field where one is detected.
		# Some comments are very long. Truncates at 500 characters.
		if self.comment_after and len(self.comment_after) > 500:
			self.pbp[self.play_id]['comment'] = self.comment_after[:500]
			self.comment_after = None
		elif self.comment_after and len(self.comment_after) < 500:
			self.pbp[self.play_id]['comment'] = self.comment_after
			self.comment_after = None
		
		self.play_id = self.set_play_id(parsed_line)
		self.pbp[self.play_id] = {}
		self.pbp[self.play_id]['game_id'] = self.game_id
		self.pbp[self.play_id]['player_id'] = parsed_line['player_id']
		self.pbp[self.play_id]['rts_play_sequence'] = self.rts_play_sequence
		self.pbp[self.play_id]['play_type'] = parsed_line['type']
		self.pbp[self.play_id]['inning'] = parsed_line['inning']
		self.pbp[self.play_id]['bottom_inning'] = parsed_line['home_team']
		self.pbp[self.play_id]['rts_pitch_count'] = parsed_line['rts_pitch_count']
		self.pbp[self.play_id]['rts_pitch_sequence'] = parsed_line['rts_pitch_seq']
		self.pbp[self.play_id]['play_meta'] = parsed_line['play_meta']
		
		# Occasionally there is a comment before a play. Handles those instances.
		if self.comment_before:
			self.pbp[self.play_id]['comment'] = self.comment_before
			self.comment_before = None
		
		self.add_none(self.pbp[self.play_id])
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_sub(self, parsed_line):
		"""Set sub type"""
		
		self.play_id = self.set_play_id(parsed_line)
		self.pbp[self.play_id] = {}
		self.pbp[self.play_id]['game_id'] = self.game_id
		self.pbp[self.play_id]['player_id'] = parsed_line['player_id']
		self.pbp[self.play_id]['rts_play_sequence'] = self.rts_play_sequence
		self.pbp[self.play_id]['play_type'] = parsed_line['type']
# 		self.pbp[self.play_id]['player_team'] = parsed_line['player_team']
		self.pbp[self.play_id]['sub_batting_order'] = parsed_line['batting_order']
		self.pbp[self.play_id]['sub_field_position'] = parsed_line['field_position']
		self.pbp[self.play_id]['player_name'] = parsed_line['player_name']
		
		self.add_none(self.pbp[self.play_id])
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_data(self, parsed_line):
		"""Set data type"""
		
		set_special_keys = ['earned_runs', 'player_id']
		
		# Get keys from parsed line.
		self.keys = [key for key in parsed_line.keys() if key is not 'type']
		
		# Add values from identified keys
		if set_special_keys.sort() == self.keys.sort():
			self.ginfo[self.game_id]['info'][parsed_line['player_id']] = parsed_line['earned_runs']
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_ladj(self, parsed_line):
		"""Set ladj type"""
		
		# Inconsistency between how these events are listed in files and described on the website.
		pass
	
	def setter_badj(self, parsed_line):
		"""Set badj type"""
		
		self.comment_before = 'badj: ' + parsed_line['badj_note']
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_padj(self, parsed_line):
		
		self.comment_before = 'padj: ' + parsed_line['padj_note']
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def setter_com(self, parsed_line):
		"""Set com type"""
		
		# Special case where comment is first event of game.
		if self.rts_play_sequence == 0 and self.comment_before is None:
			self.comment_before = parsed_line['comment']
		elif self.rts_play_sequence == 0 and self.comment_before:
			self.comment_before = self.comment_before + ' ' + parsed_line['comment']
		
		# Most comments fit this category.
		if self.rts_play_sequence > 0 and self.comment_after is None:
			self.comment_after = parsed_line['comment']
		elif self.rts_play_sequence > 0 and self.comment_after:
			self.comment_after = self.comment_after + ' ' + parsed_line['comment']	
		
		return {'ginfo': self.ginfo, 'pbp': self.pbp, 'starters': self.starters}
	
	def add_none(self, play_id):
		"""Add None(s) in otherwise unfilled fields"""
		
		pbp_keys = ['game_id', 'player_id', 'rts_play_sequence', 'play_type', 'inning', 'bottom_inning', 'rts_pitch_count', 'rts_pitch_sequence', 'play_meta', 'sub_batting_order', 'sub_field_position', 'comment']
		
		for key in pbp_keys:
			if key not in play_id.keys():
				play_id[key] = None
