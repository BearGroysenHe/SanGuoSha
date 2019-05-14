import socket
from random import randint
import json
from select import select
from datapack import DataPack
from dataunpack import DataUnPack

# sk = socket.socket()
# sk.bind(('127.0.0.1',8999))
# sk.listen(5)
# con,addr = sk.accept()
# players = {'01':con}

class GameController():
    def __init__(self,players_socket):
        with open('setting/setting_hero.json','r') as f:
            self.setting_hero = json.loads(f.read(),encoding='utf-8')
        self.players = {}
        self.players_socket = players_socket
        self.rlist = []
        for con in self.players_socket.values():
            self.rlist.append(con)
        self.datapack = DataPack(players_socket)
        self.dataunpack = DataUnPack()
        for player_num in players_socket.keys():
            self.players[player_num] ={}
            self.players[player_num]['equip'] = {}
            self.players[player_num]['equip'] = {"horse_add": None, "houser_sub": None, "armour": None, "weapon": None}
            self.players[player_num]['identity'] = None
        self.total_card = []
        self.drop_card = []

    def run_game(self):
        self.datapack.pack_msg('00','人数已满，正在进入游戏')
        self.__init()
        for key, value in self.players.items():
            if value['identity'] == '主公':
                player = key
                break
        while True:
            print(player)
            self.__beginning()
            self.__judgment()
            self.__get_card(player)
            self.__push_card(player)
            self.__drop_card(player)
            self.__ending()
            player = int(player) + 1
            print(player)
            if player > 5:
                player -= 5
            player = str(player).zfill(2)
            print(player)

    def __init(self):
        self.__card_creater()
        self.__identity_creater()
        self.__choice_hero()
        self.__send_hero_to_player()
        for con in self.players_socket.values():
            self.__send_card_to_player(4,con)

    def __card_creater(self):
        type = ('Sha','Shan','Tao')
        card_color = ('S','H','C','D')
        for i in range(108):
            card = {}
            card['name'] = type[randint(0,2)]
            card['card_color'] = card_color[randint(0,3)]
            card['card_numb'] = str(randint(1,13)).zfill(2)
            self.total_card.append(card)

    def __identity_creater(self):
        identity_pool = ['主公','忠臣','内奸','反贼','反贼']
        # identity_pool = ['主公']
        for i in range(1,len(self.players.keys())+1):
            identity = identity_pool[randint(0, len(identity_pool)-1)]
            self.players[str(i).zfill(2)]['identity'] = identity
            identity_pool.remove(identity)
            msg = '您的身份是%s'%(identity)
            self.datapack.pack_msg('00',msg,self.players_socket[str(i).zfill(2)])

    def __choice_hero(self):
            hero_list = []
            for hero in self.setting_hero.keys():
                hero_list.append(hero)
            self.datapack.pack_msg('00','开始选择英雄')
            self.datapack.pack_msg('00',json.dumps(hero_list,ensure_ascii=False))
            self.datapack.pack_order({'name':'__choice_hero','data':''})
            condition = True
            while True:
                if condition:
                    rl,wl,xl = select(self.rlist,[],[])
                    for r in rl:
                        data = r.recv(2048).decode()
                        data = self.dataunpack.unpack(data)
                        player = self.__get_player_by_con(r)
                        hero = data[2]
                        if data[0] == 'C' and data[1] == '__choice_hero':
                            if hero in hero_list:
                                self.__add_hero_to_player(player,hero)
                                self.datapack.pack_order({'name':'__choice_hero','data':'OK'},self.players_socket[player])
                            else:
                                self.datapack.pack_order({'name': '__choice_hero', 'data': 'filed'},self.players_socket[player])
                                continue
                        else:
                            self.datapack.pack_order({'name': '__choice_hero', 'data': 'filed'},self.players_socket[player])
                            continue
                        # msg = '玩家%s已选择英雄%s'%(player,hero)
                        # self.datapack.pack_msg(player,msg)
                        hero_list.remove(hero)
                        # self.datapack.pack_msg('00', json.dumps(hero_list, ensure_ascii=False))
                        if len(hero_list) == 0:
                            self.datapack.pack_msg('00','选择英雄结束')
                            condition =False
                            break
                else:
                    break


    def __get_player_by_con(self,con):
        for key, value in self.players_socket.items():
            if value == con:
                return key

    def __add_hero_to_player(self,player,hero):
        hero_setting = 'setting/hero/' + self.setting_hero[hero]
        with open(hero_setting,encoding='utf-8') as f:
            hero_setting = json.loads(f.read(),encoding='utf-8')
        self.players[player]['hero'] = hero_setting

    def __send_hero_to_player(self):
        self.datapack.pack_order({'name':'send_hero','data':self.players})

    def __send_card_to_player(self,numb,target):
        for i in range(numb):
            card = self.total_card.pop()
            self.datapack.pack_order({'name':'send_card','data':card},target)

    def __beginning(self):
        pass

    def __judgment(self):
        pass

    def __get_card(self,player):
        self.__send_card_to_player(2,self.players_socket[player])

    def __push_card(self,player):
        self.datapack.pack_order({'name':'push_card','data':None},self.players_socket[player])
        while True:
            data = self.players_socket[player].recv(2048).decode()
            data = self.dataunpack.unpack(data)
            if data[0] == 'C':
                if data[1] == 'push_card':
                    # self.datapack.pack_msg('玩家%s打出了一张%s'%(player,data[2]['name']))
                    print('玩家%s打出了一张%s'%(player,data[2]))
                    pass
                elif data[1] == 'drop_card':
                    break

    def __drop_card(self,player):
        while True:
            data = self.players_socket[player].recv(2048).decode()
            data = self.dataunpack.unpack(data)
            if data[0] == 'C' and data[1] == 'drop_card':
                if data[2] == 'OK':
                    break
                else:
                    self.drop_card.append(data[2])
                    print('玩家%s丢弃了%s'%(player,data[2]))

    def __ending(self):
        pass

# game_controller = GameController(players)
# game_controller.run_game()
# data = input('zuse')
