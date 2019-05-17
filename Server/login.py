import socket
from select import select
from game_controller import GameController
from multiprocessing import Process
from datapack import DataPack
from dataunpack import DataUnPack
import signal

class Server():
    def __init__(self):
        self.sk = socket.socket()
        self.sk.bind(('127.0.0.1', 8999))
        self.sk.listen(5)
        self.rlist = [self.sk]
        self.game_room = {}
        self.datapack = DataPack(None)
        self.dataunpack = DataUnPack()

    def log_in(self):
        while True:
            rl, wl, xl = select(self.rlist,[],[])
            for r in rl:
                if r is self.sk:
                    con, addr = r.accept()
                    self.rlist.append(con)
                else:
                    response = r.recv(2048).decode()
                    response = self.dataunpack.unpack(response)
                    if response[0] == 'C' and response[1] == 'room_numb':
                        data = response[2]
                        if data not in self.game_room:
                            self.game_room[data]= {'01':None,'02':None,'03':None,'04':None,'05':None}
                            self.game_room[data]['01'] = r
                            self.datapack.pack_order({'name':'room_numb','data':'OK'},r)
                            self.datapack.pack_order({'name': 'player_numb', 'data': '01'}, r)
                        else:
                            for keys,values in self.game_room[data].items():
                                if values == None:
                                    self.game_room[data][keys] = r
                                    self.datapack.pack_order({'name': 'room_numb', 'data': 'OK'}, r)
                                    self.datapack.pack_order({'name': 'player_numb', 'data': keys}, r)
                                    break
                        for con in self.game_room[data].values():
                            if con == None:
                                break
                        else:
                            for con in self.game_room[data].values():
                                self.rlist.remove(con)
                            game_controller = GameController(self.game_room[data])
                            p = Process(target = game_controller.run_game)
                            p.start()


if __name__ == '__main__':
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    server = Server()
    server.log_in()