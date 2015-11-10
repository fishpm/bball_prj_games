import glob
import re
import os
import csv
import numpy

class YearSummary(object):
	
	def __init__(self, year_start, year_finish=None):
		
		# Starting year
		self.year_start = year_start
		# Ending year
		if not year_finish:
			self.year_finish = year_start
		else: self.year_finish = year_finish
		
		self.top_path = '/Users/patrickfisher/Documents/mlb/retrosheet/'
		
		# Warnings encountered.
		self.warn = []
		
		# Possible years bounded by these years.
		self.min_year = 1980
		self.max_year = 2014
		
		# Miscellaneous events skipped when reading play-by-play.
		self.non_batter_events = {
				"BK": 'balk', 
				"CS": 'caught stealing',
				"DI": 'defensive indifference',
				"OA": 'misc baserunner advance',
				"PB": 'passed ball',
				"WP": 'wild pitch',
				"PO": 'picked off',
				"POCS": 'picked off charged with caught stealing',
				"SB": 'stolen base',
				"NP": 'Not a play (i.e., substitution or otherwise',
				"FLE": 'Fielding error on foul ball (i.e., foul ball)'}
		
		# Make sure years entries are valid.
		try:
			int(self.year_start)
			all([self.year_start >= self.min_year, self.year_start <= self.max_year])
		except ValueError: 
			print self.year_start, "is an invalid start year.  Choose year between %d and %d" % (self.min_year, self.max_year)

		try:
			int(self.year_finish)
			all([self.year_finish >= self.min_year, self.year_finish <= self.max_year])
		except ValueError: 
			print self.year_finish, "is an invalid finish year.  Choose year between %d and %d" % (self.min_year, self.max_year)
		
	
	def season_extract(self):
	
		""" Reads play-by-play files for a given year and return a dictionary with player id and assorted stats from that year."""
		
		# Dictionary of players with data.
		self.players = {}
		self.players_std = {}
		
		# Error dictionary for unexpected play-by-play events.
		self.err={'file': [], 'err': []}

		# Filename output based on start and finish years.
		outname = "YearSummary" + str(self.year_start) + "_" + str(self.year_finish) + ".csv"
		
		# If filename output already exists, remove it.
		if os.path.isfile(outname):
			print 'Warning: over-writing', outname
			os.remove(outname)
		
		# Read through all play-by-play files for inclusive years.
		for y in range(self.year_start, self.year_finish + 1):
			self.players = {}
			self.year_pbp_path = self.top_path + "pbp/" + str(y) + "*.EV*"
			self.year_roster = self.top_path + "pbp/*" + str(y) + ".ROS"
		
			# For each team file, for each inclusive year...
			for file in glob.glob(self.year_pbp_path):
				with open(file,'r') as f:
					
					print "Working on",file
					
					# For each line in a team file for a given year...
					for line in f:
						
						# 'play' indicates a game event occurs. Read this line.
						if line.startswith('play'):
							parts = line.split(',')
							# If a new playerID for current year (not in self.players{}) and the 'play' is a "batter event"...
							if all([parts[3] not in self.players.keys(), not any(event in parts[6] for event in self.non_batter_events.keys())]):
								
								# Add playerID for the current year.
								self.players[parts[3]] = {
								'Year': y, 
								'PA': 0,
								"AB": 0,
								"H": 0,
								"S": 0,
								"D": 0,
								"T": 0,
								"HR": 0,
								"BB": 0,
								"K": 0,
								"HP":0,
								"IBB": 0,
								"TB": 0,
								"AVG": 0.0,
								"OBP": 0.0,
								"SLG": 0.0,
								"OPS":0,
								"ROE":0,
								"FC":0,
								"SF":0,
								"SH":0}
								
								# Read 'play' event and update playerID stats.
								self.event_check(parts[3],parts[6],self.players)
							
							# If playerID already exists in self.players{} for current year, update playerID stats.
							elif all([not any(event in parts[6] for event in self.non_batter_events.keys())]):
								self.event_check(parts[3],parts[6],self.players)
					
					print 'Done with', file
			
# 			Read roster file for additional player info (e.g., name, team and playerID).
			for file in glob.glob(self.year_roster):
				with open(file,'r') as f:
# 					print "Adding names to",file
					for line in f:
						parts = line.split(',')
						if parts[0] in self.players.keys():
							self.players[parts[0]]['last_name'] = parts[1]
							self.players[parts[0]]['first_name'] = parts[2]
							self.players[parts[0]]['team'] = parts[5]
							self.players[parts[0]]['id'] = parts[0]
					print "Finished adding names to",file
			
