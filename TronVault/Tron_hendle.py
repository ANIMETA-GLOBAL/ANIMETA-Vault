import json
import redis
from pprint import pprint as pp
import os
from dotenv import load_dotenv
from tronpy import Tron, Contract
import Tron_sync_history
from concurrent.futures import ThreadPoolExecutor
from mysql_handle import VaultDB
from redis_handle import VaultRedis

load_dotenv()

REDIS_HOST = os.getenv('REDISHOST')
REDIS_PWD = os.getenv('REDISPWD')


class TronTrc20(object):

    def __init__(self) -> None:
        self.pool = redis.Redis(host=REDIS_HOST, decode_responses=True,
                                password=REDIS_PWD, db=3)
        self.sync_history = Tron_sync_history.SyncHistory(self.pool)
        self.vault_db = VaultDB()
        self.vault_redis = VaultRedis()
        self.wallet_dict = self.vault_db.get_deposit_wallet_dict_tron()
        # print(self.wallet_dict)
    def handle_evnet(self):
        print("getting latest event")
        while True:
            tx = self.pool.lpop("TronTransfer")
            # print(tx)
            if tx:
                print(tx)
                event = json.loads(tx)
                self.pool.set("last_block_TUSDT", event["blockNumber"])

                if event["eventName"] == "Transfer":
                    pp(event)
                    from_address = Tron().to_base58check_address(event["result"]["from"])
                    to_address = Tron().to_base58check_address(event["result"]["to"])
                    value = float(event["result"]["value"]) / 1000000
                    transaction_hash = event["transactionHash"]

                    if to_address in self.wallet_dict:
                        wallet = self.wallet_dict[to_address]
                        deposit_data = {
                            "user_id": wallet["user_id"] if wallet["user_id"] else "0000",
                            "wallet_id": wallet["wallet_id"],
                            "source_address": from_address,
                            "deposit_address": to_address,
                            "network": "tron",
                            "hash": transaction_hash,
                            "amount": value ,
                            "token": "USDT"
                        }
                        pp(deposit_data)
                        VaultRedis().upload(json.dumps(deposit_data))
                        VaultDB().upload_deposit_history(deposit_data)

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
                        # pp(event)
                        from_address = Tron().to_base58check_address(event["result"]["from"])
                        to_address = Tron().to_base58check_address(event["result"]["to"])
                        value = float(event["result"]["value"]) / 1000000
                        transaction_hash = event["transaction_id"]

                        if to_address in self.wallet_dict:
                            wallet = self.wallet_dict[to_address]
                            deposit_data = {
                                "user_id": wallet["user_id"] if wallet["user_id"] else "0000",
                                "wallet_id": wallet["wallet_id"],
                                "source_address": from_address,
                                "deposit_address": to_address,
                                "network": "tron",
                                "hash": transaction_hash,
                                "amount": value ,
                                "token": "USDT"
                            }
                            pp(deposit_data)
                            VaultRedis().upload(json.dumps(deposit_data))
                            VaultDB().upload_deposit_history(deposit_data)

    def run(self):
        with ThreadPoolExecutor(2) as t:
            t.submit(self.handle_evnet)
            # t.submit(self.handle_evnet)
            # t.submit(self.handle_history_event)


if __name__ == '__main__':
    A = TronTrc20()
    A.run()
