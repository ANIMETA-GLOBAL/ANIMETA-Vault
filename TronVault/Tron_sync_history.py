from concurrent.futures import ThreadPoolExecutor

import requests
from pprint import pprint as pp
import threading
import redis
import json


class SyncHistory(object):

    def __init__(self, pool):
        self.pool = pool

    def get_latest_block(self):
        url = "https://api.trongrid.io/v1/blocks/latest/events?limit=1"
        headers = {
            'Content-Type': "application/json",
            'TRON-PRO-API-KEY': "a4cd0eca-6745-4d79-b15f-e6c44640aa7f"
        }
        response = requests.request("get", url, headers=headers)
        result = response.json()
        return result['data'][0]['block_number']

    def get_from_block(self, block_number: int, fingerprint=None):
        res = []

        url = f"https://api.trongrid.io/v1/contracts/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t/events?event_name=Transfer&limit=20{('&block_number=' + str(block_number)) if block_number else ''}" \
              f"{('&fingerprint=' + fingerprint) if fingerprint else ''}"
        # print(url)
        payload = ""
        headers = {
            'Content-Type': "application/json",
            'TRON-PRO-API-KEY': "a4cd0eca-6745-4d79-b15f-e6c44640aa7f"
        }
        response = requests.request("get", url, headers=headers)
        result = response.json()
        # pp(result)
        if 'fingerprint' in result['meta']:
            next_fingerprint = result['meta']['fingerprint']
            res += self.get_from_block(block_number=block_number, fingerprint=next_fingerprint)

        res += result['data']
        # print(len(result['data']))
        for n in res:
            self.pool.rpush("TronTransferHistory", json.dumps(n))

        return res

    def get_sync_history(self, from_block, to_block=None):
        history_event = []

        if not to_block:
            to_block = self.get_latest_block()
            print(f"sync from {from_block} to {to_block}")
        with ThreadPoolExecutor(50) as t:
            for n in range(int(from_block), to_block):
                t.submit(self.get_from_block, n)

        return history_event

# fin = get_from_block(block_number=43348146)
# print(len(fin))
