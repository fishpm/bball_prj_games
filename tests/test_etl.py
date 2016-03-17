from etl.RetrosheetParser import RetrosheetLineParser


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

