from eth_account import Account
from web3 import Web3
import csv
import pymysql

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

with open('rsa.key', 'r') as f:
    private_key = f.read()


def decode_key(coded_key):
    rsa_key_obj = RSA.importKey(private_key)
    cipher_obj = PKCS1_v1_5.new(rsa_key_obj)
    random_generator = Random.new().read
    plain_text = cipher_obj.decrypt(base64.b64decode(coded_key), random_generator)
    return plain_text


with open('rsa.pub', 'r') as f:
    public_key = f.read()


def encode_key(private_key):
    rsa_key_obj = RSA.importKey(public_key)
    cipher_obj = PKCS1_v1_5.new(rsa_key_obj)
    cipher_text = base64.b64encode(cipher_obj.encrypt(private_key.encode()))
    return cipher_text


def createNewETHWallet():
    wallets = []

    for id in range(1000):
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
            "codedPrivateKey": encode_key(str(privateKey)).decode('UTF-8')
        }
        # print(type(encode_key(str(privateKey)).decode('UTF-8') ))
        wallets.append(wallet.values())

    return wallets


def saveETHWallet(jsonData):
    with open('wallets.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["序号", "钱包地址", "私钥", "公钥", "加密私钥"])
        csv_writer.writerows(jsonData)


def updateETHWallet(jsonData):
    db = pymysql.connect(host="211.149.170.109", user="animeta", password="animeta", db="animeta")

    cursor = db.cursor()
    sql = "INSERT INTO animeta_wallet(wallet_address, \
           private_key) \
           VALUES (%s,%s)"

    val = [(list(n)[1],list(n)[4]) for n in jsonData]
    # print(set(val))
    try:
        # 执行sql语句
        cursor.executemany(sql, set(val))
        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    print("---- 开始创建钱包 ----")
    # 创建 1000 个随机钱包
    wallets = createNewETHWallet()

    # 保存至 csv 文件
    saveETHWallet(wallets)
    # updateETHWallet(wallets)

    print("---- 完成 ----")
