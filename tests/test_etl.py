from etl.RetrosheetParser import RetrosheetLineParser
import csv
import itertools

def test_parse_id():
    rsp = RetrosheetLineParser()
    retro_list = ['id','DET198204150']
    id_map = rsp.parse_id(retro_list)
    print(id_map)
    assert(all([id_map['team'] == 'DET',
        id_map['year'] == '1982',
        id_map['month'] == '04',
        id_map['day'] == '15',
        id_map['game_num'] == '0'
        ]))


def test_parse_info():
    rsp = RetrosheetLineParser()
    retro_list = ['info','hometeam','COL']
    id_map = rsp.parse_info(retro_list)
    print(id_map)
    assert(id_map['hometeam'] == 'COL')


def test_parse_start():
	rsp = RetrosheetLineParser()
	retro_list = ['start','utlec001','"Chase Utley"','0','3','4']
	id_map = rsp.parse_start(retro_list)
	print(id_map)
	assert(all([id_map['player_id'] == 'utlec001', 
		id_map['player_name'] == '"Chase Utley"', 
		id_map['player_team'] == '0', 
		id_map['batting_order'] == '3', 
		id_map['field_position'] == '4'
		]))


def test_parse_play():
	rsp = RetrosheetLineParser()
	retro_list = ['play','1','1','spilr001','12','>B.SFX','FC6/G.2X3(65)']
	id_map = rsp.parse_play(retro_list)
	print(id_map)
	assert(all([id_map['inning'] == '1', 
		id_map['home_team'] == '1', 
		id_map['player_id'] == 'spilr001', 
		id_map['rts_pitch_count'] == '12',
		id_map['rts_pitch_seq'] == '>B.SFX',
		id_map['play_meta'] == 'FC6/G.2X3(65)'
		]))


def test_parse_sub():
	rsp = RetrosheetLineParser()
	retro_list = ['sub','happj001','"J.A. Happ"','0','7','1']
	id_map = rsp.parse_sub(retro_list)
	print(id_map)
	assert(all([id_map['player_id'] == 'happj001', 
		id_map['player_name'] == '"J.A. Happ"', 
		id_map['player_team'] == '0', 
		id_map['batting_order'] == '7',
		id_map['field_position'] == '1'
		]))


def test_parse_data():
	rsp = RetrosheetLineParser()
	retro_list = ['data','er','durbc001','3']
	id_map = rsp.parse_data(retro_list)
	print(id_map)
	assert(all([id_map['player_id'] == 'durbc001', 
		id_map['earned_runs'] == '3'
		]))


def test_parse_ladj():
	pass


def test_parse_badj():
	rsp = RetrosheetLineParser()
	retro_list = ['badj','rodrw002','R']
	id_map = rsp.parse_badj(retro_list)
	print(id_map)
	assert(all([id_map['player_id'] == 'rodrw002',
		id_map['badj_note'] == 'R'
		]))


def test_parse_padj():
	rsp = RetrosheetLineParser()
	retro_list = ['padj','harrg001','L']
	id_map = rsp.parse_padj(retro_list)
	print(id_map)
	assert(all([id_map['player_id'] == 'harrg001',
		id_map['padj_note'] == 'L'
		]))


def test_parse_com():
	rsp = RetrosheetLineParser()
	retro_list = ['com',"Rockies first baseman Todd Helton left the game due to an injured head"]
	id_map = rsp.parse_com(retro_list)
	print(id_map)
	assert(id_map['comment'] == "Rockies first baseman Todd Helton left the game due to an injured head")


def test_type_parser():
	#Need to specify stable path
	file_path = '/Users/patrickfisher/Documents/mlb/retrosheet/pbp/2013PIT.evn'
	rsp = RetrosheetLineParser()
# 	tmp_f = open('file.txt', 'wb')
# 	tmp_output = csv.writer(tmp_f, quoting = csv.QUOTE_ALL)
	with open(file_path,'r') as f:
		for line in f:
			line_parts = line.rstrip().split(',')
			parsed_line = rsp.type_parser(line_parts, rsp.parser_map)
			return parsed_line
# 			if parsed_line:
# # 				parsed_line_list = list(itertools.chain.from_iterable([[k, parsed_line[k]] for k in parsed_line]))
# 				parsed_line_list = sum([[k, parsed_line[k]] for k in parsed_line],[])
# # 				tmp_output.writerow(parsed_line_list)
# 				print parsed_line_list

test_parse_id()
test_parse_info()
test_parse_start()
test_parse_play()
test_parse_sub()
test_parse_data()
test_parse_ladj()
test_parse_badj()
test_parse_padj()
test_parse_com()
test_type_parser()
