import json
class DataUnPack():
    def unpack(self,data):
        data = data.strip()
        if data[0] == 'C':
            order = json.loads(data[1:],encoding='utf-8')
            order_type = order['name']
            order_data = order['data']
            return ['C',order_type,order_data]
        elif data[0] == 'D':
            #提取字符消息
            data_from = data[1:3]
            data_cont = data[3:]
            return ['D',data_from,data_cont]