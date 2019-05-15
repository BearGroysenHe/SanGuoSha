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
        self.player_numb = None
        self.players = None
        self.card = []
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
                        if data[1] == '__choice_hero':
                            self.__choice_hero(data)
                        elif data[1] == 'send_hero':
                            self.__get_hero_setting(data)
                        elif data[1] == 'send_card':
                            self.__send_card(data[2])
                        elif data[1] == 'push_card':
                            self.__push_card()
                else:
                    data = sys.stdin.readline()
                    self.sk.send(data.encode())


    def __choice_hero(self,data):
        while True:
            hero_name = input('请输入您要选择的英雄的名字')
            pack = {'name':data[1],'data':hero_name}
            self.datapack.pack_order(pack)
            response = self.sk.recv(2048).decode()
            response = self.dataunpack.unpack(response)
            print(response)
            if response[0] == 'C' and response[1] == '__choice_hero' and response[2] == 'OK':
                print('选择英雄成功')
                break
            elif response[0] == 'C' and response[1] == '__choice_hero' and response[2] == 'filed':
                print('选择英雄失败，请重新输入')

    def __get_hero_setting(self,data):
        self.players = data[2]
        print(self.players)

    def __push_card(self):
        while True:
            print(self.card)
            card_index = input('请输入您要出的牌的索引(输入quit进入弃牌阶段)')
            if card_index == 'quit':
                break
            else:
                self.datapack.pack_order({'name':'push_card','data':self.card[int(card_index)]})
                card = self.card.pop(int(card_index))
                response = self.sk.recv(2048).decode()
                response = self.dataunpack.unpack(response)
                if response[0] == 'C' and response[1] == 'push_card' and response[2]['status'] == 'failed':
                    print(response[2]['msg'])
                    self.card.append(card)
        self.__drop_card()

    def __drop_card(self):
        print('请弃牌至当前血量')
        current_hp =self.players[self.player_numb]['hero']['hp']
        print(current_hp)
        self.datapack.pack_order({'name':'drop_card','data':None})
        while True:
            if len(self.card) > current_hp:
                card_index = input('请输入您要丢弃的牌的索引')
                self.datapack.pack_order({'name':'drop_card','data':self.card[int(card_index)]})
                self.card.pop(int(card_index))
            else:
                self.datapack.pack_order({'name':'drop_card','data':'OK'})
                break

    def __send_card(self,card):
        card['from'] = self.player_numb
        card['to'] = None
        self.card.append(card)

if __name__ == '__main__':
    client = Client()