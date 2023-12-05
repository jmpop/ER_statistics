import os

os.system("cls")
from ER_datas.data_class import DataClass
from .rank_mmr import mmr_charges
from .tier_mmr import Tier

"""
dic_characterNum_characterName[characterNum] = 캐릭터명
dic_characterNum_characterCount[characterNum] = 캐릭터별 빈도
dic_characterNum_BeforeMMR[characterNum]= {BeforeMMR:dic_BeforeMMR_datas}
dic_BeforeMMR_datas
=[{         
    "mmrGain": 얻은점수,
    "gameRank":게임 순위,
    "escapeState":탈출유무
 }]
"""

# game_data 가져오기


import json
from glob import glob


# game_mode ["Rank", "Normal"]
# "Rank"
#


def load_lastest_version():
    game_list = sorted(glob("./datas/Ver*.json"))
    last_game = (game_list[-1].split("Ver")[1]).split("._")[0]
    lastest_version = last_game.split("_")[0]
    print(lastest_version)
    return lastest_version.split(".")[0], lastest_version.split(".")[1]


def load_lastest_verson_from_file():
    file_name = "./setting/game_version.json"
    with open(file_name, "r", encoding="utf-8") as f:
        lastest_version = json.load(f)
    return (
        lastest_version["CURRENT_GAME_MAJOR_VERSION"],
        lastest_version["CURRENT_GAME_MINOR_VERSION"],
    )


from ER_apis.ER_DB import query_mongoDB


def ERDataCleansing(
    data_class=DataClass(),
    game_mode=["Rank"],
    major_version=-1,
    minor_version=-1,
    dbQuery="",
):
    if major_version == -1 and minor_version == -1:
        major_version, minor_version = load_lastest_verson_from_file()
    elif major_version == -1 or minor_version == -1:
        print("version error,used base Version")
    if dbQuery == "":
        for mode in game_mode:
            game_list = glob(
                "./datas/Ver{0}.{1}_{2}_*.json".format(
                    major_version, minor_version, mode
                )
            )
            for file_name in game_list:
                with open(file_name, "r", encoding="utf-8") as f:
                    game_datas = json.load(f)
                # file_index = str(file_name.split("_")[2]).split(".")[0]
                # print("Add {0}.json".format(file_index))
                for user_data in game_datas["userGames"]:
                    """유저 정보"""
                    data_class.add_data(user_data)
                data_class.add_data_game_id()
        data_class.last_calculate()
    else:
        game_list = query_mongoDB(dbQuery)
        for game in game_list:
            for user_data in game["userGames"]:
                data_class.add_data(user_data)
            data_class.add_data_game_id()
        data_class.last_calculate()


class FilterType:
    """type=filter
    dic_characterNum_datas[characterNum][condition]=datas
    """

    def filter_data_init(self):
        self.dic_characterNum_datas = {}

    def filter_data(self, user_data):
        characterNum = user_data["characterNum"]
        datas = {}
        list_request_datatype = self.condition
        for request_datatype in list_request_datatype:
            datas[request_datatype] = user_data[request_datatype]
            self.dic_characterNum_datas[characterNum] = self.dic_characterNum_datas.get(
                characterNum, []
            ) + [datas]

    def data_cleansing_init(self):
        self.dic_characterNum_datas = {}

    def data_cleansing(self, user_data):
        characterNum = user_data["characterNum"]
        dic_characterNum_datas = self.dic_characterNum_datas.get(characterNum, {})
        for condition in self.condition:
            data = user_data[condition]
            dic_characterNum_datas[condition] = dic_characterNum_datas.get(
                condition, []
            ) + [data]
        self.dic_characterNum_datas[characterNum] = dic_characterNum_datas

    """type=data_cleansing
    dic_characterNum_datas["mmrGain"]=datas
    dic_characterNum_datas["condition"]=datas
    """

    def mmrGain_option_init(self):
        self.dic_characterNum_datas = {}

    def mmrGain_option(self, user_data):
        characterNum = user_data["characterNum"]
        dic_characterNum_datas = self.dic_characterNum_datas.get(characterNum, {})
        data = user_data["mmrGain"] + mmr_charges(user_data["mmrBefore"])

        dic_characterNum_datas["mmrGain"] = dic_characterNum_datas.get(
            "mmrGain", []
        ) + [data]
        for condition in self.condition:
            data = user_data[condition]
            dic_characterNum_datas[condition] = dic_characterNum_datas.get(
                condition, []
            ) + [data]
        self.dic_characterNum_datas[characterNum] = dic_characterNum_datas

    """split_mmr"""

    def split_mmr_init(self):
        self.dic_characterNum_datas = {}

    def split_mmr(self, user_data):
        characterNum = user_data["characterNum"]
        dic_characterNum_datas = self.dic_characterNum_datas.get(characterNum, Tier())
        dic_characterNum_datas.split_tier(user_data["mmrBefore"], user_data["mmrGain"])
        self.dic_characterNum_datas[characterNum] = dic_characterNum_datas

    dic_type_init = {
        "filter": filter_data_init,
        "data_cleansing": data_cleansing_init,
        "mmrGain_option": mmrGain_option_init,
        "split_mmr": split_mmr_init,
    }
    dic_type_add_data = {
        "filter": filter_data,
        "data_cleansing": data_cleansing,
        "mmrGain_option": mmrGain_option,
        "split_mmr": split_mmr,
    }

    dic_type_last_calculate = {}

    """setting"""

    def __init__(self, type, condition):
        self.type = type
        self.condition = condition
        self.dic_type_init[type](self)
        pass

    """add result"""

    def add_data(self, user_data):
        self.dic_type_add_data[self.type](self, user_data)

    def last_calculate(self):
        self.dic_type_last_calculate.get(self.type, "")
        print("last")


# list_request_datatype=["mmrBefore","mmrGain"]
# dic_characterNum_datas=ERDataCleansing(27619195,27621220,"data_cleansing",["mmrBefore","mmrGain"])
# print(dic_characterNum_datas.dic_characterNum_datas)
