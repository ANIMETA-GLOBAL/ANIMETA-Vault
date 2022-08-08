import redis

import config


class VaultRedis(object):

    def __init__(self):
        self.host = config.redis_host
        self.port = config.redis_port
        self.pwd = config.redis_pwd

        self.pool = redis.Redis(host=self.host, port=self.port, decode_responses=True, password=config.redis_pwd, db=0)
        self.deposit_ch = config.redis_deposit_ch

    def upload(self,data):
        try:
            self.pool.rpush(self.deposit_ch,data)
            return True

        except Exception as e:
            print(e)
            return False

