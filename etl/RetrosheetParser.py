"""
Parse Retrosheet Data

Goal: turn data into relational tables
? Use python schematics for data validation
"""


class RetrosheetLineParser()


    def init(self):
        parser_map = {
                "id" : self.parse_id
                , "version" : self.version
                , "info": self.info
                , "start": self.start
                , "play": self.play
                , "sub": self.sub
                , "data": self.data
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
                , 'team' : team
                , 'year' : year
                , 'month' : month
                , 'day' : day
                , 'game_num' : game_num
                }
        return id_instance

    
    def parse_version(self, retro_list):
        "Parse the version type"
        pass


    def parse_info(self, retro_list):
        pass


    def parse_start(self, retro_list):
        "Parse the start type"
        pass


    def parse_play(self, retro_list):
        "Parse the play type"
        pass


    def parse_sub(self, retro_list):
        "Parse the sub type"
        pass


    def parse_data(self, retro_list):
        "Parse the retrodata 'data' type"
        pass
