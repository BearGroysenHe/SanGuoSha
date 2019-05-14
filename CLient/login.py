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
        self.__log_in()

    def __log_in(self):
        print('欢迎登录三国杀')
        room_numb = input('请输入您要进入的房间号：')
        self.datapack.pack_order({'name':'room_numb','data':room_numb})
        response = self.sk.recv(512).decode()
        response = self.dataunpack.unpack(response)
        if response[0] == 'C' and response[1] == 'room_numb':
            if response[2] == 'OK':
                print('成功进入房间')
            else:
                print('进入房间失败')
        response = self.sk.recv(1024).decode()
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
                    data = r.recv(512).decode()
                    data = self.dataunpack.unpack(data)
                    if data[0] == "D":
                        if data[1] == '00':
                            print(data[2])
                        else:
                            print('玩家%s:%s'%(data[1],data[2]))
                    elif data[0] == 'C':
                        if data[1] == '__choice_hero':
                            self.__choice_hero(data)
                        if data[1] == 'send_hero':
                            self.__get_hero_setting(data)

                else:
                    data = sys.stdin.readline()
                    self.sk.send(data.encode())


    def __choice_hero(self,data):
        while True:
            hero_name = input('请输入您要选择的英雄的名字')
            pack = {'name':data[1],'data':hero_name}
            self.datapack.pack_order(pack)
            response = self.sk.recv(512).decode()
            print(response)
            response = self.dataunpack.unpack(response)
            if response[0] == 'C' and response[1] == '__choice_hero' and response[2] == 'OK':
                print('选择英雄成功')
                break
            elif response[0] == 'C' and response[1] == '__choice_hero' and response[2] == 'filed':
                print('选择英雄失败，请重新输入')

    def __get_hero_setting(self,data):
        print(data[2])

if __name__ == '__main__':
    client = Client()