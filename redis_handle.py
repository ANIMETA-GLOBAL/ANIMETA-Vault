import redis

import config


class VaultRedis(object):

    def __init__(self):
        self.host = config.redis_host
        self.port = config.redis_port
        self.pwd = config.redis_pwd

        self.deposit_ch = config.redis_deposit_ch

    def upload(self, data):
        try:
            pool = redis.Redis(host=self.host, port=self.port, decode_responses=True, password=config.redis_pwd, db=0)

            pool.rpush(self.deposit_ch, data)
            return True

        except Exception as e:
            print(e)
            return False

    def get_last_block(self, network: str):
        pool = redis.Redis(host=self.host, port=self.port, decode_responses=True, password=config.redis_pwd, db=0)
        return pool.get(f"last_block_{network}")

    def set_last_block(self, network: str, block_number):
        pool = redis.Redis(host=self.host, port=self.port, decode_responses=True, password=config.redis_pwd, db=0)
        pool.set(f"last_block_{network}", block_number)
