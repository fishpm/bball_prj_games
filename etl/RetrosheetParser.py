"""
Parse Retrosheet Data

Goal: turn data into relational tables
? Use python schematics for data validation
"""


class RetrosheetLineParser()


    def init(self):
        parser_map = {
                "id" : self.parse_id
                , "version" : self.parse_version
                , "info": self.parse_info
                , "start": self.parse_start
                , "play": self.parse_play
                , "sub": self.parse_sub
                , "data": self.parse_data
                , "com": self.com
                }
        
        info_types = ['visteam', 'hometeam', 'site', 'date', 'number', 'starttime', 'daynight', 'usedh', 'umphome', 'ump1b', 'ump2b', 'ump3b', 'howscored', 'pitches', 'temp', 'winddir', 'windspeed', 'fieldcond', 'precip', 'sky', 'timeofgame', 'attendance', 'wp', 'lp', 'save', 'gwrbi']
        
        play_types = tuple(['S', 'K', 'D', 'H', 'W', 'IW', 'T', 'E', 'FC', 'HP', 'C', 'NP'] + map(str,range(1,10)))


    def type_parser(self, retro_list, parser_map):
        "Read the type and pass to the appropriate parser"
        retro_type = retro_list[0]
        if parser_map.has_key(retro_type):
            parser = self.parser_map[retro_type]
            type_parsed = parser(retro_list)
            return type_parsed
        else:
            # TODO: Replace with logger
            print("Unknown retrosheet data type: %s. Skipping" % (retro_type))
        return None 


    def parse_id(self, retro_list):
        "Parse the id type"
        game_id = retro_list[1]
        team = game_id[0:2]       
        year = game_id[3:6]
        month = game_id[7:8]
        day = game_id[9:10]
        game_num = game_id[11]
        id_instance = {
                'game_id' : game_id
                , 'team': team
                , 'year' : year
                , 'month' : month
                , 'day' : day
                , 'game_num' : game_num
                }
        return id_instance
        
#         # Why not this? Is it more an aesthetic than a practical thing?
#         id_instance = {
#                 'game_id' : retro_list[1]
#                 , 'team': retro_list[1][:2]
#                 , 'year' : retro_list[1][3:6]
#                 , 'month' : retro_list[1][7:8]
#                 , 'day' : retro_list[1][9:10]
#                 , 'game_num' : retro_list[1][11]
#                 }
    
    def parse_version(self, retro_list):
        "Parse the version type"
        pass


    def parse_info(self, retro_list):
    	"Parse the info type"
    	# We don't need to read all "info" rows. For example, an "info" row repeats the game date, which is already collected from "id".  There are other random "info" types that are not particularly relevant.
    	if retro_list[1] in self.info_types:
	    	info_instance = {retro_list[1]: retro_list[2]}
	    return info_instance


    def parse_start(self, retro_list):
        "Parse the start type"
        player_instance = {
        		'player_id': retro_list[1]
        		, 'player_name': retro_list[2]
        		, 'player_team': retro_list[3]
        		, 'batting_order': retro_list[4]
        		, 'def_position': retro_list[5]
        		}
        return player_instance


    def parse_play(self, retro_list):
        "Parse the play type"
        if retro_list[6].startswith(self.play_types):
        	# If starts with '99' then play unknown.
        	if retro_list[6].startswith('99'):
        		pass
        	else:
        		pass


    def parse_sub(self, retro_list):
        "Parse the sub type"
        pass


    def parse_data(self, retro_list):
        "Parse the retrodata 'data' type"
        pass
