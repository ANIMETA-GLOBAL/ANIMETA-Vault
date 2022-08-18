import pymysql
import config


class VaultDB(object):

    def __init__(self):

        self.con = pymysql.connect(host=config.mysql_host, user=config.mysql_user, password=config.mysql_pwd,
                                   db=config.mysql_db)

    def get_deposit_wallet_dict(self):

        try:
            with self.con.cursor() as cursor:
                sql = f"select id,wallet_address,user_id from {config.wallet_table} "
                cursor.execute(sql)
                result = cursor.fetchall()
                wallet_dict = {}
                a = [wallet_dict.update({n[1]: {
                    "user_id": n[2],
                    "wallet_id": n[0]
                }}) for n in result]
                return wallet_dict

        except Exception as E:
            print(E)

    def get_deposit_wallet_dict_tron(self):

        try:
            with self.con.cursor() as cursor:
                sql = f"select id,wallet_address,user_id from {config.wallet_table_tron} "
                cursor.execute(sql)
                result = cursor.fetchall()
                wallet_dict = {}
                a = [wallet_dict.update({n[1]: {
                    "user_id": n[2],
                    "wallet_id": n[0]
                }}) for n in result]
                return wallet_dict

        except Exception as E:
            print(E)

    def upload_deposit_history(self, data):
        try:
            with self.con.cursor() as cursor:
                # val = (
                #     (data["user_id"], data["wallet_id"], data["source_address"], data["deposit_address"],
                #      data["network"], data["hash"], data["amount"], data["token"]))
                sql = f"INSERT INTO {config.deposit_table}(user_id,wallet_id,source_wallet_address,deposit_wallet_address,network,hash,amount,token) " \
                      f"VALUES ({data['user_id']},{data['wallet_id']},'{data['source_address']}','{data['deposit_address']}','{data['network']}','{data['hash']}',{data['amount']},'{data['token']}')"
                print(sql)
                cursor.execute(sql)
                self.con.commit()
                return {"result": True}

        except Exception as E:
            self.con.rollback()
            print(E)
            return {"result": False, "ERROR": str(E)}


if __name__ == '__main__':
    T = VaultDB()
    dict = T.get_deposit_wallet_dict_tron()

    if "TVPH3zumSz3MRni27d7wXSrc8XFpmfQgKw" in dict:
        print("True", dict["TVPH3zumSz3MRni27d7wXSrc8XFpmfQgKw"])
