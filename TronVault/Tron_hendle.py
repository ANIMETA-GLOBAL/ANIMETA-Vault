import json
import redis
from pprint import pprint as pp
import os
from dotenv import load_dotenv
from tronpy import Tron, Contract
import Tron_sync_history
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

REDIS_HOST = os.getenv('REDISHOST')
REDIS_PWD = os.getenv('REDISPWD')


class TronTrc20(object):

    def __init__(self, wallet_list: dict) -> None:
        self.pool = redis.Redis(host=REDIS_HOST, decode_responses=True,
                                password=REDIS_PWD, db=3)
        self.sync_history = Tron_sync_history.SyncHistory(self.pool)

    def handle_evnet(self):
        print("getting lates event")
        while True:
            tx = self.pool.lpop("TronTransfer")

            if tx:
                event = json.loads(tx)
                self.pool.set("last_block_TUSDT", event["blockNumber"])
                # print(event)
                if event["eventName"] == "Transfer":
                    pp(event)
                    from_address = Tron().to_base58check_address(event["result"]["from"])
                    to_address = Tron().to_base58check_address(event["result"]["to"])
                    value = float(event["result"]["value"]) / 100000

                    # if to_address in wallet_list:

    def handle_history_event(self):
        last_block = self.pool.get("last_block_TUSDT")
        print("last_block:", last_block)
        if last_block:
            self.sync_history.get_sync_history(last_block)
            while True:
                tx = self.pool.lpop("TronTransferHistory")
                if tx:
                    event = json.loads(tx)
                    # print(event)
                    if event["event_name"] == "Transfer":
                        pp(event)
                        from_address = Tron().to_base58check_address(event["result"]["from"])
                        to_address = Tron().to_base58check_address(event["result"]["to"])
                        value = float(event["result"]["value"]) / 100000

    def run(self):
        with ThreadPoolExecutor(2) as t:
            t.submit(self.handle_evnet)
            t.submit(self.handle_history_event)


if __name__ == '__main__':
    A = TronTrc20(wallet_list={})
    A.run()
