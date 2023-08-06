import os
import json
import redis
import time

class ExecutorApi():
    def __init__(self,exchange,symbol_coin,symbol_basecoin):
        self.data_name = symbol_coin + "/" + symbol_basecoin
        self.trade_name = symbol_coin + symbol_basecoin
        self.CCAWS_REDIS_HOST = os.getenv('CCAWS_REDIS_HOST')
        self.CCAWS_REDIS_AUTH = os.getenv('CCAWS_REDIS_AUTH')
        self.ex = exchange
        if self.ex == "OKEX":
            self.exlabel = "O"

    def send_cmd_maker(self, instance, targetside, targetLevel):
        instance_name = instance + "_" + self.trade_name + "." + self.exlabel
        #cmd = {"instance": instance_name, "action": "set_posLevel", "value":targetLevel}
        cmd = {"instance": instance_name, "action": "set_trading_mode", "value": targetside, "posLevel": targetLevel}
        conn = redis.StrictRedis(host=self.CCAWS_REDIS_HOST, port=6396, db=0, password=self.CCAWS_REDIS_AUTH)
        channel = 'command'
        data = json.dumps({'type': 'MSG_TYPE_COMMAND', 'data': cmd},indent=4)
        
        print(data)
        conn.publish(channel, data)
        data=[int(time.time()), {"type": "MSG_TYPE_COMMAND", "data": {"instance": instance_name, \
                            "action": "set_trading_mode", "value": targetside, "posLevel": targetLevel}}]
        return data
        #send_cmd(trade_name)

    def send_cmd_taker(self, instance, targetLevel):
        instance_name = instance + "_" + self.trade_name + "." + self.exlabel
        cmd = {"instance": instance_name, "action": "set_posLevel", "value":targetLevel}
        conn = redis.StrictRedis(host=self.CCAWS_REDIS_HOST, port=6396, db=0, password=self.CCAWS_REDIS_AUTH)
        channel = 'command'
        data=[int(time.time()), {"type": "MSG_TYPE_COMMAND", "data": {"instance": instance_name, \
                            "action": "set_trading_mode", "posLevel": targetLevel}}]
        print(data)
        conn.publish(channel, data)
        return data



