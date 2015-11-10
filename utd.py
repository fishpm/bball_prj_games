# Where no ABs exist, observed SLG is "0.0".  This seems like a bad player estimate. Change somehow.

import glob
import re
import os
import csv

class YearGames(object):
	
	def __init__(self,year_start):
		
		"""Takes input of year from which data will be extracted."""
		
		# Year from which up-to-date info will be drawn.
		self.year_start = year_start
		
		# Game list. Dictionary games played within current year.
		self.glist = {}
		
		# Up-to-date stats. Running record of stats from current season for each player.
		self.utd = {}
		
		# Error dictionary for unexpected play-by-play events.
		self.err = {}
		self.err['file'] = []
		
		# Summary info for each starter at beginning of each game. Info to be feed into predictive model.
		self.g = {}
		
		# Career-to-date. Preceding years totals for players in current season.
		self.ctd = {}
		
		# Game log dictionary.
		self.glog = {}
		
		# Min and max allowed years.
		self.min_year = 1980
		self.max_year = 2014
		
		# Miscellaneous events skipped when reading play-by-play.
		self.non_batter_events = {
				"BK": 'balk', "CS": 'caught stealing',"DI": 'defensive indifference',
				"OA": 'misc baserunner advance',"PB": 'passed ball',"WP": 'wild pitch',
				"PO": 'picked off',"POCS": 'picked off charged with caught stealing',
				"SB": 'stolen base',"NP": 'Not a play (i.e., substitution or otherwise',
				"FLE": 'Fielding error on foul ball (i.e., foul ball)'}
		
		# Play-by-play and roster files for current season.
		self.pbp_path = "/Users/patrickfisher/Documents/mlb/retrosheet/pbp/"+str(self.year_start)+"*.EV*"
		self.roster = "/Users/patrickfisher/Documents/mlb/retrosheet/pbp/*"+str(self.year_start)+".ROS"
		self.glog_file = "/Users/patrickfisher/Documents/mlb/retrosheet/game_logs/GL"+str(self.year_start)+".txt"
		
		# Make sure year entry is valid.
		try:
			int(self.year_start)
			all([self.year_start >= self.min_year, self.year_start <= self.max_year])
		except ValueError: 
			print self.year_start, "is an invalid start year.  Choose year between %d and %d" % (self.min_year, self.max_year)
	
	def game_log(self):
		"""Read game logs for winner/loser status. """
		
		for file in glob.glob(self.glog_file):
			with open(file,'r') as f:
				for line in f:
					parts = line.split(',')
					game_id = parts[0].strip('"') + parts[1].strip('"') + parts[6].strip('"')
					if parts[10] > parts[9]:
						self.glog[game_id] = {'game_id': game_id, 'winner': 'home'}
					else: self.glog[game_id] = {'game_id': game_id, 'winner': 'away'}
		
		outname = 'GL' + str(self.year_start) + '.csv'
		
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
	
	
	def order_games(self):
		"""Reads game dates from all teams to create a chronologically
		ordered schedule."""
		
		# For each play-by-play file...
		for file in glob.glob(self.pbp_path):
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
	
	def update_stats(self):
		""" Creates a running set of up-to-date statistics for each player. Stats are fed into dictionary organized by batting order at start of a given game. """

		# Used to sort home and away teams.
		v1 = ['a','h']
		outname = 'UTD_' + str(self.year_start) + '.csv'
		
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
						self.utd[parts[1]] = {'Year': self.year_start, 'G': 1, 'PA': 0,"AB": 0,"H": 0,"S": 0,"D": 0,
						"T": 0,"HR": 0,"BB": 0,"K": 0,"HP":0,"IBB": 0,"TB": 0,"AVG": 0.0,
						"OBP": 0.0,"SLG": 0.0,"OPS":0,"ROE":0,"FC":0,"SF":0,"SH":0}
						
						# For each new player ID, read career information into another dictionary that can be repeatedly accessed whenever this player re-appears throughout the season.
						self.career_to_date(parts[1],0)
						
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
						self.utd[parts[3]] = {'Year': self.year_start, 'G': 1, 'PA': 0,"AB": 0,"H": 0,"S": 0,"D": 0,"T": 0,"HR": 0,
							"BB": 0,"K": 0,"HP":0,"IBB": 0,"TB": 0,"AVG": 0.0,"OBP": 0.0,"SLG": 0.0,
							"OPS":0,"ROE":0,"FC":0,"SF":0,"SH":0}
						
						# For each new player ID, read career information into another dictionary that can be repeatedly accessed whenever this player re-appears throughout the season.
						self.career_to_date(parts[3],0)
						
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
		return {'utd': self.utd, 'g': self.g}
	
	def event_check(self,p3,p6,dict):
		""" Read through lines of pbp data and extract event information."""
		
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
		# Print event and read it into the error dictionary.
		else:
			print p6
			self.err['file'].append(p6)
		
		# Sac fly
		if re.search('SF',p6):
			dict[p3]["PA"] += 1
			dict[p3]["SF"] += 1
		# Sac hit
		elif re.search('SH',p6):
			dict[p3]["PA"] += 1
			dict[p3]["AB"] += 1
			dict[p3]["H"] += 1
			dict[p3]["SH"] += 1
	
		# Calculate total hits
		dict[p3]["H"] = dict[p3]["S"] + dict[p3]["D"] + dict[p3]["T"] + dict[p3]["HR"]
		
		# Total bases is weighted total hits.
		dict[p3]["TB"] = dict[p3]["S"] + dict[p3]["D"]*2 + dict[p3]["T"]*3 + dict[p3]["HR"]*4
		
		# If there is an AB, calculate AVG and SLG
		if dict[p3]["AB"]:
			dict[p3]["AVG"] = float(format(float(dict[p3]["H"])/dict[p3]["AB"],'0.3f'))
			dict[p3]["SLG"] = float(format(float(dict[p3]["TB"])/dict[p3]["AB"],'0.3f'))
		
		# If there is AB, BB, HP or SF, calculate OBP.
		if (dict[p3]["AB"]+ dict[p3]["BB"] + dict[p3]["HP"] + dict[p3]["SF"]):
			dict[p3]["OBP"] = float(format((float(dict[p3]["H"]) + dict[p3]["BB"] + dict[p3]["HP"])/(dict[p3]["AB"]+ dict[p3]["BB"] + dict[p3]["HP"] + dict[p3]["SF"]),'0.3f'))
		
		# OBP + SLG
		dict[p3]["OPS"] = float(format(dict[p3]["OBP"] + dict[p3]["SLG"],'0.3f'))
			
	def career_to_date(self, id, code):
		""" Read exists yearly summary info file to determine player statistics up to the year before the one being evaluated. """
		
		# If player ID not already added, initialize values.
		if id not in self.ctd.keys():
			self.ctd[id] = {'TB': 0, 'AB': 0, 'H': 0, 'BB': 0, 'HP': 0, 'SF': 0, 'SLG': 0.0, 'OBP': 0.0, 'OPS': 0.0}
			# Years in league counter
			c = 0
			
			# Read previously created file.
			with open('YearSummary1980_2014.csv') as csvfile:
				r = csv.DictReader(csvfile)
				
				# For each row...
				for row in r:
					# If row ID matches player ID and year is before current year.
					if row['id'] == id and int(row['Year']) < self.year_start:
						c += 1
						
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
				else: print 'CTD complete for %s with %d years included.' % (id,c)
		
		
for y in range(2012,2015):
	a = utd.YearGames(y)
	og = a.order_games()
	gl = a.game_log()
	us = a.update_stats()