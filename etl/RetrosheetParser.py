"""
Parse Retrosheet Data

Goal: turn data into relational tables
? Use python schematics for data validation
"""


class RetrosheetLineParser(object):


    def __init__(self):
        parser_map = {
                "id" : self.parse_id
                , "version" : self.parse_version
                , "info": self.parse_info
                , "start": self.parse_start
                , "play": self.parse_play 
                , "sub": self.parse_sub
                , "data": self.parse_data
                , "com": self.com
                , "ladj": self.parse_ladj
                , "badj": self.parse_badj
                , "padj": self.parse_padj
                }
        

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
        
    
    def parse_version(self, retro_list):
        "Parse the version type"
        # Indicated on retrosheet.org that the version record is obsolete.
        pass


    def parse_info(self, retro_list):
    	"Parse the info type"
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
        "Parse the play type with respect to the play_by_play table"
        play_instance = {
                'inning': retro_list[1]
                , 'home_team': retro_list[2]
                , 'rts_player_id': retro_list[3]
                , 'rts_pitch_count': retro_list[4]
                , 'rts_pitch_seq': retro_list[5]
                , 'play_meta': retro_list[6]
                }
        return play_instance


    def parse_sub(self, retro_list):
        "Parse the sub type"
        sub_instance = {
        		'player_id': retro_list[1]
        		, 'player_name': retro_list[2]
        		, 'player_team': retro_list[3]
        		, 'batting_order': retro_list[4]
        		, 'def_position': retro_list[5]
        		}
        return sub_instance


    def parse_data(self, retro_list):
        "Parse the 'data' type"
        data_instance = {
        		'player_id': retro_list[2]
        		, 'earned_runs': retro_list[3]
        		}


    def parse_ladj(self, retro_list):
    	"Parse the ladj type, also know as BOOT"
    	ladj_instance = {
    			'team': retro_list[1]
    			, 'batting_order': retro_list[2]
                }
        return ladj_instance


    def parse_badj(self, retro_list):
    	"Parse the badj type"
    	badj_instance = {
    			'player_id': retro_list[1]
    			, 'badj_note': retro_list[2]
    			}
        return badj_instance
   

    def parse_padj(self, retro_list):
    	"Parse the padj type"
    	padj_instance = {
    			'player_id': retro_list[1]
    			, 'padj_note': retro_list[2]
    			}
        return padj_instance


    def parse_com(self, retro_list):
        return {'comment':retro_list[1]}
