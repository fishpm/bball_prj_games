import glob
import re
import os
import csv

class YearSummary(object):
	
	def __init__(self, year_start, year_finish):
		
		# Starting year
		self.year_start = year_start
		# Ending year
		self.year_finish = year_finish
		
		# Years are capped between these years.
		self.min_year = 1980
		self.max_year = 2014
		
		# Dictionary of players with data.
		self.players = {}

		# Does not appear to be used.  Delete?		
# 		self.ps = {}
		
		# Error dictionary for unexpected play-by-play events.
		self.err={'file': [], 'err': []}
		
		# Miscellaneous events skipped when reading play-by-play.
		self.non_batter_events = {
				"BK": 'balk', "CS": 'caught stealing',"DI": 'defensive indifference',
				"OA": 'misc baserunner advance',"PB": 'passed ball',"WP": 'wild pitch',
				"PO": 'picked off',"POCS": 'picked off charged with caught stealing',
				"SB": 'stolen base',"NP": 'Not a play (i.e., substitution or otherwise',
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
		
		# Filename output based on start and finish years.
		outname = "YearSummary"+str(self.year_start)+"_"+str(self.year_finish)+".csv"
		
		# If filename output already exists, over-write it.
		if os.path.isfile(outname):
			print 'Warning: over-writing', outname
			exist = 1
		else: exist = 0
		
		# Read through all play-by-play files for inclusive years.
		for y in range(self.year_start,self.year_finish+1):
			self.players = {}
			self.pbp_path = "/Users/patrickfisher/Documents/mlb/retrosheet/pbp/"+str(y)+"*.EV*"
			self.roster = "/Users/patrickfisher/Documents/mlb/retrosheet/pbp/*"+str(y)+".ROS"
		
			# For each team file for each inclusive year...
			for file in glob.glob(self.pbp_path):
				with open(file,'r') as f:
					
					print "Working on",file
					
					# For each line a team file for a given year...
					for line in f:
						
						# 'play' indicates a game event occurs. Read this line.
						if line.startswith('play'):
							parts = line.split(',')
							# Check that 'play' is a "batter event" and whether the playerID has already been added.
							if all([parts[3] not in self.players.keys(), not any(event in parts[6] for event in self.non_batter_events.keys())]):
								
								# Add playerID for given year if it does not already exist.
								self.players[parts[3]] = {'Year': y, 'PA': 0,"AB": 0,"H": 0,"S": 0,"D": 0,"T": 0,"HR": 0,
								"BB": 0,"K": 0,"HP":0,"IBB": 0,"TB": 0,"AVG": 0.0,"OBP": 0.0,"SLG": 0.0,
								"OPS":0,"ROE":0,"FC":0,"SF":0,"SH":0}
								
								# Read 'play' event and update playerID stats.
								self.event_check(parts[3],parts[6],self.players)
							
							# If playerID entry already exists, simply update playerID stats.
							elif all([not any(event in parts[6] for event in self.non_batter_events.keys())]):
								self.event_check(parts[3],parts[6],self.players)
					
					print 'Done with', file
			
			# Read roster file to get additional player info.
			for file in glob.glob(self.roster):
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
			
			# List of all playerIDs.
			pk = self.players.keys()
			
			# Update .csv file.
			print "Updating", outname
			with open(outname,'a') as csvfile:
				# Fieldnames in .csv are statistical categories and player info recorded for each player.
				fnames = self.players[pk[0]].keys()
				writer = csv.DictWriter(csvfile,fieldnames = fnames)
				if os.stat(outname).st_size == 0:
					print "Header written!"
					writer.writeheader()
				
				for name in pk:
					writer.writerow(self.players[name])
			
			print "Finished updating",outname
		
		return self.players
	
	
	def event_check(self,p3,p6,dict):
		
		""" Extract event information from a line of play-by-play data. """
		
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


a = YearSummary(1980,2014)
b = a.season_extract()