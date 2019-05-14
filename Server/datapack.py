import json

class DataPack():
    def __init__(self,players_socket):
        self.players_socket = players_socket

    #打包控制流信息
    def pack_order(self,order,target = None):
        pack ='C' + json.dumps(order,ensure_ascii=False)
        pack = pack.ljust(512).encode()[:512]
        self.__send_pack(pack,target)

    #打包文本信息
    def pack_msg(self,player_numb ,msg,target = None):
        pack = 'D' + player_numb + msg
        pack = pack.ljust(512).encode()[:512]
        self.__send_pack(pack,target)

    #发送打包好的文件
    def __send_pack(self,pack,target):
        if target == None:
            for con in self.players_socket.values():
                con.send(pack)
        else:
            target.send(pack)