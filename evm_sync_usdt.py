# utf-8

import asyncio
import json
import traceback
from pprint import pprint as pp
import web3
from web3 import Web3
import threading
import redis
import config
import deposit_currency_config
import csv
from mysql_handle import VaultDB
from redis_handle import VaultRedis
import time

class SyncListen(object):
    def __init__(self, token, network, provider, contract_address, contract_abi, channel_name, sync_history=False):
        self.provider = provider
        self.contract_address = contract_address
        self.contract_abi = json.loads(contract_abi)
        self.token = token
        self.network = network
        self.provider = Web3.HTTPProvider(provider)
        self.web3 = Web3(self.provider)
        self.channel_name = channel_name
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)
        self.event_list = ["Transfer"]
        self.sync_history = sync_history
        self.vault_db = VaultDB()
        # self.vault_redis = VaultRedis()
        self.wallet_dict = self.vault_db.get_deposit_wallet_dict()
        print(list(self.wallet_dict.keys())[0])
        # print(self.event_list)

    # {'args': {'from': '0x00056A746Ccc5bC2fb05B4c1e6E274B8D1816739', 'to': '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640',
    #           'value': 8500000}, 'event': 'Transfer', 'logIndex': 200, 'transactionIndex': 86,
    #  'transactionHash': '0xdab94074ef5106e6e9ad8c48d5c84f2702e4c7bb630ea8283fa9804b96b79d45',
    #  'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    #  'blockHash': '0x1744edbe819179f37c1469feffd75d58eb5992627cfdc73e12ea25a093dc192e', 'blockNumber': 15281596}

    # (data["user_id"], data["wallet_id"], data["source_address"], data["deposit_address"],
    #  data["network"], data["hash"], data["amount"], data["token"]))
    def handle_event(self, event):
        try:

            # print(self.channel_name, " : ", event)
            transfer = json.loads(Web3.toJSON(event))
            # self.vault_redis.set_last_block(self.network, transfer["blockNumber"])

            if transfer["args"]["to"] in self.wallet_dict:
                pp(transfer)
                wallet = self.wallet_dict[transfer["args"]["to"]]
                # print(wallet)
                # print(transfer["transactionHash"])
                # print((str(transfer["transactionHash"])))
                deposit_data = {
                    "user_id": wallet["user_id"] if wallet["user_id"] else "0000",
                    "wallet_id": wallet["wallet_id"],
                    "source_address": transfer["args"]["from"],
                    "deposit_address": transfer["args"]["to"],
                    "network": self.network,
                    "hash": str(transfer["transactionHash"]),
                    "amount": float(transfer["args"]["value"]) / (1 * 10 ** 18),
                    "token": self.token
                }

                VaultDB().upload_deposit_history(deposit_data)
                VaultRedis().upload(json.dumps(deposit_data))


        except Exception as e:
            print("error-", self.channel_name, "--", e)

    async def log_loop(self, poll_interval, is_block_filter=False):

        if not is_block_filter:
            while True:
                event_filter = self.contract.events['Transfer'].createFilter(fromBlock="latest",
                                                                             address=self.contract_address)
                try:
                    while True:
                        for event in event_filter.get_new_entries():
                            self.handle_event(event)
                        await asyncio.sleep(poll_interval)
                except Exception as E:
                    print(self.network, self.token, "syncing latest block:", E)
        else:
            while True:
                block_filter = self.web3.eth.filter('latest')
                try:
                    while True:
                        for block in block_filter.get_new_entries():
                            VaultRedis().set_last_block(self.network, self.web3.eth.block_number)
                            print(time.asctime( time.localtime(time.time()) ),self.network, self.web3.eth.block_number)
                            await asyncio.sleep(poll_interval)

                except Exception as E:
                    print(self.network, self.token, "syncing latest block:", E)

    async def log_history(self, event_filter):

        history_data = event_filter.get_all_entries()
        # print(history_data)
        for n in history_data:
            # print(n)
            self.handle_event(n)
        print(self.network, "-", self.token, "sync history finished")

    def run(self):
        last_block = VaultRedis().get_last_block(self.network)
        print(self.network, "last_block:", last_block)

        log_history_list = [
            self.contract.events[event_name].createFilter(fromBlock=int(last_block), toBlock="latest",
                                                          address=self.contract_address) for
            event_name in
            self.event_list] if last_block else []

        loop_list = [self.log_loop(2), self.log_loop(2, True)]

        history_list = [self.log_history(n) for n in log_history_list] if self.sync_history else []

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        try:
            print(f'syncing {self.network}-{self.token}...')
            loop.run_until_complete(
                asyncio.gather(
                    *(history_list + loop_list)
                ))
        except Exception as E:
            print(self.network, "--", self.token, self, "--", E)
        finally:
            new_loop.close()


def start(sync_history=False):
    with open('erc20ABI.json', 'r') as abi:
        abi = abi.read()
    thread_list = []

    for network in deposit_currency_config.address:

        for token_name in deposit_currency_config.address[network]:
            sync = SyncListen(provider=deposit_currency_config.provider[network], token=token_name, network=network,
                              contract_address=deposit_currency_config.address[network][token_name], contract_abi=abi,
                              channel_name=f"{network}-{token_name}", sync_history=sync_history)
            thread = threading.Thread(target=sync.run, name=f"{network}-{token_name}")
            thread_list.append(thread)

    for n in thread_list:
        print(n.name)
        n.start()

    # for n in thread_list:
    #     n.join()


if __name__ == "__main__":
    start()
