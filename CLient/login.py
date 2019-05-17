import socket
import sys
from select import select
from datapack import DataPack
from dataunpack import DataUnPack

class Client():
    def __init__(self):
        self.sk = socket.socket()
        self.sk.connect(('127.0.0.1', 8999))
        self.rlist = [self.sk, sys.stdin]
        self.datapack = DataPack(self.sk)
        self.dataunpack = DataUnPack()
        self.player_numb = '01'
        self.players = None
        self.card = []
        self.status = None
        self.alive_players = None
        self.have_attack = True
        self.__log_in()

    def __log_in(self):
        print('欢迎登录三国杀')
        room_numb = input('请输入您要进入的房间号：')
        self.datapack.pack_order({'name':'room_numb','data':room_numb})
        response = self.sk.recv(2048).decode()
        response = self.dataunpack.unpack(response)
        if response[0] == 'C' and response[1] == 'room_numb':
            if response[2] == 'OK':
                print('成功进入房间')
            else:
                print('进入房间失败')
        response = self.sk.recv(2048).decode()
        response = self.dataunpack.unpack(response)
        if response[0] == 'C' and response[1] == 'player_numb':
            self.player_numb = response[2]
        print(self.player_numb)
        self.__choice_hero()
        self.__run_game()

    def __run_game(self):
        while True:
            rl, wl, xl = select(self.rlist,[],[])
            for r in rl:
                if r is self.sk:
                    data = r.recv(2048).decode()
                    data = self.dataunpack.unpack(data)
                    if data[0] == "D":
                        if data[1] == '00':
                            print(data[2])
                        else:
                            print('玩家%s:%s'%(data[1],data[2]))
                    elif data[0] == 'C':
                        if data[1] == 'send_hero':
                            self.__get_hero_setting(data)
                        elif data[1] == 'send_card':
                            self.__send_card(data[2])
                        elif data[1] == 'push_card':
                            self.have_attack = False
                            self.status = 'push_card'
                            print(self.card)
                            print(len(self.card))
                            print('请输入您要出的牌的索引(输入quit进入弃牌阶段)')
                        elif data[1] == 'add_hp':
                            self.__add_hp(data[2])
                        elif data[1] == 'response':
                            self.__response(data[2])
                        elif data[1] == 'sub_hp':
                            self.__sub_hp(data[2])
                else:
                    data = sys.stdin.readline()[:-1]
                    print(data)
                    if data == 'show':
                        print('角色信息')
                        print(self.players[self.player_numb])
                        print('卡牌信息')
                        for card in self.card:
                            print(card)
                        print('存活玩家列表')
                        print(self.alive_players)
                        print('您的编号')
                        print(self.player_numb)
                    elif self.status == 'push_card':
                        self.__push_card(data)
                    elif self.status == 'drop_card':
                        self.__drop_card(data)


    def __choice_hero(self):
        condition = True
        while True:
            if condition:
                rl, wl, xl = select(self.rlist,[],[])
                for r in rl:
                    if r is self.sk:
                        data = r.recv(2048).decode()
                        data = self.dataunpack.unpack(data)
                        if data[0] == "D":
                            if data[1] == '00':
                                print(data[2])
                            else:
                                print('玩家%s:%s'%(data[1],data[2]))
                        elif data[0] == 'C' and data[1] == '__choice_hero' and data[2] == 'OK':
                            print('选择英雄成功')
                        elif data[0] == 'C' and data[1] == '__choice_hero' and data[2] == 'filed':
                            print('选择英雄失败，请重新输入')
                        elif data[0] == 'C' and data[1] == '__choice_hero' and data[2] == None:
                            print('请输入您要选择英雄的名字')
                        elif data[0] == 'C' and data[1] == '__choice_hero' and data[2] == 'over':
                            condition = False
                            break
                    else:
                        hero_name = sys.stdin.readline()[:-1]
                        pack = {'name': '__choice_hero', 'data': hero_name}
                        self.datapack.pack_order(pack)
            else:
                break

    def __get_hero_setting(self,data):
        self.players = data[2]
        self.alive_players = []
        for key, value in self.players.items():
            if value['alive'] == True:
                self.alive_players.append(key)
        self.alive_players.sort()

    def __push_card(self,card_index):
        if card_index == 'quit':
            print('请弃牌至当前血量')
            current_hp = int(self.players[self.player_numb]['hero']['hp'])
            print(current_hp)
            print('请输入您要丢弃的牌的索引')
            self.datapack.pack_order({'name': 'drop_card', 'data': None})
            self.status = 'drop_card'
        else:
            card =self.card[int(card_index)]
            if card['name'] == 'Sha':
                if self.have_attack:
                    print('您本回合已经出过一次杀了')
                else:
                    while True:
                        target = input('请输入目标玩家的编号')
                        card['to'] = target
                        print(target)
                        if self.__check_distance(self.player_numb,target):
                            self.datapack.pack_order({'name':'push_card','data':card})
                            self.card.remove(card)
                            self.have_attack = True
                            break
                        else:
                            print('您的攻击距离不够无法出杀')
            elif card['name'] == 'Tao':
                if self.players[self.player_numb]['hero']['hp_max'] == self.players[self.player_numb]['hero']['hp']:
                    print('您的生命值已满,无法出桃')
                else:
                    self.datapack.pack_order({'name':'push_card','data':card})
                    self.card.remove(card)
            else:
                print('您不能打出这张牌')


    def __drop_card(self,card_index):
        current_hp = int(self.players[self.player_numb]['hero']['hp'])
        self.datapack.pack_order({'name': 'drop_card', 'data': self.card[int(card_index)]})
        self.card.pop(int(card_index))
        if len(self.card) <= current_hp:
            print('弃牌结束')
            self.datapack.pack_order({'name': 'drop_card', 'data': 'OK'})
            self.status = 'response'

    def __send_card(self,card):
        card['from'] = self.player_numb
        card['to'] = None
        self.card.append(card)

    def __check_distance(self,skill_from,skill_to):
        index1 = self.alive_players.index(skill_from)
        index2 = self.alive_players.index(skill_to)
        alive_numb = len(self.alive_players)/2
        distance = alive_numb-abs(abs(index1-index2)-alive_numb)
        range = 1
        if distance > range:
            return False
        else:
            return True

    def __add_hp(self,data):
        self.players[data['target']]['hero']['hp'] += 1

    def __response(self,data):
        if data['name'] == 'Sha':
            print('有人对我除了一张杀')
            result = self.__check_card_exist('Shan')
            print(result)
            if result == False:
                data['response'] = 'failed'
                self.datapack.pack_order({'name':'response','data':data})
            else:
                card_index = input('请出一张闪(输入quit放弃)')
                if card_index == 'quit':
                    data['response'] = 'failed'
                    self.datapack.pack_order({'name': 'response', 'data': data})
                elif self.card[int(card_index)]['name'] == 'Shan':
                    data['response'] = 'OK'
                    self.datapack.pack_order({'name':'response','data':data})
                    self.datapack.pack_order({'name':'push_card','data':self.card[int(card_index)]})
                    self.card.remove(self.card[int(card_index)])
                else :
                    print('您只能出闪')


    def __sub_hp(self,data):
        self.players[data]['hero']['hp'] -= 1
        self.__check_alive()

    def __check_alive(self):
        if self.players[self.player_numb]['hero']['hp'] < 1:
            if self.__check_card_exist('tao'):
                self.datapack.pack_order({'name':'dying','data':self.player_numb})
            else:
                card_index = input('您快要死了，请出桃(输入quit拒绝)')
                if card_index == 'quit':
                    self.datapack.pack_order({'name': 'dying', 'data': self.player_numb})
                elif self.card[int(card_index)]['name'] == 'tao':
                    self.datapack.pack_order({'name': 'push_card', 'data': self.card[int(card_index)]})
                else:
                    print('您只能出桃')

    def __check_card_exist(self,card_name):
        for card in self.card:
            if card['name'] == card_name:
                return True
        return False

if __name__ == '__main__':
    client = Client()