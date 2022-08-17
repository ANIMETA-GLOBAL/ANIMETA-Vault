import config
import time
from eth_account import Account
from web3 import Web3
import csv
import pymysql
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from tronpy import Tron, Contract
import base58
import config


class AnimetaVault(object):

    def __init__(self):
        self.public_key = ""
        self.load_pub()

    def load_pub(self):
        with open('rsa.pub', 'r') as f:
            self.public_key = f.read()

        print(f"pubKey loaded: \n{self.public_key}")

    def encode_key(self, private_key):
        rsa_key_obj = RSA.importKey(self.public_key)
        cipher_obj = PKCS1_v1_5.new(rsa_key_obj)
        cipher_text = base64.b64encode(cipher_obj.encrypt(private_key.encode()))
        return cipher_text

    def update_wallet_evm(self, jsonData):
        db = pymysql.connect(host=config.mysql_host, port=config.mysql_port, user=config.mysql_user, password=config.mysql_pwd,
                             db=config.mysql_db)

        cursor = db.cursor()
        sql = "INSERT INTO animeta_wallet(wallet_address, \
               private_key) \
               VALUES (%s,%s)"

        val = [(list(n)[1], list(n)[4]) for n in jsonData]
        # print(set(val))
        try:
            # 执行sql语句
            cursor.executemany(sql, set(val))
            # 提交到数据库执行
            db.commit()
        except Exception as E:
            print(E)
            # 如果发生错误则回滚
            db.rollback()

        # 关闭数据库连接
        db.close()

    def gen_wallet_evm(self, amount_to_generate: int = 1000):
        wallets = []

        for id in range(amount_to_generate):
            # 添加一些随机性
            account = Account.create('Random  Seed' + str(id))

            # 私钥
            privateKey = account._key_obj

            # 公钥
            publicKey = privateKey.public_key

            # 地址
            address = publicKey.to_checksum_address()

            wallet = {
                "id": id,
                "address": address,
                "privateKey": privateKey,
                "publicKey": publicKey,
                "codedPrivateKey": self.encode_key(str(privateKey)).decode('UTF-8')
            }
            # print(type(encode_key(str(privateKey)).decode('UTF-8') ))
            wallets.append(wallet.values())

        with open(f'wallets_{int(time.time())}.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["序号", "钱包地址", "私钥", "公钥", "加密私钥"])
            csv_writer.writerows(wallets)

        self.update_wallet_evm(wallets)

        return wallets

    def update_wallet_tron(self, jsonData):
        db = pymysql.connect(host=config.mysql_host, port=config.mysql_port,user=config.mysql_user, password=config.mysql_pwd,
                             db=config.mysql_db)

        cursor = db.cursor()
        sql = "INSERT INTO animeta_wallet_tron(wallet_address, \
               private_key) \
               VALUES (%s,%s)"

        val = [(list(n)[1], list(n)[4]) for n in jsonData]
        # print(set(val))
        try:
            # 执行sql语句
            cursor.executemany(sql, set(val))
            # 提交到数据库执行
            db.commit()
        except Exception as E:
            print(E)
            # 如果发生错误则回滚
            db.rollback()

        # 关闭数据库连接
        db.close()

    def gen_wallet_tron(self, amount_to_generate: int = 1000):
        wallets = []
        for id in range(amount_to_generate):
            new = Tron().generate_address()
            wallet = {
                "id": id,
                "address": new['base58check_address'],
                "privateKey": new['private_key'],
                "publicKey": new['public_key'],
                "codedPrivateKey": self.encode_key(new['private_key']).decode('UTF-8')
            }
            # print(type(encode_key(str(privateKey)).decode('UTF-8') ))
            wallets.append(wallet.values())

        with open(f'tron_wallets_{int(time.time())}.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["序号", "钱包地址", "私钥", "公钥", "加密私钥"])
            csv_writer.writerows(wallets)

        self.update_wallet_tron(wallets)


if __name__ == '__main__':
    A = AnimetaVault()
    A.gen_wallet_tron(1000)