# 			List of all playerIDs.
			pk = self.players.keys()
			
			for name in pk:
				self.players_std[name] = {'Year': y, 'S': 0.0, 'D': 0.0, 'T': 0.0, 'HR': 0.0, 'BB': 0.0, 'K': 0.0, 'HP': 0.0: 'IBB': 0.0, 'AVG': 0.0, 'SLG': 0.0, 'OPS': 0.0}
				
				l = [b[name]['S']/float(b[name]['PA']) for name in b.keys()]
				(l - mean(l))/std(l) 
				
				if sum([b[name]['PA'] for name in b.keys()]):
					self.players_std[name]['S'] = sum([b[name]['S'] for name in b.keys()])/float(sum([b[name]['PA'] for name in b.keys()]))
					
					self.players_std[name]['D'] = sum([b[name]['D'] for name in b.keys()])/float(sum([b[name]['PA'] for name in b.keys()]))
					
					self.players_std[name]['T'] = sum([b[name]['T'] for name in b.keys()])/float(sum([b[name]['PA'] for name in b.keys()]))
				
				}
			
# # 			Update .csv file with season information for each player, for each year.
# 			print "Updating", outname
# 			with open(outname,'a') as csvfile:
# # 				Fieldnames in .csv are keys from self.players{}.
# 				fnames = self.players[pk[0]].keys()
# 				writer = csv.DictWriter(csvfile, fieldnames = fnames)
# 				if os.stat(outname).st_size == 0:
# 					print "Header written!"
# 					writer.writeheader()
# 				
# 				for name in pk:
# 					writer.writerow(self.players[name])
# 			
# 			print "Finished updating",outname
# 		
		return self.players
	
	
	def event_check(self,p3,p6,dict):
		
		""" Extract event information from a line of play-by-play data. """
		"""
		p3 = playerID
		p6 = type of 'play' event
		dict = dictionary to be updated.
		"""
		
		
		# Outs attributed to fielders
		if re.search('^[0-9]',p6):
			dict[p3]["PA"] += 1	
			dict[p3]["AB"] += 1
		# Single
		elif p6.startswith('S'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["S"] += 1
		# Strikeout
		elif p6.startswith('K'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["K"] += 1
		# Double
		elif p6.startswith('D'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["D"] += 1
		# Home-run
		elif p6.startswith('HR'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["HR"] += 1
		# Walk
		elif p6.startswith('W'):
			dict[p3]["PA"] += 1
			dict[p3]["BB"] += 1
		# Intentional walk
		elif p6.startswith('IW'):
			dict[p3]["PA"] += 1
			dict[p3]["BB"] += 1
			dict[p3]["IBB"] += 1
		# Triple
		elif p6.startswith('T'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["T"] += 1
		# Error
		elif p6.startswith('E'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["ROE"] += 1
		# Fielder's choice
		elif p6.startswith('FC'):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
		# Hit-by-pitch
		elif p6.startswith('HP'):
			dict[p3]["PA"] += 1
			dict[p3]["HP"] += 1
		# Catcher interference.
		elif re.search('^C',p6):
			dict[p3]["PA"] += 1
		# If none of these, send to error dictionary.
		else:
			self.err['file'].append(file)
			self.err['file'].append(p6)
		
		# If sacrifice fly
		if re.search('SF',p6):
			dict[p3]["PA"] += 1
			dict[p3]["SF"] += 1
		# If sacrifice hit
		elif re.search('SH',p6):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["H"] += 1
			dict[p3]["SH"] += 1
	
		# Hits are sum of singles, double, triples and homers.
		dict[p3]["H"] = dict[p3]["S"] + dict[p3]["D"] + dict[p3]["T"] + dict[p3]["HR"]
		
		# Total bases are "weighted hits".
		dict[p3]["TB"] = dict[p3]["S"] + dict[p3]["D"]*2 + dict[p3]["T"]*3 + dict[p3]["HR"]*4
		
		# Calculate batting average if there is at least one AB (otherwise denominator is 0)
		if dict[p3]["AB"]:
			dict[p3]["AVG"] = float(format(float(dict[p3]["H"])/dict[p3]["AB"],'0.3f'))
			dict[p3]["SLG"] = float(format(float(dict[p3]["TB"])/dict[p3]["AB"],'0.3f'))
		
		# Calculate on-base percentage if one of AB, BB, HP or SF has occurred (otherwise denominator is 0)
		if (dict[p3]["AB"]+ dict[p3]["BB"] + dict[p3]["HP"] + dict[p3]["SF"]):
			dict[p3]["OBP"] = float(format((float(dict[p3]["H"]) + dict[p3]["BB"] + dict[p3]["HP"])/(dict[p3]["AB"]+ dict[p3]["BB"] + dict[p3]["HP"] + dict[p3]["SF"]),'0.3f'))
		# On-base plus slugging.
		dict[p3]["OPS"] = float(format(dict[p3]["OBP"] + dict[p3]["SLG"],'0.3f'))
	
	def game_log(self,y=None):
		"""Read game logs for winner/loser status. """
		"""
		y = year on which game_log will be determined.
		"""
		
		self.glog = {}
		
		if not y:
			self.glog_file = self.top_path + "game_logs/GL" + str(self.year_start) + ".txt"
		else: 
			try:
				int(y)
				all([y >= self.min_year, y <= self.max_year])
				self.glog_file = self.top_path + "game_logs/GL" + str(y) + ".txt"
			except ValueError:
				print str(y), "is an invalid start year.  Choose year between %d and %d" % (self.min_year, self.max_year)
		
		for file in glob.glob(self.glog_file):
			with open(file,'r') as f:
				print 'Reading game logs for', file
				for line in f:
					parts = line.split(',')
					game_id = parts[0].strip('"') + parts[1].strip('"') + parts[6].strip('"')
					if parts[10] > parts[9]:
						self.glog[game_id] = {'game_id': game_id, 'winner': 'home'}
					else: self.glog[game_id] = {'game_id': game_id, 'winner': 'away'}
		
		outname = 'GL' + str(y) + '.csv'
		
		games = self.glog.keys()
		# Update .csv file.
		with open(outname,'a') as csvfile:
			# Fieldnames in .csv are statistical categories and player info recorded for each player.
			fnames = self.glog[games[0]].keys()
			writer = csv.DictWriter(csvfile, fieldnames = fnames)
			if os.stat(outname).st_size == 0:
				writer.writeheader()
			
			for name in games:
				writer.writerow(self.glog[name])
	
	
	def order_games(self,y=None):
		"""Reads game dates from all teams to create a chronologically
		ordered schedule."""
		"""
		y = year on which order_games will be determined.
		"""
		
		self.glist = {}
		if not y:
			self.year_pbp_path = self.top_path + "pbp/" + str(self.year_start) + "*.EV*"
		else: 
			try:
				int(y)
				all([y >= self.min_year, y <= self.max_year])
				self.year_pbp_path = self.top_path + "pbp/" + str(y) + "*.EV*"
			except ValueError:
				print str(y), "is an invalid start year.  Choose year between %d and %d" % (self.min_year, self.max_year)
		
		# For each play-by-play file...
		for file in glob.glob(self.year_pbp_path):
			with open(file,'r') as f:
				print "Working on",file
				for line in f:
					# 'id' line includes data information and clarifies order of double-headers.
					if line.startswith('id'):
						nline = line.rstrip()
						parts = nline.split(',')
						self.glist[parts[1][3:]+parts[1][0:3]] = []
					else: 
						self.glist[parts[1][3:]+parts[1][0:3]].append(line)
		
		# Sorts are recorded information by game, which is ordered chronologically. Keys are game IDs and values are game information.
  		return self.glist
	
	def utd_stats(self):
		""" Creates a running set of up-to-date statistics for each player. Stats are fed into dictionary organized by batting order at start of a given game. """
		
		if self.year_start != self.year_finish:
			print "Looping through %d and %d" % (self.year_start, self.year_finish)
		
		for y in range(self.year_start, self.year_finish+1):
			
			self.order_games(y)
			self.game_log(y)
			self.g = {}
			self.utd = {}
			self.ctd = {}
			
			# Used to sort home and away teams.
			v1 = ['a','h']
			outname = 'UTD_' + str(y) + '.csv'
			
			# If filename output already exists, remove it.
			if os.path.isfile(outname):
				print 'Warning: over-writing', outname
				os.remove(outname)
		
			# Consider each game (chronologically ordered) in season.
			sk = sorted(self.glist.keys())
		
			# For each game (chronologically ordered) in season...
			for game in sk:
			
				# Save game ID.
				self.g[game] = {}
				self.g[game]['game'] = game
				print game
			
				# For each line of game information within a given game...
				for line in self.glist[game]:
					# Save game date information.
					if line.startswith('info,date,'):
						parts = line.split(',')
						self.g[game]['date'] = parts[2].rstrip()
				
					# Save home team name information.
					elif line.startswith('info,hometeam,'):
						parts = line.split(',')
						self.g[game]['hteam'] = parts[2].rstrip()
				
					# Save away team name information.
					elif line.startswith('info,visteam,'):
						parts = line.split(',')
						self.g[game]['ateam'] = parts[2].rstrip()
				
					# Save information about starting players.
					elif line.startswith('start'):
						parts = line.split(',')
					
						# If new player ID is encountered, add it to utd (up-to-date) dictionary.
						if parts[1] not in self.utd.keys():
	# 						print "First starter entry for",parts[1]
							self.utd[parts[1]] = {'Year': y, 
							'G': 1, 
							'PA': 0,
							"AB": 0,
							"H": 0,
							"S": 0,
							"D": 0,
							"T": 0,
							"HR": 0,
							"BB": 0,
							"K": 0,
							"HP":0,
							"IBB": 0,
							"TB": 0,
							"AVG": 0.0,
							"OBP": 0.0,
							"SLG": 0.0,
							"OPS":0,
							"ROE":0,
							"FC":0,
							"SF":0,
							"SH":0}
						
							# For each new player ID, read career information into another dictionary that can be repeatedly accessed whenever this player re-appears throughout the season.
							self.career_to_date(parts[1],y)
						
							# Pitchers in AL do not bat. parts[4] here is batting order.
							if parts[4] != '0':
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_id"] = parts[1]
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_obp"] = self.ctd[parts[1]]['OBP']
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_slg"] = self.ctd[parts[1]]['SLG']
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_ops"] = self.ctd[parts[1]]['OPS']
					
						# If player ID already exists, evaluate whether information should be added.
						else:
						
							# Pitchers in AL do not bat. parts[4] here is batting order.
							if parts[4] != '0':
								# Increment games played.
								self.utd[parts[1]]['G'] += 1
							
								# Add player ID to appropriate batting order position.
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_id"] = parts[1]
							
								# If the player has recorded ABs, compute SLG.
								if self.ctd[parts[1]]['AB'] or self.utd[parts[1]]['AB']:
									num = self.ctd[parts[1]]['TB'] + self.utd[parts[1]]['TB']
									denom = self.ctd[parts[1]]['AB'] + self.utd[parts[1]]['AB']
									frac = float(format(float(num)/denom,'0.3f'))
								
									# Add SLG to appropriate batting order position.
									self.g[game][v1[int(parts[3])]+str(parts[4])+"_slg"] = frac								
							
								else:
									# If player has 0 historical ABs, set SLG to 0.0
									# THIS SHOULD BE MODIFIED BECAUSE THIS IS A BAD PREDICTION.
									self.g[game][v1[int(parts[3])]+str(parts[4])+"_slg"] = 0.0
							
								# If the player has an AB, BB, HP or SF, compute OBP.
								if self.ctd[parts[1]]['AB'] or self.utd[parts[1]]['AB'] or self.ctd[parts[1]]['BB'] or self.utd[parts[1]]['BB'] or self.ctd[parts[1]]['HP'] or self.utd[parts[1]]['HP'] or self.ctd[parts[1]]['SF'] or self.utd[parts[1]]['SF']:
									num = self.utd[parts[1]]['H'] + self.utd[parts[1]]['BB'] + self.utd[parts[1]]['HP'] + self.ctd[parts[1]]['H'] + self.ctd[parts[1]]['BB'] + self.ctd[parts[1]]['HP']
									denom = self.utd[parts[1]]['AB'] + self.utd[parts[1]]['BB'] + self.utd[parts[1]]['HP'] + self.utd[parts[1]]['SF'] + self.ctd[parts[1]]['AB'] + self.ctd[parts[1]]['BB'] + self.ctd[parts[1]]['HP'] + self.ctd[parts[1]]['SF']
									frac = float(format(float(num)/denom,'0.3f'))
								
									# Add OBP to appopriate batting order position.
									self.g[game][v1[int(parts[3])]+str(parts[4])+"_obp"] = frac
								
								else:
									# If player has 0 historical AB, BB, HP or SF, set OBP to 0.0
									# THIS SHOULD BE MODIFIED BECAUSE THIS IS A BAD PREDICTION.
									self.g[game][v1[int(parts[3])]+str(parts[4])+"_obp"] = 0.0
							
								# Sum the SLG and OBP that were added to compute OPS.
								self.g[game][v1[int(parts[3])]+str(parts[4])+"_ops"] = float(format(self.g[game][v1[int(parts[3])]+str(parts[4])+"_slg"] + self.g[game][v1[int(parts[3])]+str(parts[4])+"_obp"],'0.3f'))
				
					# Read play-by-play information to make up-to-date dictionary accurate.
					elif line.startswith('play'):
						parts = line.split(',')
					
						# If player ID not in utd dictionary, add it.  This can happen here is new player enters via pinch-hitting or injury, mid game.
						if all([parts[3] not in self.utd.keys(), not any(event in parts[6] for event in self.non_batter_events.keys())]):
	# 						print "First game entry for",parts[3]
							self.utd[parts[3]] = {'Year': y, 'G': 1, 'PA': 0,"AB": 0,"H": 0,"S": 0,"D": 0,"T": 0,"HR": 0,
								"BB": 0,"K": 0,"HP":0,"IBB": 0,"TB": 0,"AVG": 0.0,"OBP": 0.0,"SLG": 0.0,
								"OPS":0,"ROE":0,"FC":0,"SF":0,"SH":0}
						
							# For each new player ID, read career information into another dictionary that can be repeatedly accessed whenever this player re-appears throughout the season.
							self.career_to_date(parts[3],y)
						
							# Read play event to update up-to-date dictionary
							self.event_check(parts[3],parts[6],self.utd)
							
						# If player ID already exists, read play event to update up-to-date dictionary.
						elif all([not any(event in parts[6] for event in self.non_batter_events.keys())]):
	# 						print "Updating game entry for",parts[3]
							self.event_check(parts[3],parts[6],self.utd)
				
			# List of all playerIDs.
			gkeys = self.g.keys()
		
			# Update .csv file.
			print "Updating", outname
			with open(outname,'a') as csvfile:
				# Fieldnames in .csv are statistical categories and player info recorded for each player.
				fnames = self.g[gkeys[0]].keys()
				writer = csv.DictWriter(csvfile,fieldnames = fnames)
				if os.stat(outname).st_size == 0:
					print "Header written!"
					writer.writeheader()
			
				for name in gkeys:
					writer.writerow(self.g[name])
		
			print "Finished updating",outname

			# Return up-to-date dictionary and g dictionary, which is starting player information for each game.
 			# return {'utd': self.utd, 'g': self.g}
	
	def career_to_date(self, id, y):
		""" Read exists yearly summary info file to determine player statistics up to the year before the one being evaluated. """
		"""
		id = playerID
		y = year on which career_to_date will be determined.
		"""
		
		# If player ID not already added, initialize values.
		if id not in self.ctd.keys():
			self.ctd[id] = {'TB': 0, 'AB': 0, 'H': 0, 'BB': 0, 'HP': 0, 'SF': 0, 'SLG': 0.0, 'OBP': 0.0, 'OPS': 0.0}
			# Years in league counter
			c = 0
			
			# Read previously created file.
			yname = 'YearSummary%s_%s.csv' % (str(self.year_start), str(self.year_finish))
			with open(yname) as csvfile:
				r = csv.DictReader(csvfile)
				
				# For each row...
				for row in r:
					# If row ID matches player ID and year is before current year.
					if row['id'] == id and int(row['Year']) < y:
						c += 1
						
						if int(row['Year']) == self.min_year:
							print 'temp'
							self.warn.append('Entry for %s found from %s, expand YearSummary to avoid truncating data included.' % (id, self.min_year))
						
						# Update info in ctd (career-to-date) dictionary.
						self.ctd[id]['TB'] += int(row['TB'])
						self.ctd[id]['AB'] += int(row['AB'])
						self.ctd[id]['H'] += int(row['H'])
						self.ctd[id]['BB'] += int(row['BB'])
						self.ctd[id]['HP'] += int(row['HP'])
						self.ctd[id]['SF'] += int(row['SF'])
						
						# If AB, compute SLG
						if self.ctd[id]['AB']:
							self.ctd[id]['SLG'] = float(format(float(self.ctd[id]['TB'])/self.ctd[id]['AB'],'0.3f'))
						
						# Otherwise, historical SLG is 0.0
						else: self.ctd[id]['SLG'] = 0.0
						
						# If AB, BB, HP or SF, compute OBP
						if self.ctd[id]['AB'] or self.ctd[id]['BB'] or self.ctd[id]['HP'] or self.ctd[id]['SF']:
							self.ctd[id]['OBP'] = float(format((float(self.ctd[id]['H']) + self.ctd[id]['BB'] + self.ctd[id]['SF'])/(float(self.ctd[id]['AB']) + self.ctd[id]['BB'] + self.ctd[id]['SF'] + self.ctd[id]['HP']),'0.3f'))
						
						# Otherwise, historical OBP is 0.0
						else: self.ctd[id]['OBP'] = 0.0
						
						# OPS = OBP + SLG
						self.ctd[id]['OPS'] = float(format(self.ctd[id]['SLG'] + self.ctd[id]['OBP'],'0.3f'))
						
				# Notification of a rookie!
				if c == 0:
					print "%s not found! ROOKIE BIATCH!" % id
				else: print 'CTD complete for %s with %d years included.' % (id, c)